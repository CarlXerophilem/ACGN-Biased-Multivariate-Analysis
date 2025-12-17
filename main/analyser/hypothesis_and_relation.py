import scipy as sp
import pandas as pd
import numpy as np
import os


INPUT_FILE = 'C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\project\\src\\main\\processor\\categorical_table.csv'
def load_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return None
    
    # Read CSV, ensuring empty strings are treated as NaN for easier counting initially
    # but we will handle mixed types below
    df = pd.read_csv(INPUT_FILE)
    return df

#1. convert keywords in processed_tag to a numeric vector
def vectorize(df):

    return []


def test_japan_hypothesis(df):
    print("\n--- 2. Hypothesis Test: Japanese Works vs Others ---")
    
    # Logic: Check if "日本" (Japan) appears in name_cn, tags, or meta
    # We create a searchable text column for efficiency
    df['search_text'] = (
                         df['processed_tags'] + " " + 
                         df['processed_meta'])
    
    # Create groups
    is_japanese = df['search_text'].str.contains("日本", na=False)
    is_china = df['search_text'].str.contains("中国", na = False)
    
    jp_scores = df[is_japanese]['score']
    other_scores = df[is_china]['score']
    
    mean_jp = jp_scores.mean()
    mean_other = other_scores.mean()
    
    print(f"Mean Score (Japanese Works, n={len(jp_scores)}): {mean_jp:.2f}")
    print(f"Mean Score (Other Regions, n={len(other_scores)}): {mean_other:.2f}")
    
    # T-Test (Independent samples, unequal variance/Welch's t-test recommended)
    if len(jp_scores) > 1 and len(other_scores) > 1:
        t_stat, p_val = sp.stats.ttest_ind(jp_scores, other_scores, equal_var=False)
        
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
    print("\n--- 3. Hypothesis Test: Source (Novel/Manga) vs Adaptation (Anime & Game) ---")
    SOURCE_MEDIA_TYPES = [1]
    NOVEL_TAGS = ['小说']
    MANGA_TAGS = ['漫画','小说']
    ADAPTED_MEDIA_TYPES = [2, 4]
    # Type 1: Novel/Manga (Source)
    # Type 2/4: Anime/Game (Adaptation/High Media)
    
    source_scores_1 = df[df['type'].isin(SOURCE_MEDIA_TYPES) & df['processed_tags'].isin(NOVEL_TAGS)]['score']
    source_scores_2 = df[df['type'].isin(SOURCE_MEDIA_TYPES) & df['processed_tags'].isin(MANGA_TAGS)]['score']
    adaptation_scores = df[df['type'].isin(ADAPTED_MEDIA_TYPES) ]['score']
    
    mean_source = source_scores_1.mean()
    mean_adapt = adaptation_scores.mean()
    
    print(f"Mean Score (Source/Print, n={len(source_scores_1)}): {mean_source:.2f}")
    print(f"Mean Score (Adaptation/Screen, n={len(adaptation_scores)}): {mean_adapt:.2f}")
    
    if len(source_scores_1) > 1 and len(adaptation_scores) > 1:
        # Alternative hypothesis: Adaptation > Source (One-sided test logic, but we print two-sided p-value)
        t_stat, p_val = sp.stats.ttest_ind(adaptation_scores, source_scores_1, equal_var=False)
        
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
        # 2. Test Region Hypothesis
        test_japan_hypothesis(df)

        # 3. Test Adaptation Hypothesis
        test_adaptation_hypothesis(df)
        
if __name__ == "__main__":
    main()
