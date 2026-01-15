# !/bin/bash

# 1. 데이터셋과 binning method 리스트
# DATASETS=("breast_cancer" "iris" "spam" "steel")

DATASETS=("default_of_credit_card" "processed_bank_marketing6")
METHODS=("sturges")
# DEPTHS="3,5"
# MAX_BINS="6,10"
# N_ESTIMATORS="15"
# TODO
DEPTHS="4"
MAX_BINS="8"
N_ESTIMATORS="20"

# 3. 각 데이터셋 × 방법에 대해 반복 실행
for DATASET in "${DATASETS[@]}"; do
  for METHOD in "${METHODS[@]}"; do
    COMBINED="${DATASET}/${METHOD}"
    echo "🚀 실행 중: ${COMBINED}"

    BIN_PATH="./cpp_results/${COMBINED}"
    python3 ../python/make_tree.py \
      --dataset=$COMBINED \
      --max_bins=$MAX_BINS \
      --depths=$DEPTHS \
      --n_estimators=$N_ESTIMATORS \
      --bin_path=$BIN_PATH

    echo "✅ 완료: ${COMBINED}"
    echo "------------------------------------------"
  done
done
