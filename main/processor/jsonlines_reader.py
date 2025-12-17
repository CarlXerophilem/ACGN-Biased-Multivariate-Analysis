
import pandas as pd
import json
import os
import re
import numpy as np
from datetime import datetime, timedelta
from typing import Dict

# ========================================== 0. INPUT/OUTPUT CONFIGURATION ==========================================

# Use June to November 2025 dataset
# create Dataset folder if not exists (This should be handled outside, but kept for robustness)
if not os.path.exists('D:\\Dataset'):
    os.makedirs('D:\\Dataset')

# List of input subject files (JSON lines)
INPUT_FILE = ['D:\\Dataset\\25_11_26\\subject.jsonlines', 'D:\\Dataset\\25_10_28\\subject.jsonlines',
              'D:\\Dataset\\25_09_30\\subject.jsonlines', 'D:\\Dataset\\25_08_26\\subject.jsonlines',
              'D:\\Dataset\\25_07_29\\subject.jsonlines', 'D:\\Dataset\\25_06_24\\subject.jsonlines']

# List of output modern CSV files (one for each input snapshot)
OUTPUT_MODERN = ["D:\\Dataset\\25_11_26\\modern_subject.csv", "D:\\Dataset\\25_10_28\\modern_subject.csv",
                 "D:\\Dataset\\25_09_30\\modern_subject.csv", "D:\\Dataset\\25_08_26\\modern_subject.csv",
                 "D:\\Dataset\\25_07_29\\modern_subject.csv", "D:\\Dataset\\25_06_24\\modern_subject.csv"]

# Single output for old data (as it's stable and partitioned only once)
OUTPUT_OLD = "D:\\Dataset\\old_subject.csv" 

# List of input relation files
RELATION_FILE = ['D:\\Dataset\\25_11_26\\subject-relations.jsonlines', 'D:\\Dataset\\25_10_28\\subject-relations.jsonlines',
                 'D:\\Dataset\\25_09_30\\subject-relations.jsonlines', 'D:\\Dataset\\25_08_26\\subject-relations.jsonlines',
                 'D:\\Dataset\\25_07_29\\subject-relations.jsonlines', 'D:\\Dataset\\25_06_24\\subject-relations.jsonlines']

CHUNK_SIZE = 8000 

# Date partitions
OLD_START = pd.Timestamp("1940-01-01")
OLD_END = pd.Timestamp("1980-01-01")
MODERN_START = pd.Timestamp("1980-01-01")
MODERN_END = pd.Timestamp("2025-06-01")

# Type Codes
TYPE_NOVEL = 5 # Custom code after '小说' tag promotion
INVALID_TYPES = [6] # Remove type = 6 (Real/3D)
ADAPTATION_RELATIONS = [1] # Type 1: Adaptation

# =============== 1. EXTRACTION & UTILITY FUNCTIONS ===================

# (All your extraction and compute functions (episode_number, clean_tags, recalculate_score, etc.) 
# are assumed to be correct and remain here. Only the critical Novel promotion is shown.)

def extract_episode_number(infobox):
    # ... (function body omitted for brevity) ...
    if not isinstance(infobox, str):
        return 0
    match = re.search(r"[集话]数\s*=\s*(\d+)", infobox)
    if match:
        return int(match.group(1))
    return 0

def clean_tags(tag_list):
    # ... (function body omitted for brevity) ...
    if not isinstance(tag_list, list):
        return ""
    names = [t.get("name", "").strip() for t in tag_list if isinstance(t, dict)]
    names = list({n for n in names if n})
    return ",".join(names)

def compute_comment_amount(score_details):
    # ... (function body omitted for brevity) ...
    if not isinstance(score_details, dict):
        return 0
    return int(sum(score_details.get(str(k), 0) for k in range(1, 11)))

def recalculate_score(score_details):
    # ... (function body omitted for brevity) ...
    if not isinstance(score_details, dict):
        return 0.0
    total_score = 0
    total_count = 0
    for s in range(1, 11):
        count = score_details.get(str(s), 0)
        total_score += s * count
        total_count += count
    if total_count == 0:
        return 0.0
    average = total_score / total_count
    return round(average, 2)

