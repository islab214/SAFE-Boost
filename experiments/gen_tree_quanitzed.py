import json
import os
import random

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

CLASSIFICATION_VALUE_BITLENGTH = 8


class Leaf:
    def __init__(self, value, nodeid, depth):
        self.nodeid = nodeid
        self.depth = depth
        self.leaf = float(value)
        self.cover = 1.0  # 필요 시 조정

    def to_dict(self):
        return {
            "nodeid": self.nodeid,
            "depth": self.depth,
            "leaf": self.leaf,
            "cover": self.cover,
        }


class Internal:
    def __init__(self, feature, threshold, left, right, nodeid, depth):
        self.nodeid = nodeid
        self.depth = depth
        self.split = f"f{feature}"
        self.split_condition = float(threshold)
        self.split_bin_idx = 0  # 필요 시 바꾸세요
        self.gain = 1.0  # 필요 시 바꾸세요
        self.cover = 1.0  # 필요 시 바꾸세요
        self.children = [left, right]

    def to_dict(self):
        return {
            "nodeid": self.nodeid,
            "depth": self.depth,
            "split": self.split,
            "split_condition": self.split_condition,
            "split_bin_idx": self.split_bin_idx,
            "gain": self.gain,
            "cover": self.cover,
            "children": [c.to_dict() for c in self.children],
        }


def build_tree(tree):
    node_count = [0]
    return build_tree_rec(tree, 0, node_count), node_count[0]


def build_tree_rec(tree, node_id, node_count):
    left_child = tree.tree_.children_left[node_id]
    right_child = tree.tree_.children_right[node_id]
    is_split_node = left_child != right_child

    if is_split_node:
        left = build_tree_rec(tree, left_child, node_count)
        right = build_tree_rec(tree, right_child, node_count)
        node_count[0] += 1
        # Internal 생성 시에도 수정된 필드명이 적용됩니다
        return Internal(tree.tree_.threshold[node_id], tree.tree_.feature[node_id], left, right)
    else:
        return Leaf(tree.tree_.value[node_id].argmax())


def generate_balanced_tree_rec(max_depth, depth, bitlength, num_attributes, nodeid_counter):
    if depth < max_depth:
        left = generate_balanced_tree_rec(max_depth, depth + 1, bitlength, num_attributes, nodeid_counter)
        right = generate_balanced_tree_rec(max_depth, depth + 1, bitlength, num_attributes, nodeid_counter)
        nodeid = nodeid_counter[0]
        nodeid_counter[0] += 1
        threshold = random.randint(0, 2**bitlength - 1)
        feature = random.randint(0, num_attributes - 1)
        return Internal(feature, threshold, left, right, nodeid, depth)
    else:
        value = random.uniform(-1, 1)  # 또는 클래스 인덱스도 가능
        nodeid = nodeid_counter[0]
        nodeid_counter[0] += 1
        return Leaf(value, nodeid, depth)


def generate_tree(max_depth, bitlength, num_attributes, seed=None):
    if seed is not None:
        random.seed(seed)
    nodeid_counter = [0]
    tree = generate_balanced_tree_rec(
        max_depth, depth=0, bitlength=bitlength, num_attributes=num_attributes, nodeid_counter=nodeid_counter
    )
    return tree


def extract_splits(node, path="", splits=None):
    """
    XGBoost-style JSON에서 재귀적으로 분기 노드를 순회하며 분기 정보 추출
    """
    if splits is None:
        splits = []

    if "split" in node:  # split 노드
        splits.append(
            {
                "node_path": path if path else "-1",
                "depth": node.get("depth", 0),
                "feature": node.get("split"),
                "condition": node.get("split_condition"),
                "split_bin_idx": node.get("split_bin_idx", None),
            }
        )
        for i, child in enumerate(node.get("children", [])):
            extract_splits(child, path + str(i), splits)

    return splits


