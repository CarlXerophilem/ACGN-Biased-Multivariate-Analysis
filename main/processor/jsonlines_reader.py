import pandas as pd
import json
import os
import re
import numpy as np
from datetime import datetime, timedelta
from typing import Dict

# ========================================== 0. CONFIGURATION ==========================================

if not os.path.exists('D:\\Dataset'):
    os.makedirs('D:\\Dataset')

INPUT_FILE = ['D:\\Dataset\\25_11_26\\subject.jsonlines', 'D:\\Dataset\\25_10_28\\subject.jsonlines',
              'D:\\Dataset\\25_09_30\\subject.jsonlines', 'D:\\Dataset\\25_08_26\\subject.jsonlines',
              'D:\\Dataset\\25_07_29\\subject.jsonlines', 'D:\\Dataset\\25_06_24\\subject.jsonlines']

OUTPUT_MODERN = ["D:\\Dataset\\25_11_26\\modern_subject.csv", "D:\\Dataset\\25_10_28\\modern_subject.csv",
                 "D:\\Dataset\\25_09_30\\modern_subject.csv", "D:\\Dataset\\25_08_26\\modern_subject.csv",
                 "D:\\Dataset\\25_07_29\\modern_subject.csv", "D:\\Dataset\\25_06_24\\modern_subject.csv"]

OUTPUT_OLD = "D:\\Dataset\\old_subject.csv" 

RELATION_FILE = ['D:\\Dataset\\25_11_26\\subject-relations.jsonlines', 'D:\\Dataset\\25_10_28\\subject-relations.jsonlines',
                 'D:\\Dataset\\25_09_30\\subject-relations.jsonlines', 'D:\\Dataset\\25_08_26\\subject-relations.jsonlines',
                 'D:\\Dataset\\25_07_29\\subject-relations.jsonlines', 'D:\\Dataset\\25_06_24\\subject-relations.jsonlines']

CHUNK_SIZE = 8000 
OLD_START = pd.Timestamp("1940-01-01")
OLD_END = pd.Timestamp("1980-01-01")
MODERN_START = pd.Timestamp("1980-01-01")
MODERN_END = pd.Timestamp("2025-06-01")

TYPE_NOVEL = 5
INVALID_TYPES = [6]
ADAPTATION_RELATIONS = [1]

# =============== 1. UTILITY FUNCTIONS ===================

def extract_episode_number(infobox):
    if not isinstance(infobox, str): return 0
    match = re.search(r"[集话]数\s*=\s*(\d+)", infobox)
    if match: return int(match.group(1))
    return 0

def clean_tags(tag_list):
    if not isinstance(tag_list, list): return ""
    names = [t.get("name", "").strip() for t in tag_list if isinstance(t, dict)]
    names = list({n for n in names if n})
    return ",".join(names)

def compute_comment_amount(score_details):
    if not isinstance(score_details, dict): return 0
    return int(sum(score_details.get(str(k), 0) for k in range(1, 11)))

def recalculate_score(score_details):
    if not isinstance(score_details, dict): return 0.0
    total_score = sum(int(k) * score_details.get(str(k), 0) for k in range(1, 11))
    total_count = sum(score_details.get(str(k), 0) for k in range(1, 11))
    if total_count == 0: return 0.0
    return round(total_score / total_count, 2)

def compute_skewness(score_details):
    if not isinstance(score_details, dict): return 0.0
    scores = []
    for s in range(1, 11): scores.extend([s] * score_details.get(str(s), 0))
    if len(scores) < 15: return 0.0
    arr = np.array(scores, dtype=float)
    mean, std = arr.mean(), arr.std()
    if std == 0: return 0.0
    return float(np.mean((arr - mean) ** 3) / (std ** 3))

def compute_std(score_details):
    if not isinstance(score_details, dict): return 0.0
    scores = []
    for s in range(1, 11): scores.extend([s] * score_details.get(str(s), 0))
    if len(scores) < 15: return 0.0
    return float(np.std(scores, ddof=0))

def compute_played_amount(fav):
    if not isinstance(fav, dict): return 0
    return int(fav.get("done", 0)) + int(fav.get("doing", 0))

def compute_dropped_amount(fav):
    if not isinstance(fav, dict): return 0
    return int(fav.get("dropped", 0))

def get_snapshot_date(file_path: str) -> datetime:
    try:
        dir_name = os.path.basename(os.path.dirname(file_path))
        return datetime.strptime(dir_name, '%y_%m_%d')
    except:
        return datetime.now()

# =============== 2. MAPPING FUNCTIONS ===================

