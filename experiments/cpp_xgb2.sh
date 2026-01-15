#!/bin/bash

# 1. 실행할 데이터셋 및 binning method 리스트
DATASETS=("secureXGB_syn_n50m50")
DATASETS2=("secureXGB_syn_n30m50" "secureXGB_syn_n70m50" "secureXGB_syn_n50m30" "secureXGB_syn_n50m70")
METHODS=("sturges")

# 2. 기본 파라미터 설정
DEFAULT_MAX_BINS=6
DEFAULT_DEPTH=3
DEFAULT_N_ESTIMATORS=1

# 3. 실행 파일 경로
EXECUTABLE="../cpp_test/build/xgboost_cpp"
OUTPUT_DIR="./cpp_results"

if [ ! -f "${EXECUTABLE}" ]; then
  echo "❌ 실행 파일을 찾을 수 없습니다: ${EXECUTABLE}"
  echo "⚠️ 먼저 build 디렉토리에서 cmake && make를 통해 빌드해주세요."
  exit 1
fi

# --------------------------------------------------
# # 4-1. Depth만 변경 (2,4,6) → MaxBins=8, N_Est=15 고정
# DEPTH_LIST=(2)
# for DATASET in "${DATASETS[@]}"; do
#   for METHOD in "${METHODS[@]}"; do
#     for DEPTH in "${DEPTH_LIST[@]}"; do
#       COMB="${DATASET}/${METHOD}"
#       echo "🚀 ${COMB} with depth=${DEPTH}, max_bins=${DEFAULT_MAX_BINS}, n_est=${DEFAULT_N_ESTIMATORS}"
#       "${EXECUTABLE}" \
#         --dataset="${COMB}" \
#         --depths="${DEPTH}" \
#         --max_bins="${DEFAULT_MAX_BINS}" \
#         --n_estimators="${DEFAULT_N_ESTIMATORS}" \
#         --output=${OUTPUT_DIR}
#       echo "✅ Done: depth=${DEPTH}"
#       echo "----------------------------------------"
#     done
#   done
# done

# --------------------------------------------------
# 4-2. MaxBins만 변경 (4,8,12) → Depth=4, N_Est=15 고정
MAX_BINS_LIST=(6 10)
for DATASET in "${DATASETS[@]}"; do
  for METHOD in "${METHODS[@]}"; do
    for MAXB in "${MAX_BINS_LIST[@]}"; do
      COMB="${DATASET}/${METHOD}"
      echo "🚀 ${COMB} with depth=${DEFAULT_DEPTH}, max_bins=${MAXB}, n_est=${DEFAULT_N_ESTIMATORS}"
      "${EXECUTABLE}" \
        --dataset="${COMB}" \
        --depths="${DEFAULT_DEPTH}" \
        --max_bins="${MAXB}" \
        --n_estimators="${DEFAULT_N_ESTIMATORS}" \
        --output=${OUTPUT_DIR}
      echo "✅ Done: max_bins=${MAXB}"
      echo "----------------------------------------"
    done
  done
done

MAX_BINS_LIST=(4 6 8 10 12)
for DATASET in "${DATASETS2[@]}"; do
  for METHOD in "${METHODS[@]}"; do
    for MAXB in "${MAX_BINS_LIST[@]}"; do
      COMB="${DATASET}/${METHOD}"
      echo "🚀 ${COMB} with depth=${DEFAULT_DEPTH}, max_bins=${MAXB}, n_est=${DEFAULT_N_ESTIMATORS}"
      "${EXECUTABLE}" \
        --dataset="${COMB}" \
        --depths="${DEFAULT_DEPTH}" \
        --max_bins="${MAXB}" \
        --n_estimators="${DEFAULT_N_ESTIMATORS}" \
        --output=${OUTPUT_DIR}
      echo "✅ Done: max_bins=${MAXB}"
      echo "----------------------------------------"
    done
  done
done

# --------------------------------------------------
# # 4-3. N_Estimators만 변경 (1,5,10,15) → Depth=4, MaxBins=8 고정
# N_EST_LIST=(1)
# for DATASET in "${DATASETS[@]}"; do
#   for METHOD in "${METHODS[@]}"; do
#     for NEST in "${N_EST_LIST[@]}"; do
#       COMB="${DATASET}/${METHOD}"
#       echo "🚀 ${COMB} with depth=${DEFAULT_DEPTH}, max_bins=${DEFAULT_MAX_BINS}, n_est=${NEST}"
#       "${EXECUTABLE}" \
#         --dataset="${COMB}" \
#         --depths="${DEFAULT_DEPTH}" \
#         --max_bins="${DEFAULT_MAX_BINS}" \
#         --n_estimators="${NEST}" \
#         --output=${OUTPUT_DIR}
#       echo "✅ Done: n_estimators=${NEST}"
#       echo "----------------------------------------"
#     done
#   done
# done
