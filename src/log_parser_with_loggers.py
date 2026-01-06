from src.extract_logs import stream_lines
from pathlib import Path
import re 
from datetime import datetime
from config.config import LOG_LINE_PATTERN,PROCESSED_DATA_PATH
import pandas as pd
from collections import defaultdict

log_regex =re.compile(LOG_LINE_PATTERN) 

def parse_log_line(line):
    match = log_regex.match(line)
    if not match:
        return None
    
    data = match.groupdict()
    data["timestamp"] = datetime.strptime(
        data["timestamp"], "%Y-%m-%d %H:%M:%S,%f"
    )
    return data

def process_application_id(path:Path)->dict:
    lines = stream_lines(path)
    log_count = 0
    levels = {}
    loggers = {}
    min_ts , max_ts = None,None
    for ln in lines:
        data = parse_log_line(ln)
        if(data):
            log_count+=1
            levels[data["level"]] = levels.get(data["level"],0)+1
            if(data["logger"].startswith("org.apache.hadoop")):
                type_of_logger = data["logger"].split(".")[3]
                loggers[type_of_logger] = loggers.get(type_of_logger,0)+1
            else:
                loggers["others"]=loggers.get("others",0)+1

            if(min_ts is None or data["timestamp"]<min_ts):min_ts=data["timestamp"]
            if(max_ts is None or data["timestamp"]>max_ts):max_ts=data["timestamp"]


    duration = (max_ts-min_ts).total_seconds() if min_ts and max_ts else 0
    # print(parsed_logs[-1])
    result = {
        "num_info": levels.get("INFO", 0),
        "num_warn": levels.get("WARN", 0),
        "num_error": levels.get("ERROR", 0),
        "num_fatal": levels.get("FATAL", 0),
        "log_count": log_count,
        "run_duration_seconds": duration
    }
    result = result | loggers
    return result   

def process_database():
    inv_df = pd.read_csv(Path(PROCESSED_DATA_PATH)/"inventory.csv")
    per_app=defaultdict(dict)
    for idx,row in inv_df.iterrows():

        file_path = row["file_path"]
        app = row["application"]
        data = process_application_id(Path(file_path))
        for key,val in data.items():
            per_app[app][key]=per_app[app].get(key,0)+float(val)
        per_app[app]["label"]=row["label"]
    
    
    per_app_df = pd.DataFrame.from_dict(per_app,orient="index")
    per_app_df = per_app_df.reset_index().rename(columns={"index":"application"})
    per_app_df.to_csv(Path(PROCESSED_DATA_PATH)/"logs_parsed.csv",index=False)
    


if __name__ == "__main__":
    process_database()