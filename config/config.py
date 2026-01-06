RAW_DATA_PATH = "data\\raw\Hadoop_log.zip"
PROCESSED_DATA_PATH = "data\processed"
EXTRACTED_DATA_PATH = "data\extracted\Hadoop_log"

LABEL_TEXT_PATH = "data\extracted\Hadoop_log\\abnormal_label.txt"

SAMPLES_PER_LABEL = 15
SAMPLES_PER_APP = 10

LOG_LINE_PATTERN = (
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2},\d+)\s+"
    r"(?P<level>INFO|WARN|ERROR|FATAL|DEBUG)\s+"
    r"\[(?P<thread>[^\]]+)\]\s+"
    r"(?P<logger>[\w\.]+):\s+"
    r"(?P<message>.*)"
)
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S,%f"
SEVERITY_LEVELS = ["INFO", "WARN", "ERROR", "FATAL", "DEBUG"]


# Balanced caps across labels; modest at first, scale up once stable
MAX_LINES_PER_LABEL_TRAIN = 30000
MAX_LINES_PER_LABEL_VAL   = 5000
MAX_LINES_PER_LABEL_TEST  = 5000

# Cap per application to avoid any single app dominating
MAX_LINES_PER_APP_TRAIN   = 4000
MAX_LINES_PER_APP_VAL     = 1500
MAX_LINES_PER_APP_TEST    = 1500


MAX_INFO_RATIO = 0.30  # at most 30% of sampled lines per app can be low-priority

ERROR_PATTERN = r"(ERROR|FATAL|EXCEPTION|fail(ed)?|refused|timeout|disk|full|network|connect|lost|down)"
WARN_PATTERN = r"(WARN|warning|retry|backoff|throttle)"

# Text vectorization (character-level)
SEQ_LEN = 512     
VOCAB = None       

# Model / training
EMBED_DIM = 64
DROPOUT = 0.35
BATCH_SIZE = 512
EPOCHS = 12
BASE_LR = 1e-3     # lower than before for stability

# Confidence floor for app-level aggregation 
CONF_FLOOR = 0.50