# !/bin/bash

# 1. 데이터셋과 binning method 리스트
# DATASETS=("steel")
#bank_marketing
#breast-cancer
DATASETS=( "breast-cancer"  "spam" "iris")
# DATASETS=("default_of_credit_card")
METHODS=("sturges")
# DATASETS=("bank_marketing" "breast-cancer" "default_of_credit_card" "spam" "steel" "iris")
# DATASETS=("default_of_credit_card")
# METHODS=("sturges")
# METHODS=("sturges" "scott" "doana" "fd" )
DEPTHS="5"
MAX_BINS="8"
# DEPTHS="3"
N_ESTIMATORS="7,9,11,13"

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




# # 1. 데이터셋과 binning method 리스트
# DATASETS=("processed_bank_marketing6")
# METHODS=("sturges")

# # 2. 디폴트 값
# DEFAULT_DEPTH=4
# DEFAULT_MAX_BINS=8
# DEFAULT_N_ESTIMATORS=15

# # 3. 변경할 값들 (쉼표로 구분)
# IFS=',' read -r -a DEPTHS <<< "2,4"
# IFS=',' read -r -a MAX_BINS <<< "4,8"
# IFS=',' read -r -a N_ESTIMATORS <<< "1,15"

# for DATASET in "${DATASETS[@]}"; do
#   for METHOD in "${METHODS[@]}"; do
#     COMBINED="${DATASET}/${METHOD}"
#     BIN_PATH="./cpp_results/${COMBINED}"
#     echo "=========================================="
#     echo "🚀 실행 중: ${COMBINED}"

#     # 3-1. depth 변동 (리스트 길이 >1일 때만)
#     if [ "${#DEPTHS[@]}" -gt 1 ]; then
#       echo "  → depths 변동: ${DEPTHS[*]}"
#       for depth in "${DEPTHS[@]}"; do
#         python3 ../python/make_tree.py \
#           --dataset="$COMBINED" \
#           --max_bins="$DEFAULT_MAX_BINS" \
#           --depths="$depth" \
#           --n_estimators="$DEFAULT_N_ESTIMATORS" \
#           --bin_path="$BIN_PATH"
#       done
#     fi

#     # 3-2. max_bins 변동
#     if [ "${#MAX_BINS[@]}" -gt 1 ]; then
#       echo "  → max_bins 변동: ${MAX_BINS[*]}"
#       for maxb in "${MAX_BINS[@]}"; do
#         python3 ../python/make_tree.py \
#           --dataset="$COMBINED" \
#           --max_bins="$maxb" \
#           --depths="$DEFAULT_DEPTH" \
#           --n_estimators="$DEFAULT_N_ESTIMATORS" \
#           --bin_path="$BIN_PATH"
#       done
#     fi

#     # 3-3. n_estimators 변동
#     if [ "${#N_ESTIMATORS[@]}" -gt 1 ]; then
#       echo "  → n_estimators 변동: ${N_ESTIMATORS[*]}"
#       for nest in "${N_ESTIMATORS[@]}"; do
#         python3 ../python/make_tree.py \
#           --dataset="$COMBINED" \
#           --max_bins="$DEFAULT_MAX_BINS" \
#           --depths="$DEFAULT_DEPTH" \
#           --n_estimators="$nest" \
#           --bin_path="$BIN_PATH"
#       done
#     fi

#     # 만약 모두 리스트 길이가 1이라면(=모든 파라미터 디폴트만 있다면) 한 번은 실행
#     if [ "${#DEPTHS[@]}" -eq 1 ] && [ "${#MAX_BINS[@]}" -eq 1 ] && [ "${#N_ESTIMATORS[@]}" -eq 1 ]; then
#       python3 ../python/make_tree.py \
#         --dataset="$COMBINED" \
#         --max_bins="${MAX_BINS[0]}" \
#         --depths="${DEPTHS[0]}" \
#         --n_estimators="${N_ESTIMATORS[0]}" \
#         --bin_path="$BIN_PATH"
#     fi

#     echo "✅ 완료: ${COMBINED}"
#     echo
#   done
# done