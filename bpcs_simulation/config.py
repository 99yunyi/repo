"""Configuration for BPCS simulation."""
# 部署場景
NUM_NODES = 100          # 區塊鏈節點數
DAILY_IOC = 5000         # 每日 IoC 記錄數
BATCH_SIZE = 100         # 每批次聚合的記錄數
DAILY_BATCHES = DAILY_IOC // BATCH_SIZE  # = 50
DAYS_PER_MONTH = 30
BENCH_ITERATIONS = 200   # 每個操作測量 200 次取平均

# 四種 Scheme 定義
SCHEMES = {
    "ECDSA (no batch)": {
        "algorithm": "ecdsa",
        "batch": False,
        "daily_uploads": DAILY_IOC,  # 5000
    },
    "ECDSA+Batch": {
        "algorithm": "ecdsa",
        "batch": True,
        "daily_uploads": DAILY_BATCHES,  # 50
    },
    "SLH-DSA+Batch": {
        "algorithm": "slh-dsa-sha2-128s",
        "batch": True,
        "daily_uploads": DAILY_BATCHES,
    },
    "ML-DSA-44+Batch": {
        "algorithm": "ml-dsa-44",
        "batch": True,
        "daily_uploads": DAILY_BATCHES,
    },
}

# On-chain payload (fixed, independent of algorithm):
# h(bf):32 + t_start:8 + t_end:8 + file_name:64 = 112 bytes
ONCHAIN_PAYLOAD = 112  # bytes

# Off-chain: bf contains each report's signed payload, approximate average STIX 2.1 IoC size
AVG_REPORT_SIZE = 3072  # bytes

# Results directory
RESULTS_DIR = "bpcs_simulation/results"

# 金鑰和簽章的固定大小（bytes），根據 NIST 標準
KEY_SIZES = {
    "ecdsa": {"pk": 33, "sk": 32, "sig": 71},           # secp256k1 compressed
    "slh-dsa-sha2-128s": {"pk": 32, "sk": 64, "sig": 7856},  # FIPS 205
    "ml-dsa-44": {"pk": 1312, "sk": 2560, "sig": 2420},      # FIPS 204
}