def build_type_map(subject_file_path: str) -> Dict[int, int]:
    """
    Pass 1: Scans the file to create a map of {id: type}.
    This is CRITICAL to know if an ID refers to a Novel(5), Manga(1), or Game(4).
    """
    type_map = {}
    print(f"Building Type Map from {subject_file_path}...")
    
    # We open the file manually to avoid loading everything into Pandas at once
    try:
        with open(subject_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    sid = data.get('id')
                    stype = data.get('type')
                    
                    # Apply Novel Promotion Logic here for the map
                    # If it's a book (1) and has '小说' in tags, it's a Novel (5)
                    tags = data.get('tags', [])
                    if stype == 1 and isinstance(tags, list):
                        for t in tags:
                            if isinstance(t, dict) and t.get('name') == '小说':
                                stype = TYPE_NOVEL
                                break
                    
                    if sid:
                        type_map[sid] = stype
                except:
                    continue
    except FileNotFoundError:
        print("File not found.")
        
    print(f"Type Map built with {len(type_map)} entries.")
    return type_map

def load_relation_map(relation_file_path: str) -> Dict[int, int]:
    if not os.path.exists(relation_file_path): return {}
    relation_map = {}
    print(f"Loading relations from {relation_file_path}...")
    with open(relation_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                sid, rel, rid = data.get("subject_id"), data.get("relation_type"), data.get("related_subject_id")
                if rel in ADAPTATION_RELATIONS and sid and rid:
                    if sid not in relation_map: relation_map[sid] = rid
            except: continue
    print(f"Loaded {len(relation_map)} mappings.")
    return relation_map

# ================== 3. PROCESS CHUNK ==================

def process_chunk(chunk, relation_map, type_map, snapshot_date):
    chunk = chunk[(chunk["rank"] != 0) & chunk["score"].notnull() & (chunk["score"] > 1.0) & (chunk["tags"].notnull())]
    chunk = chunk[~chunk["type"].isin(INVALID_TYPES)]
    if chunk.empty: return pd.DataFrame(), pd.DataFrame()

    chunk["date_obj"] = pd.to_datetime(chunk["date"], exact=False, errors="coerce")

    # Re-apply type correction for the main dataframe (consistency)
    def correct_type(row):
        if row['type'] == 1 and isinstance(row["tags"], list):
            if any(t.get("name") == "小说" for t in row["tags"] if isinstance(t, dict)):
                return TYPE_NOVEL
        return row["type"]
    chunk["type"] = chunk.apply(correct_type, axis=1)

    STABILITY_CUTOFF = snapshot_date - timedelta(days=365)
    chunk["is_stable"] = chunk["date_obj"] < STABILITY_CUTOFF 
    chunk = chunk[chunk["is_stable"] | (chunk["date_obj"] >= MODERN_START)]

    chunk["episode_number"] = chunk["infobox"].apply(extract_episode_number)
    chunk["comment_amount"] = chunk["score_details"].apply(compute_comment_amount)
    chunk["score"] = chunk["score_details"].apply(recalculate_score)
    chunk["score_std"] = chunk["score_details"].apply(compute_std)
    for i in range(1, 11):
        chunk[f"{i}_amount"] = chunk["score_details"].apply(lambda sd: sd.get(str(i), 0) if isinstance(sd, dict) else 0)
    chunk["sk"] = chunk["score_details"].apply(compute_skewness)
    chunk["played_amount"] = chunk["favorite"].apply(compute_played_amount)
    chunk["dropped_amount"] = chunk["favorite"].apply(compute_dropped_amount)
    chunk["tags_clean"] = chunk["tags"].apply(clean_tags)

    # --- KEY CHANGE: Source Type Lookup ---
    # 1. Get Source ID (from_id)
    chunk["from_id"] = chunk["id"].apply(lambda x: relation_map.get(x, 0))
    # 2. Get Source Type (from_type) by looking up from_id in type_map
    chunk["from_type"] = chunk["from_id"].apply(lambda x: type_map.get(x, 0))

    final = chunk[[
        "id", "rank", "date", "type", "name", "name_cn", "score", "score_std",
        "10_amount", "9_amount", "8_amount", "7_amount", "6_amount", "5_amount", 
        "4_amount", "3_amount", "2_amount", "1_amount", "comment_amount",
        "episode_number", "played_amount", "dropped_amount", "tags_clean",
        "platform", "series", "nsfw", "sk", "from_id", "from_type", "is_stable", "date_obj"
    ]].copy()

    old = final[(final["date_obj"] >= OLD_START) & (final["date_obj"] < OLD_END)].copy()
    modern = final[(final["date_obj"] >= MODERN_START) & (final["date_obj"] <= MODERN_END)].copy()
    return old, modern

# ================== MAIN ==================

def main():
    print("Starting processing...")
    all_old_list = []
    
    for i, (input_path, output_path, relation_path) in enumerate(zip(INPUT_FILE, OUTPUT_MODERN, RELATION_FILE)):
        if not os.path.exists(input_path): continue
        print(f"\n--- Snapshot {i+1}: {os.path.basename(os.path.dirname(input_path))} ---")
        
        snapshot_date = get_snapshot_date(input_path)
        # 1. Build Global Maps (Double Pass Strategy)
        type_map = build_type_map(input_path) 
        relation_map = load_relation_map(relation_path)
        
        current_modern, current_old = [], []
        reader = pd.read_json(input_path, lines=True, chunksize=CHUNK_SIZE, encoding="utf-8")
        
        for chunk in reader:
            old, modern = process_chunk(chunk, relation_map, type_map, snapshot_date)
            if not old.empty: current_old.append(old)
            if not modern.empty: current_modern.append(modern)
        
        if current_modern:
            pd.concat(current_modern, ignore_index=True).sort_values("rank").drop(columns=["date_obj"]).to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"Saved: {output_path}")

        if current_old: all_old_list.extend(current_old)

    if all_old_list:
        pd.concat(all_old_list, ignore_index=True).drop_duplicates('id').sort_values("rank").drop(columns=["date_obj"], errors='ignore').to_csv(OUTPUT_OLD, index=False, encoding="utf-8-sig")
        print(f"Saved OLD: {OUTPUT_OLD}")

if __name__ == "__main__":
    main()