import os, shutil
import subprocess
import time
import argparse

# =========================================
# Helper to clear OS caches
# =========================================
def cleanup_caches():
    subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"], check=False)
    print("▶ 페이지 캐시 비우기 완료")

# =========================================
# Parse CLI arguments
# =========================================
parser = argparse.ArgumentParser(
    description="Run binning + HE training/inf experiments with manual parameter combos"
)
parser.add_argument(
    "--combos-file", type=str, default=None,
    help="Path to a JSON file listing experiment combos (overrides built-in param grid)"
)
parser.add_argument(
    "--learning-rate", type=float, default=None,
    help="Default learning rate if not specified per combo"
)
args = parser.parse_args()

# =========================================
# 고정된 반복 횟수 설정 (Syn 데이터셋 전용)
# =========================================
SYN_REPETITIONS = 3  # secureXGB_syn_* 계열을 몇 번 반복할지

# =========================================
# Manual combo list (override via --combos-file)
# Each combo is a dict with keys:
#   dataset, method, max_bin, depth, n_estimators, learning_rate
# =========================================
manual_combos = [
    ## NDSS 추가 실험 (AUC)
    {"dataset":"processed_bank_marketing6","method":"sturges", "max_bin":8,  "depth":3, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"processed_bank_marketing6","method":"sturges", "max_bin":8,  "depth":5, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"processed_bank_marketing6","method":"sturges", "max_bin":6,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"processed_bank_marketing6","method":"sturges", "max_bin":10,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    
    {"dataset":"default_of_credit_card","method":"sturges", "max_bin":8,  "depth":3, "n_estimators":15,  "learning_rate":0.5},
    {"dataset":"default_of_credit_card","method":"sturges", "max_bin":8,  "depth":5, "n_estimators":15,  "learning_rate":0.5},
    {"dataset":"default_of_credit_card","method":"sturges", "max_bin":6,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"default_of_credit_card","method":"sturges", "max_bin":10,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    
    {"dataset":"processed_bank_marketing6","method":"sturges", "max_bin":8,  "depth":4, "n_estimators":20, "learning_rate":0.5},
    {"dataset":"default_of_credit_card","method":"sturges", "max_bin":8,  "depth":4, "n_estimators":20, "learning_rate":0.5},
    # {"dataset":"processed_bank_marketing6","method":"sturges", "max_bin":32,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    # {"dataset":"default_of_credit_card","method":"sturges", "max_bin":32,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    ##
    
    #### synthetic datasets
    ## (a)
    {"dataset":"secureXGB_syn_n30m50", "method":"sturges", "max_bin":8,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"secureXGB_syn_n70m50", "method":"sturges", "max_bin":8,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"secureXGB_syn_n50m30","method":"sturges", "max_bin":8,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"secureXGB_syn_n50m70","method":"sturges", "max_bin":8,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    
    {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":6,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":10,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    
    {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":8,  "depth":3, "n_estimators":15, "learning_rate":0.5},
    {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":8,  "depth":5, "n_estimators":15, "learning_rate":0.5},
    # ## (b)
    # {"dataset":"secureXGB_syn_n50m10","method":"sturges", "max_bin":8,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    # {"dataset":"secureXGB_syn_n50m100","method":"sturges", "max_bin":8, "depth":4, "n_estimators":15, "learning_rate":0.5},
    # ## (c)
    # {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":4,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    # {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":12, "depth":4, "n_estimators":15, "learning_rate":0.5},
    # {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":6,  "depth":4, "n_estimators":15, "learning_rate":0.5},
    # {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":10, "depth":4, "n_estimators":15, "learning_rate":0.5},
    # ## (d) ## 추가
    # {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":8,  "depth":3, "n_estimators":15, "learning_rate":0.5},
    # {"dataset":"secureXGB_syn_n50m50","method":"sturges", "max_bin":8,  "depth":5, "n_estimators":15, "learning_rate":0.5},
    ### hqsfl synthetic datasets ## 추가 (CUDA OOM)
    # {"dataset":"hqsfl_syn3_40F","method":"sturges", "max_bin":30,  "depth":3, "n_estimators":10, "learning_rate":0.1},
    # {"dataset":"hqsfl_syn3_60F","method":"sturges", "max_bin":30,  "depth":3, "n_estimators":10, "learning_rate":0.1},
    # {"dataset":"hqsfl_syn3_80F","method":"sturges", "max_bin":30,  "depth":3, "n_estimators":10, "learning_rate":0.1},
    # {"dataset":"hqsfl_syn3_100F","method":"sturges", "max_bin":30,  "depth":3, "n_estimators":10, "learning_rate":0.1},
]

# combos 가 비어 있으면 종료
if not manual_combos:
    print("🛑 No experiment combos found. Please fill 'manual_combos' or provide --combos-file.")
    exit(1)

# Paths and constants
data_base_path = "../data"
OUTPUT_BASE    = "./bin_results"
EXECUTABLE     = "../cpp_test/build/xgboost_cpp"
LOG_DIR        = "./logs"

os.makedirs(LOG_DIR, exist_ok=True)

# =========================================
# Main Loop
#   - secureXGB_syn_* 계열만 SYN_REPETITIONS 만큼 반복
#   - bank_marketing / default_of_credit_card 계열은 5-fold만 실행
# =========================================
for combo in manual_combos:
    dataset      = combo["dataset"]
    method       = combo.get("method", "sturges")
    max_bin      = combo["max_bin"]
    depth        = combo["depth"]
    n_estimators = combo["n_estimators"]
    lr           = combo.get("learning_rate", args.learning_rate)
    if lr is None:
        print(f"🛑 Combo {combo} has no learning_rate and no default provided.")
        continue

    # 공통 디렉터리
    dataset_log_dir = os.path.join(LOG_DIR, dataset)
    os.makedirs(dataset_log_dir, exist_ok=True)
    base_name = f"{dataset}-{method}-b{max_bin}-d{depth}-t{n_estimators}-lr{lr}"

    # C++ binning 결과가 있을 경로
    output_dir = os.path.join(OUTPUT_BASE, dataset, method)
    # bin_path   = os.path.join(output_dir, f"bin{max_bin}", "cutpoints.json")
    bin_path = os.path.join('./cpp_results',dataset,method, f"bin{max_bin}", "cutpoints.json") ## 수정

    # ───────────────────────────────────────────────────────────────────────
    # 1) “bank_marketing” 또는 “default_of_credit_card” 계열: 5-fold 교차검증만 실행
    # ───────────────────────────────────────────────────────────────────────
    if dataset in ("bank_marketing", "default_of_credit_card", "processed_bank_marketing6"):
        # fold은 1~5 까지
        for fold in range(1, 2):
            # 임시 디렉토리 (각 fold에 맞춰 train.csv/test.csv 로 연결할 공간)
            temp_dir = f"./temp_run/{dataset}_fold{fold}/{method}"
            os.makedirs(temp_dir, exist_ok=True)

            # 실제 원본이 저장된 경로: "../data/{dataset}/{method}/"
            src_plain_dir = os.path.join(data_base_path, dataset, method)
            src_train     = os.path.join(src_plain_dir, f"train{fold}.csv")
            src_test      = os.path.join(src_plain_dir, f"test{fold}.csv")

            # ── 임시 디렉토리에 train.csv / test.csv 로 “복사” ──────────
            tgt_train = os.path.join(temp_dir, "train.csv")
            tgt_test  = os.path.join(temp_dir, "test.csv")
            # 이미 존재하면 삭제
            if os.path.exists(tgt_train):
                os.remove(tgt_train)
            if os.path.exists(tgt_test):
                os.remove(tgt_test)
            # 복사
            shutil.copy(src_train, tgt_train)
            shutil.copy(src_test,  tgt_test)

            # ── run_only_train.py 에 넘길 인자 ─────────────────────────
            combo_data_base = f"./temp_run/{dataset}_fold{fold}"
            combo_dataset   = ""  # (run_only_train.py 내부에서 dataset=method/read_path 를 빈 문자열로 처리)

            # ── 로그 파일명 ──────────────────────────────────────────────
            dataset_log_dir = os.path.join(LOG_DIR, dataset)
            os.makedirs(dataset_log_dir, exist_ok=True)
            base_name = f"{dataset}-{method}-b{max_bin}-d{depth}-t{n_estimators}-lr{lr}"
            log_fname    = f"{base_name}-fold{fold}.log"
            log_filepath = os.path.join(dataset_log_dir, log_fname)

            with open(log_filepath, "w") as lf:
                def log(msg="", **kwargs):
                    print(msg, **kwargs)
                    print(msg, file=lf, **kwargs)

                log("========================================")
                log(f"🚀 [{dataset}] Fold={fold} | bin={max_bin} | depth={depth} | trees={n_estimators} | lr={lr}")

                # 2-1) C++ binning
                print('bin_path:', bin_path)
                if not os.path.exists(bin_path):
                    log("⏳ cutpoints.json 없음. C++로 binning 실행...")
                    cmd_cpp = [
                        EXECUTABLE,
                        f"--dataset={dataset}/{method}",
                        f"--max_bins={max_bin}",
                        f"--depths={depth}",
                        f"--n_estimators={n_estimators}",
                        f"--output={OUTPUT_BASE}",
                    ]
                    t0 = time.perf_counter()
                    try:
                        subprocess.run(cmd_cpp, check=True)
                    except subprocess.CalledProcessError as e:
                        log(f"❌ C++ binning 실패 (code {e.returncode})")
                        cleanup_caches()
                        # 복사된 train/test 파일 삭제
                        os.remove(tgt_train)
                        os.remove(tgt_test)
                        continue
                    log(f"✅ C++ binning 완료 ({time.perf_counter() - t0:.2f}s)")
                else:
                    log("✅ cutpoints.json 존재. C++ binning 단계 건너뜀")

                cleanup_caches()

                # 2-2) Python HE 학습/추론
                log("⏳ Python HE 학습/추론 시작...")
                cmd_py = [
                    "python3", "../he/run_only_train.py",
                    # data_base_path 를 “./temp_run/{dataset}_fold{fold}” 로 지정
                    "--data_base_path", combo_data_base,
                    "--dataset",        method,
                    "--method",         "",  
                    "--max_bins",       str(max_bin),
                    "--depths",         str(depth),
                    "--n_estimators",   str(n_estimators),
                    "--learning_rate",  str(lr),
                    "--bin_path",       bin_path,
                    "--save_path",      "./result",
                    "--log_path",       output_dir,
                ]
                t1 = time.perf_counter()
                try:
                    subprocess.run(cmd_py, stdout=lf, stderr=lf, check=True)
                except subprocess.CalledProcessError as e:
                    log(f"❌ 학습/추론 실패 (code {e.returncode})")
                    cleanup_caches()
                    # 복사된 train/test 파일 삭제
                    os.remove(tgt_train)
                    os.remove(tgt_test)
                    continue
                log(f"✅ 학습/추론 완료 ({time.perf_counter() - t1:.2f}s)")
                log("----------------------------------------\n")

            print(f"⚡ 완료: {base_name} | Fold={fold}")
            print(f"▶ 로그: {log_filepath}\n")

            # ── 폴드별 복사된 train/test 파일 삭제 ───────────────────
            os.remove(tgt_train)
            os.remove(tgt_test)

    # ────────────────────────────────────────────────
    # 2) synthetic dataset: SYN_REPETITIONS 만큼 반복
    # ────────────────────────────────────────────────
    else:
        for rep in range(1, SYN_REPETITIONS + 1):
            log_fname    = f"{base_name}-run{rep}.log"
            log_filepath = os.path.join(dataset_log_dir, log_fname)

            with open(log_filepath, "w") as lf:
                def log(msg="", **kwargs):
                    print(msg, **kwargs)
                    print(msg, file=lf, **kwargs)

                log("========================================")
                log(f"🚀 [{dataset}] | bin={max_bin} | depth={depth} | trees={n_estimators} | lr={lr} | run={rep}")

                # 1-1) C++ binning
                if not os.path.exists(bin_path):
                    log("⏳ cutpoints.json 없음. C++로 binning 실행...")
                    cmd_cpp = [
                        EXECUTABLE,
                        f"--dataset={dataset}/{method}",
                        f"--max_bins={max_bin}",
                        f"--depths={depth}",
                        f"--n_estimators={n_estimators}",
                        f"--output={OUTPUT_BASE}",
                    ]
                    t0 = time.perf_counter()
                    try:
                        subprocess.run(cmd_cpp, check=True)
                    except subprocess.CalledProcessError as e:
                        log(f"❌ C++ binning 실패 (code {e.returncode})")
                        cleanup_caches()
                        continue
                    log(f"✅ C++ binning 완료 ({time.perf_counter() - t0:.2f}s)")
                else:
                    log("✅ cutpoints.json 존재. C++ binning 단계 건너뜀")

                cleanup_caches()

                # 1-2) Python HE 학습/추론
                log("⏳ Python HE 학습/추론 시작...")
                cmd_py = [
                    "python3", "../he/run_only_train.py",
                    "--data_base_path", data_base_path,
                    "--dataset",        dataset,
                    "--method",         method,
                    "--max_bins",       str(max_bin),
                    "--depths",         str(depth),
                    "--n_estimators",   str(n_estimators),
                    "--learning_rate",  str(lr),
                    "--bin_path",       bin_path,
                    "--save_path",      "./result",
                    "--log_path",       output_dir,
                ]
                t1 = time.perf_counter()
                try:
                    subprocess.run(cmd_py, stdout=lf, stderr=lf, check=True)
                except subprocess.CalledProcessError as e:
                    log(f"❌ 학습/추론 실패 (code {e.returncode})")
                    cleanup_caches()
                    continue

                log(f"✅ 학습/추론 완료 ({time.perf_counter() - t1:.2f}s)")
                log("----------------------------------------\n")

            print(f"⚡ 완료: {base_name} | run={rep}")
            print(f"▶ 로그: {log_filepath}\n")
print("===== 모든 실험 완료 =====")
