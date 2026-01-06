from config import config
from pathlib import Path
from collections import defaultdict
import pandas as pd
import json
import random

label_text_path = Path(config.LABEL_TEXT_PATH)
root_dir = Path(config.EXTRACTED_DATA_PATH)
processed_dir = Path(config.PROCESSED_DATA_PATH)
SAMPLES_PER_LABEL = config.SAMPLES_PER_LABEL
SAMPLES_PER_APP = config.SAMPLES_PER_APP

def parse_labels(label_file:Path) -> dict:
    app_label ={}
    label = None
    if not label_file.exists():
        raise FileNotFoundError(f"Given file path not found {label_file}")
    
    with label_file.open("r",encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue
            
            if(line.endswith(":")):
                label = line[:-1].strip()
            
            if(label and line.startswith("+")):
                app_id = line[1:].strip()
                app_label[app_id]=label
        
        return app_label

def count_lines(file_path : Path)-> int:
    count = 0
    with file_path.open("r",encoding="utf-8") as f:
        for _ in f:
            count+=1
        
    return count    

def stream_lines(file_path:Path, max_lines = None):
    n = 0
    with file_path.open("r",encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line:
                yield line
            n+=1
            if(max_lines is not None and n>=max_lines):
                break

def reservoir_sampling(iterable,k,seed=42):
    random.seed(seed)
    sample = []
    for i,item in enumerate(iterable,start=1):
        if(i<=k):
            sample.append(item)
        else:
            j = random.randint(1,i)
            if j<=k:
                sample[j-1] = item

    return sample

def main():
    app_to_label = parse_labels(label_text_path)
    apps = []
    file_rows = []
    apps_status = defaultdict(lambda:{"num_files": 0, "total_lines": 0, "label": "unknown"})

    if not root_dir.exists():
        raise FileNotFoundError(f"Root file not found at {root_dir}")
    
    for entry in sorted(root_dir.iterdir()):
        if(entry.is_dir() and entry.name.startswith("application_")):
            app_name = entry.name
            label = app_to_label.get(app_name)
            apps.append(app_name)

            log_files = sorted([p for p in entry.iterdir() if p.is_file() and p.name.endswith(".log")])

            for lf in log_files:
                size_bytes = lf.stat().st_size
                line_count = count_lines(lf)

                file_rows.append({
                    "application": app_name,
                    "label":label,
                    "file_path": str(lf),
                    "file_name": lf.name,
                    "size_bytes": size_bytes,
                    "line_count": line_count,
                })

                apps_status[app_name]["num_files"]+=1
                apps_status[app_name]["total_lines"]+=line_count
                apps_status[app_name]["label"] = label

    inv_df = pd.DataFrame(file_rows).sort_values(["application","file_name"])
    inv_df.to_csv(processed_dir/"inventory.csv",index=False)
    apps_status_df = pd.DataFrame(
        {"application":app,**vals}
        for app,vals in apps_status.items()
    )
    apps_status_df.to_csv(processed_dir/"app_status.csv",index=False)

    label_count_apps = apps_status_df["label"].value_counts().rename_axis("label").reset_index(name="num_apps")
    lines_per_label = apps_status_df.groupby("label")["total_lines"].sum().reset_index(name="total_lines")

    label_summary = pd.merge(label_count_apps,lines_per_label,on="label",how="outer").fillna(0)
    label_summary.to_csv(processed_dir/"label_counts.csv",index=False)

    # Then we would make a test file for the testing with reservoir sampling
    # with a)per-label-sample b)per-app-sample
    samples_path = processed_dir/"samples_log.jsonl"
    with samples_path.open("w",encoding="utf-8") as jout:
        # a) per_label_samples
        for label in sorted(label_summary["label"].unique()):
            per_file_sample = []
            for _,row in inv_df[inv_df["label"]==label].iterrows():
                lines = reservoir_sampling(stream_lines(Path(row["file_path"])),k=3)

            for ln in lines:
                per_file_sample.append({
                    "kind": "per_label",
                    "label": label,
                    "application": row["application"],
                    "file": row["file_name"],
                    "line": ln
                })
            
            selected = reservoir_sampling((x for x in per_file_sample), k=min(SAMPLES_PER_LABEL, max(1, len(per_file_sample))))
            for item in selected:
                jout.write(json.dumps(item,ensure_ascii=False)+"\n")
            

        # b) per_app_sample
        # print(apps_status_df)
        for app_name in apps_status_df["application"]:
            # print(app_name)
            # print()
            label = apps_status[app_name]["label"]
            per_app_sample = []
            rows = inv_df[inv_df["application"]==app_name]
            for _,row in rows.iterrows():
                lines = reservoir_sampling(stream_lines(Path(row["file_path"])),k=2)

                for ln in lines:
                    per_app_sample.append({
                        "kind": "per_app",
                        "application": app_name,
                        "label": label,
                        "file": row["file_name"],
                        "line": ln
                    })

            selected = reservoir_sampling((x for x in per_app_sample), k=min(SAMPLES_PER_APP, max(1, len(per_app_sample))))
            for item in selected:
                jout.write(json.dumps(item, ensure_ascii=False) + "\n")


if(__name__=="__main__"):
    main()