def compute_skewness(score_details):
    # ... (function body omitted for brevity) ...
    if not isinstance(score_details, dict): return 0.0
    scores = []
    for s in range(1, 11): scores.extend([s] * score_details.get(str(s), 0))
    if len(scores) < 15: return 0.0
    arr = np.array(scores, dtype=float)
    mean = arr.mean()
    std = arr.std()
    if std == 0: return 0.0
    skew = np.mean((arr - mean) ** 3) / (std ** 3)
    return float(skew)

def compute_std(score_details):
    # ... (function body omitted for brevity) ...
    if not isinstance(score_details, dict): return 0.0
    scores = []
    for s in range(1, 11): scores.extend([s] * score_details.get(str(s), 0))
    if len(scores) < 15: return 0.0
    arr = np.array(scores, dtype=float)
    std = np.std(arr, ddof=0)
    return float(std)

def compute_played_amount(fav):
    # ... (function body omitted for brevity) ...
    if not isinstance(fav, dict):
        return 0
    return int(fav.get("done", 0)) + int(fav.get("doing", 0))

def compute_dropped_amount(fav):
    # ... (function body omitted for brevity) ...
    if not isinstance(fav, dict):
        return 0
    return int(fav.get("dropped", 0))

# --- NEW UTILITY ---
def get_snapshot_date(file_path: str) -> datetime:
    """Extracts YYYY-MM-DD snapshot date from the directory name (e.g., 25_11_26)"""
    try:
        dir_name = os.path.basename(os.path.dirname(file_path))
        # Assuming the format is YY_MM_DD
        return datetime.strptime(dir_name, '%y_%m_%d')
    except:
        print("Warning: Could not parse snapshot date. Using today's date.")
        return datetime.now()


# =============== 2. RELATION CONFIGURATION (FIXED) ===================

