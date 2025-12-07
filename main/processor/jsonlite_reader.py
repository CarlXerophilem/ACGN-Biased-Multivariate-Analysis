import pandas as pd
import json
import os
import re
import numpy as np
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = 'C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\project\\dumpGitData\\subject.jsonlines'
# OUTPUT_FILE = 'C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\3700 project\\src\\main\\processor\\categorical_table.csv'
OUTPUT_OLD = "old_anime.csv"
OUTPUT_MODERN = "modern_anime.csv"
CHUNK_SIZE = 8000 # Number of rows to process at a time (adjust based on RAM)

# Date partitions
OLD_START = pd.Timestamp("1940-01-01")
OLD_END = pd.Timestamp("1980-01-01")
MODERN_START = pd.Timestamp("1980-01-01")
MODERN_END = pd.Timestamp("2025-01-01")

# Remove type = 6 only
INVALID_TYPES = [6]

# ==========================================================
# UTILITIES
# ==========================================================

def extract_episode_number(infobox):
    """Extract episode number from infobox across manga/anime/novel."""
    if not isinstance(infobox, str):
        return 0
    match = re.search(r"[集话]数\s*=\s*(\d+)", infobox)
    if match:
        return int(match.group(1))
    return 0


def clean_tags(tag_list):
    """Convert [{'name': 'FPS', ...}, {...}] to comma-separated distinct names."""
    if not isinstance(tag_list, list):
        return ""
    names = [t.get("name", "").strip() for t in tag_list if isinstance(t, dict)]
    names = list({n for n in names if n})
    return ",".join(names)


def compute_comment_amount(score_details):
    """Sum all score_details."""
    if not isinstance(score_details, dict):
        return 0
    return int(sum(score_details.get(str(k), 0) for k in range(1, 11)))


def compute_skewness(score_details):
    """Compute skewness from score distribution."""
    if not isinstance(score_details, dict):
        return 0.0

    scores = []
    for s in range(1, 11):
        count = score_details.get(str(s), 0)
        if count > 0:
            scores.extend([s] * count)

    if len(scores) < 3:
        return 0.0

    arr = np.array(scores, dtype=float)
    mean = arr.mean()
    std = arr.std()
    if std == 0:
        return 0.0

    skew = np.mean((arr - mean) ** 3) / (std ** 3)
    return float(skew)


def compute_played_amount(fav):
    """favorite.done + favorite.doing"""
    if not isinstance(fav, dict):
        return 0
    return int(fav.get("done", 0)) + int(fav.get("doing", 0))


# ==========================================================
# PROCESS ONE CHUNK
# ==========================================================
def process_chunk(chunk):
    # Remove null score
    chunk = chunk[chunk["score"].notnull()]

    # Remove type = 6
    chunk = chunk[~chunk["type"].isin(INVALID_TYPES)]

    if chunk.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Convert date
    chunk["date_obj"] = pd.to_datetime(chunk["date"], errors="coerce")

    # Promote novel type
    def correct_type(row):
        if isinstance(row["tags"], list):
            if any(t.get("name") == "小说" for t in row["tags"] if isinstance(t, dict)):
                return 5
        return row["type"]

    chunk["type"] = chunk.apply(correct_type, axis=1)

    # Extract episode number
    chunk["episode_number"] = chunk["infobox"].apply(extract_episode_number)

    # Compute comment amount
    chunk["comment_amount"] = chunk["score_details"].apply(compute_comment_amount)

    # Compute skewness
    chunk["sk"] = chunk["score_details"].apply(compute_skewness)

    # Played amount
    chunk["played_amount"] = chunk["favorite"].apply(compute_played_amount)

    # Clean tags
    chunk["tags_clean"] = chunk["tags"].apply(clean_tags)

    # Select final fields
    final = chunk[
        [
            "rank",
            "date",
            "name",
            "name_cn",
            "score",
            "comment_amount",
            "episode_number",
            "played_amount",
            "tags_clean",
            "platform",
            "series",
            "nsfw",
            "sk",
            "date_obj",
        ]
    ].copy()

    # Partition
    old_mask = (final["date_obj"] >= OLD_START) & (final["date_obj"] < OLD_END)
    mod_mask = (final["date_obj"] >= MODERN_START) & (final["date_obj"] <= MODERN_END)

    old = final[old_mask].copy()
    modern = final[mod_mask].copy()

    return old, modern


# ==========================================================
# MAIN
# ==========================================================
def main():
    print("Starting processing...")

    if not os.path.exists(INPUT_FILE):
        print("Input file not found.")
        return

    old_list = []
    modern_list = []

    reader = pd.read_json(INPUT_FILE, lines=True, chunksize=CHUNK_SIZE, encoding="utf-8")

    for chunk in reader:
        old, modern = process_chunk(chunk)
        if not old.empty:
            old_list.append(old)
        if not modern.empty:
            modern_list.append(modern)

    if old_list:
        old_final = pd.concat(old_list, ignore_index=True).sort_values("rank")
        old_final.drop(columns=["date_obj"], inplace=True)
        old_final.to_csv(OUTPUT_OLD, index=False, encoding="utf-8-sig")
        print(f"Saved: {OUTPUT_OLD}")

    if modern_list:
        modern_final = pd.concat(modern_list, ignore_index=True).sort_values("rank")
        modern_final.drop(columns=["date_obj"], inplace=True)
        modern_final.to_csv(OUTPUT_MODERN, index=False, encoding="utf-8-sig")
        print(f"Saved: {OUTPUT_MODERN}")

    print("Completed successfully.")


if __name__ == "__main__":
    main()
