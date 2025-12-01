import pandas as pd
import numpy as np
from scipy import stats
import os

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = 'C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\3700 project\\src\\main\\processor\\categorical_table.csv'
OUTPUT_FILE = 'C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\3700 project\\src\\main\\analyser\\clean_categorical_table.csv'

# Hypothesis Settings
# Assuming standard ACG Data types: 1=Book/Comic/Novel, 2=Anime, 4=Game
SOURCE_MEDIA_TYPES = [1] 
ADAPTED_MEDIA_TYPES = [2, 4]

# ==========================================
# MAIN LOGIC
# ==========================================

def load_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return None
    
    # Read CSV, ensuring empty strings are treated as NaN for easier counting initially
    # but we will handle mixed types below
    df = pd.read_csv(INPUT_FILE)
    return df

def analyze_and_clean_nulls(df):
    print("\n--- 1. Null Row Analysis ---")
    
    total_rows = len(df)
    
    # Condition: 
    # (Rating is NULL or 0) AND (Processed_Tag is NULL/Empty OR Processed_Meta is NULL/Empty)
    
    # 1. Normalize columns to handle NaNs vs Empty Strings
    df['score'] = df['score'].fillna(0)
    df['processed_tags'] = df['processed_tags'].fillna("").astype(str)
    df['processed_meta'] = df['processed_meta'].fillna("").astype(str)
    
    # 2. Define the "Bad Row" mask
    # Score invalid?
    score_invalid = (df['score'] == 0)
    # Context invalid? (Both tags AND meta are empty/null)
    # Note: Logic says "||" (OR) in prompt, usually implies if *either* is missing context is low.
    # Adjusting strictly to prompt: (tag == null || meta == null)
    context_invalid = (df['processed_tags'] == "") | (df['processed_meta'] == "")
    
    bad_rows_mask = score_invalid & context_invalid
    
    bad_row_count = bad_rows_mask.sum()
    percent_bad = (bad_row_count / total_rows) * 100
    
    print(f"Total Rows: {total_rows}")
    print(f"Target Null Rows (Score=0 & Missing Info): {bad_row_count}")
    print(f"Percentage of Null Rows: {percent_bad:.2f}%")
    
    # Remove rows
    df_clean = df[~bad_rows_mask].copy()
    print(f"Rows remaining after cleaning: {len(df_clean)}")
    
    return df_clean

def test_japan_hypothesis(df):
    print("\n--- 2. Hypothesis Test: Japanese Works vs Others ---")
    
    # Logic: Check if "日本" (Japan) appears in name_cn, tags, or meta
    # We create a searchable text column for efficiency
    df['search_text'] = (df['name_cn'].fillna('') + " " + 
                         df['processed_tags'] + " " + 
                         df['processed_meta'])
    
    # Create groups
    is_japanese = df['search_text'].str.contains("日本", na=False)
    
    jp_scores = df[is_japanese]['score']
    other_scores = df[~is_japanese]['score']
    
    mean_jp = jp_scores.mean()
    mean_other = other_scores.mean()
    
    print(f"Mean Score (Japanese Works, n={len(jp_scores)}): {mean_jp:.2f}")
    print(f"Mean Score (Other Regions, n={len(other_scores)}): {mean_other:.2f}")
    
    # T-Test (Independent samples, unequal variance/Welch's t-test recommended)
    if len(jp_scores) > 1 and len(other_scores) > 1:
        t_stat, p_val = stats.ttest_ind(jp_scores, other_scores, equal_var=False)
        
        print(f"T-Statistic: {t_stat:.4f}, P-Value: {p_val:.4e}")
        if p_val < 0.05:
            if mean_jp > mean_other:
                print(">> RESULT: REJECT Null Hypothesis. Japanese works have significantly HIGHER ratings.")
            else:
                print(">> RESULT: REJECT Null Hypothesis. Japanese works have significantly LOWER ratings.")
        else:
            print(">> RESULT: FAIL TO REJECT Null Hypothesis. No significant difference found.")
    else:
        print("Not enough data to perform T-test.")

def test_adaptation_hypothesis(df):
    print("\n--- 3. Hypothesis Test: Source (Novel/Manga) vs Adaptation (Anime/Game) ---")
    
    # Type 1: Novel/Manga (Source)
    # Type 2/4: Anime/Game (Adaptation/High Media)
    
    source_scores = df[df['type'].isin(SOURCE_MEDIA_TYPES)]['score']
    adaptation_scores = df[df['type'].isin(ADAPTED_MEDIA_TYPES)]['score']
    
    mean_source = source_scores.mean()
    mean_adapt = adaptation_scores.mean()
    
    print(f"Mean Score (Source/Print, n={len(source_scores)}): {mean_source:.2f}")
    print(f"Mean Score (Adaptation/Screen, n={len(adaptation_scores)}): {mean_adapt:.2f}")
    
    if len(source_scores) > 1 and len(adaptation_scores) > 1:
        # Alternative hypothesis: Adaptation > Source (One-sided test logic, but we print two-sided p-value)
        t_stat, p_val = stats.ttest_ind(adaptation_scores, source_scores, equal_var=False)
        
        # Adjust p-value for one-tailed test if testing specifically for "Higher"
        # However, standard reporting usually starts with two-tailed.
        
        print(f"T-Statistic: {t_stat:.4f}, P-Value: {p_val:.4e}")
        
        if p_val < 0.05:
            if mean_adapt > mean_source:
                print(">> RESULT: REJECT Null Hypothesis. Adaptations rate significantly HIGHER than source material.")
            else:
                print(">> RESULT: REJECT Null Hypothesis. Adaptations rate significantly LOWER than source material.")
        else:
            print(">> RESULT: FAIL TO REJECT Null Hypothesis. No significant difference found.")
    else:
        print("Not enough data to perform T-test.")

def main():
    df = load_data()
    if df is not None:
        # 1. Clean
        df_clean = analyze_and_clean_nulls(df)
        
        # 2. Test Region Hypothesis
        test_japan_hypothesis(df_clean)
        
        # 3. Test Adaptation Hypothesis
        test_adaptation_hypothesis(df_clean)
        
        # 4. Save Final
        # Drop the temp search column used for hypothesis testing
        if 'search_text' in df_clean.columns:
            df_clean = df_clean.drop(columns=['search_text'])
            
        df_clean.to_csv(OUTPUT_FILE, index=False)
        print(f"\nFinal washed table saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()