# FIXED: Now accepts the specific relation file path
def load_relation_map(relation_file_path: str) -> Dict[int, int]:
    """
    Reads the specific subject-relations.jsonlines file and creates a map: {adapted_id: source_id}.
    """
    if not os.path.exists(relation_file_path):
        print(f"Relation file not found: {relation_file_path}. Skipping relation mapping for this month.")
        return {}
    
    relation_map = {}
    print(f"Loading relations from {relation_file_path}...")
    
    with open(relation_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                
                subject_id = data.get("subject_id")
                relation_type = data.get("relation_type")
                related_subject_id = data.get("related_subject_id")
                
                if relation_type in ADAPTATION_RELATIONS and subject_id is not None and related_subject_id is not None:
                    # only store the FIRST source found 
                    if subject_id not in relation_map:
                        relation_map[subject_id] = related_subject_id
                        
            except json.JSONDecodeError:
                continue
                
    print(f"Loaded {len(relation_map)} primary adaptation mappings.")
    return relation_map


# ================== 3. PROCESS CHUNKS (FIXED) ==================

# FIXED: Now accepts the snapshot date for stability check
def process_chunk(chunk, relation_map, snapshot_date: datetime):
    
    # 1. Filter
    chunk = chunk[(chunk["rank"] != 0) & chunk["score"].notnull() & (chunk["score"] > 1.0) & (chunk["tags"].notnull())]
    chunk = chunk[~chunk["type"].isin(INVALID_TYPES)]

    if chunk.empty:
        return pd.DataFrame(), pd.DataFrame()

    # 2. Type Correction & Date Conversion
    chunk["date_obj"] = pd.to_datetime(chunk["date"], exact= False, errors="coerce")

    def correct_type(row):
        if isinstance(row["tags"], list):
            if any(t.get("name") == "小说" for t in row["tags"] if isinstance(t, dict)):
                return TYPE_NOVEL # Use the constant 5
        return row["type"]

    chunk["id"] = chunk["id"]
    chunk["type"] = chunk.apply(correct_type, axis=1)

    # 3. Stability Filter (The critical missing part)
    STABILITY_CUTOFF = snapshot_date - timedelta(days=365)
    # is_stable: True if the release date is before the cutoff date
    chunk["is_stable"] = chunk["date_obj"] < STABILITY_CUTOFF 


    # 4. Feature Extraction
    chunk["episode_number"] = chunk["infobox"].apply(extract_episode_number)
    chunk["comment_amount"] = chunk["score_details"].apply(compute_comment_amount)
    chunk["score"] = chunk["score_details"].apply(recalculate_score)
    chunk["score_std"] = chunk["score_details"].apply(compute_std)
    
    # Extract score amounts
    for i in range(1, 11):
        chunk[f"{i}_amount"] = chunk["score_details"].apply(lambda sd: sd.get(str(i), 0) if isinstance(sd, dict) else 0)

    chunk["sk"] = chunk["score_details"].apply(compute_skewness)
    chunk["played_amount"] = chunk["favorite"].apply(compute_played_amount)
    chunk["dropped_amount"] = chunk["favorite"].apply(compute_dropped_amount)
    chunk["tags_clean"] = chunk["tags"].apply(clean_tags)

    # 5. Adaptation Mapping
    # We also include 'is_stable' here
    chunk["from_id"] = chunk["id"].apply(lambda x: relation_map.get(x, 0))

    # 6. Final Selection
    # Added 'date_obj' and 'is_stable' to the list
    final = chunk[
        [
            "id", "rank", "date", "type", "name", "name_cn", "score", "score_std",
            "10_amount", "9_amount", "8_amount", "7_amount", "6_amount", "5_amount", 
            "4_amount", "3_amount", "2_amount", "1_amount", "comment_amount",
            "episode_number", "played_amount", "dropped_amount", "tags_clean",
            "platform", "series", "nsfw", "sk", "from_id", "is_stable", "date_obj"
        ]
    ].copy()

    # 7. Partition
    old_mask = (final["date_obj"] >= OLD_START) & (final["date_obj"] < OLD_END)
    mod_mask = (final["date_obj"] >= MODERN_START) & (final["date_obj"] <= MODERN_END)

    old = final[old_mask].copy()
    modern = final[mod_mask].copy()

    return old, modern


# ==========================================================
# MAIN (FIXED)
# ==========================================================
def main():
    print("Starting processing...")

    # We need to collect ALL old subjects across all runs to save them once
    all_old_list = []
    
    # Loop over all file sets simultaneously using zip
    for i, (input_path, output_path, relation_path) in enumerate(zip(INPUT_FILE, OUTPUT_MODERN, RELATION_FILE)):
        
        print(f"\n--- Processing Snapshot {i+1}/{len(INPUT_FILE)}: {os.path.basename(os.path.dirname(input_path))} ---")
        
        if not os.path.exists(input_path):
            print(f"Skipping: Input file not found at {input_path}")
            continue

        # 1. Get snapshot date for stability check
        snapshot_date = get_snapshot_date(input_path)
        
        # 2. Load relations specific to this month's file
        relation_map = load_relation_map(relation_path)
        
        # 3. Process the subject file
        current_modern_list = []
        current_old_list = []
        
        reader = pd.read_json(input_path, lines=True, chunksize=CHUNK_SIZE, encoding="utf-8")
        
        for chunk in reader:
            # Pass the relation map AND the snapshot date to the chunk processor
            old, modern = process_chunk(chunk, relation_map, snapshot_date) 
            
            if not old.empty:
                current_old_list.append(old)
            if not modern.empty:
                current_modern_list.append(modern)
        
        # 4. Save Modern Data
        if current_modern_list:
            modern_final = pd.concat(current_modern_list, ignore_index=True).sort_values("rank")
            # date_obj is needed for partitioning but not for saving
            modern_final.drop(columns=["date_obj"], inplace=True) 
            modern_final.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"Saved MODERN data to: {output_path}")

        # 5. Collect Old Data (only need to save once, but collect from all runs)
        if current_old_list:
            all_old_list.extend(current_old_list)
        
        print(f"Completed processing snapshot {i+1}.")

    # 6. Save Final Old Data (once)
    if all_old_list:
        old_final = pd.concat(all_old_list, ignore_index=True).drop_duplicates(subset=['id'], keep='first').sort_values("rank")
        # Ensure 'date_obj' is dropped if it made it into the old list via extend
        if 'date_obj' in old_final.columns:
             old_final.drop(columns=["date_obj"], inplace=True)
             
        old_final.to_csv(OUTPUT_OLD, index=False, encoding="utf-8-sig")
        print(f"\nSaved OLD data to: {OUTPUT_OLD}")
        
    print("\nAll processing complete.")


if __name__ == "__main__":
    main()

