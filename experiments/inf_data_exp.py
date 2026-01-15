import subprocess

# 실험 반복 횟수
ITERATIONS = 10

# 실험할 데이터셋과 메서드
DATASETS = ["iris", "breast-cancer", "spam"]
# DATASETS = ["bank_marketing"]
METHODS = ["sturges"]
MAX_BINS_LIST = ["8"]  # ✅ 여러 max_bin 값 실험 가능

# 공통 파라미터
DATA_BASE_PATH = "../data"
DEPTHS = "5"
N_ESTIMATORS = "7,9,11,13"
# N_ESTIMATORS = "3"
MODE = "one"
ENCRYPTED = "true"
# 실행할 파이썬 스크립트 경로
SCRIPT = "../he/inf_plain_tree.py"
# 사용할 CPU 코어 번호
CPU_CORE = "28"

for dataset in DATASETS:
    print(f"🚀 시작: {dataset}")

    for method in METHODS:
        for max_bin in MAX_BINS_LIST:
            data_method = f"{dataset}/{method}"

            for iteration in range(ITERATIONS):
                print(f"▶ 실행 중: {data_method}, max_bins={max_bin}, iteration={iteration + 1}/{ITERATIONS}")

                cmd = [
                    # "taskset",
                    # "-c",
                    # CPU_CORE,
                    "python3",
                    SCRIPT,
                    "--data_base_path",
                    DATA_BASE_PATH,
                    "--iterations",
                    "1",  # ❗ 여기서 고정
                    "--dataset",
                    data_method,
                    "--max_bins",
                    max_bin,
                    "--depths",
                    DEPTHS,
                    "--n_estimators",
                    N_ESTIMATORS,
                    "--mode",
                    MODE,
                    "--enc",
                    ENCRYPTED,
                ]

                subprocess.run(cmd, check=True)

            print(f"✅ 완료: {data_method}, max_bins={max_bin}")
            print("----------------------------------------")
