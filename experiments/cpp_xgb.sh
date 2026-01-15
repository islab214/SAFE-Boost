#!/bin/bash

# 1. 실행할 데이터셋 및 binning method 리스트
DATASETS=("breast-cancer" "iris" "spam" "steel" "bank_marketing" "default_of_credit_card" )
# DATASETS=("bank_marketing")
# METHODS=("sturges" "scott" "doana" "fd" )
METHODS=("sturges")
# DEPTHS="3,4,5,6,7,8,9,10"
MAX_BINS="4,8,16"
DEPTHS="3"
N_ESTIMATORS=1
OUTPUT_DIR="./cpp_results"

# 2. 실행 파일 경로
EXECUTABLE="../cpp_test/build/xgboost_cpp"

if [ ! -f "${EXECUTABLE}" ]; then
  echo "❌ 실행 파일을 찾을 수 없습니다: ${EXECUTABLE}"
  echo "⚠️ 먼저 build 디렉토리에서 cmake && make를 통해 빌드해주세요."
  exit 1
fi

# 3. 데이터셋 × 방법 조합으로 실행
for DATASET in "${DATASETS[@]}"; do
  for METHOD in "${METHODS[@]}"; do
    COMBINED="${DATASET}/${METHOD}"
    # COMBINED="${DATASET}"
    echo "========================================"
    echo "🚀 실행 중: ${COMBINED}"
    
    ${EXECUTABLE} \
      --dataset=${COMBINED} \
      --max_bins=${MAX_BINS} \
      --depths=${DEPTHS} \
      --n_estimators=${N_ESTIMATORS} \
      --output=${OUTPUT_DIR}

    echo "✅ 완료: ${COMBINED}"
    echo "----------------------------------------"
  done
done