def save_split_conditions_grouped(tree_dir):
    """
    tree_dir 안의 model.json을 읽어
    동일 폴더에 splitcond.json으로 분기 기준을 depth별로 그룹화해 저장합니다.
    """
    model_path = os.path.join(tree_dir, "model.json")
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"No model.json found in {tree_dir!r}")

    # 모델 JSON 로드
    with open(model_path, "r") as f:
        tree = json.load(f)

    # 분기 조건 추출
    splits = extract_splits(tree)

    # depth 기준으로 그룹화
    grouped = {}
    for s in splits:
        d = str(s["depth"])
        grouped.setdefault(d, []).append(
            {
                "node_path": s["node_path"],
                "feature": s["feature"],
                "condition": s["condition"],
                "split_bin_idx": s["split_bin_idx"],
            }
        )

    # 저장
    out_path = os.path.join(tree_dir, "splitcond.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(grouped, f, indent=4, ensure_ascii=False)

    print(f"✅ Saved grouped split conditions to {out_path!r}")


def save_tree_to_json(tree, save_path):
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(tree.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"✅ Tree saved to {save_path}")


if __name__ == "__main__":
    base_path = "../data"
    for dataset_name in ["breast-cancer", "spam", "steel"]:
        base_output_dir = os.path.join("./quantized_trees")
        write_dir = os.path.join(base_output_dir, "datasets_quantized", dataset_name)
        os.makedirs(write_dir, exist_ok=True)

        data_path = os.path.join(base_path, f"{dataset_name}.csv")
        df = pd.read_csv(data_path)

        # feature / target 분리
        X = df.drop("target", axis=1).values
        y = df["target"].values

        # 80% train, 20% test 분할 (stratify=y로 클래스 분포 유지)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        encoder = LabelEncoder()
        y_train = encoder.fit_transform(y_train)
        y_test = encoder.fit_transform(y_test)

        # 피처 개수 config 저장
        with open(os.path.join(write_dir, f"{dataset_name}.config"), "w") as f:
            f.write(str(X_train.shape[1]))

        for max_depth in range(3, 11):
            for bitlength in range(1, 10):
                save_dir = os.path.join(write_dir, f"bit{bitlength}")
                os.makedirs(save_dir, exist_ok=True)
                depth_dir = os.path.join(save_dir, f"depth{max_depth}/n_tree1/tree1")
                os.makedirs(depth_dir, exist_ok=True)
                # 균형 트리 생성 후 저장
                balanced = generate_tree(max_depth, bitlength, X_train.shape[1], seed=42)
                with open(os.path.join(depth_dir, "model.json"), "w") as f:
                    json.dump(balanced.to_dict(), f, indent=2)
                save_split_conditions_grouped(depth_dir)

            print(f"Done {dataset_name}")

    write_path = "datasets_synthetic"
    base_output_dir = os.path.join("./quantized_trees")
    write_dir = os.path.join(base_output_dir, write_path, "synthetic")
    os.makedirs(write_dir, exist_ok=True)

    if not os.path.exists(os.path.join(base_output_dir, write_path)):
        os.makedirs(os.path.join(base_output_dir, write_path))

    for max_depth in range(2, 12):
        for bitlength in [4, 8, 12, 16, 24, 26, 32]:
            for num_attributes in range(2, 110, 2):
                save_dir = os.path.join(write_dir, f"bit{bitlength}")
                os.makedirs(save_dir, exist_ok=True)
                depth_dir = os.path.join(save_dir, f"depth{max_depth}")
                os.makedirs(depth_dir, exist_ok=True)
                att_dir = os.path.join(depth_dir, f"att{num_attributes}")
                os.makedirs(att_dir, exist_ok=True)
                t = generate_tree(max_depth, bitlength, num_attributes)
                with open(os.path.join(att_dir, "model.json"), "w") as f:
                    json.dump(t.to_dict(), f, indent=2)
                save_split_conditions_grouped(att_dir)
