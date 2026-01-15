#!/usr/bin/env bash

# 실험 반복 횟수
ITERATIONS=1

# 실험할 데이터셋 리스트
DATASETS=("breast-cancer")
# DATASETS=("bank_marketing")
METHODS=("plain")

# 공통 파라미터
DATA_BASE_PATH="../data"
MAX_BINS="8"
DEPTHS="3"
N_ESTIMATORS=1
MODE="one"

# 실행할 파이썬 스크립트 경로
SCRIPT="../he/inf_plain_tree.py"

for DATASET in "${DATASETS[@]}"; do
  echo "🚀 시작: ${DATASET}"

  for METHOD in "${METHODS[@]}"; do
    DATA_METHOD="${DATASET}/${METHOD}"

    python3 "${SCRIPT}" \
      --data_base_path "${DATA_BASE_PATH}" \
      --iterations "${ITERATIONS}" \
      --dataset "${DATA_METHOD}" \
      --max_bins "${MAX_BINS}" \
      --depths "${DEPTHS}" \
      --n_estimators "${N_ESTIMATORS}" \
      --mode "${MODE}"
  #### 1-core #####
    # taskset -c 30 python3 "${SCRIPT}" \
    #   --data_base_path "${DATA_BASE_PATH}" \
    #   --iterations "${ITERATIONS}" \
    #   --dataset "${DATA_METHOD}" \
    #   --max_bins "${MAX_BINS}" \
    #   --depths "${DEPTHS}" \
    #   --n_estimators "${N_ESTIMATORS}" \
    #   --mode "${MODE}"

    echo "✅ 완료: ${DATASET}/${METHOD}"
    echo "----------------------------------------"



  done
done
