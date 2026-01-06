from pathlib import Path
import random
from extract_logs import stream_lines
import pandas as pd
import config.config as conf
from sklearn.model_selection import StratifiedShuffleSplit
import re
from collections import Counter,defaultdict

max_lines_per_label_train = conf.MAX_LINES_PER_LABEL_TRAIN
max_lines_per_label_test = conf.MAX_LINES_PER_LABEL_TEST

max_lines_per_app_train = conf.MAX_LINES_PER_APP_TRAIN
max_lines_per_app_test = conf.MAX_LINES_PER_APP_TEST

max_info_ratio = conf.MAX_INFO_RATIO

error_pattern = re.compile(conf.ERROR_PATTERN,re.I)
warn_pattern = re.compile(conf.WARN_PATTERN,re.I)

processed_data_path = Path(conf.PROCESSED_DATA_PATH)

def line_priority(line:str)->float:
    if error_pattern.search(line):
        return 3.0
    if(error_pattern).search(line):
        return 1.5
    return 1.0

def collect_lines_for_split(apps_subset, app_to_label, per_label_cap, per_app_cap, max_info_ratio):
    per_label_counts = Counter()
    texts,labels = [],[]
    app_to_indices = defaultdict(list)

    apps_list = list(apps_subset)
    random.shuffle(apps_list)

    inv_df = pd.read_csv(processed_data_path/"inventory.csv",index_col="application")


    for app in apps_list:
        label = app_to_label(app)
        log_files = inv_df[inv_df["application"]==app]

        log_files_paths = [Path(file["file_path"]) for file in log_files.iterrows()]

        scored = []

        for lf_path in log_files_paths:
            lines = stream_lines(lf_path)
            for line in lines:
                scored.append((line_priority(line),line))

        if not scored:continue

        scored.sort(key=lambda x:x[0],reverse=True)

        chosen, info_count = [],0
        info_limit = int(max_info_ratio*per_app_cap) if per_app_cap>0 else 0
        for score,line in scored:
            if(len(chosen)>per_app_cap):
                break
            is_info = (score==1.0)
            if is_info and info_count>=info_limit:
                continue
            chosen.append(line)
            if is_info:
                info_count+=1

        for line in chosen:
            if(per_label_counts[app]> per_label_cap):
                break
            idx = len(texts)
            texts.append(line)
            labels.append(label)
            app_to_indices[app].append(idx)
            per_label_counts[app]+=1

    return texts,labels,app_to_indices

        