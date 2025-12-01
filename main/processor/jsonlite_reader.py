import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = 'C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\3700 project\\dumpGitData\\subject.jsonlines'
OUTPUT_FILE = 'C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\3700 project\\src\\main\\processor\\categorical_table.csv'
CHUNK_SIZE = 10000  # Number of rows to process at a time (adjust based on RAM)

# Filter Settings
DATE_START = pd.Timestamp('1980-01-01')
DATE_END = pd.Timestamp('2025-01-01')
VALID_TYPES = [1, 2, 4]

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def clean_tags(tag_list):
    """
    NLP-Simple: Decomposes the complex tag list of dictionaries 
    into a simple comma-separated string of category names.
    Example: [{'name': 'Wii', ...}, {'name': 'Sim', ...}] -> "wii, sim"
    """
    if not isinstance(tag_list, list):
        return ""
    
    # Extract names, lowercase for clustering, and remove duplicates
    extracted_tags = [t.get('name', '').strip().lower() for t in tag_list if 'name' in t]
    
    # Remove empty strings and join
    return ",".join(list(set(filter(None, extracted_tags))))

def process_chunk(chunk):
    """
    Applies filtering and transformation logic to a single dataframe chunk.
    """
    # 1. Date Filter
    # Convert to datetime, coerce errors to NaT
    chunk['date_obj'] = pd.to_datetime(chunk['date'], errors='coerce')
    date_mask = (chunk['date_obj'] >= DATE_START) & (chunk['date_obj'] <= DATE_END)
    
    # 2. Type Filter
    type_mask = chunk['type'].isin(VALID_TYPES)
    
    # 3. NSFW Filter (Ensure strictly False)
    nsfw_mask = chunk['nsfw'] == False
    
    # Apply Filters
    filtered_df = chunk[date_mask & type_mask & nsfw_mask].copy()
    
    if filtered_df.empty:
        return filtered_df

    # 4. NLP/String Decomposition on Tags
    filtered_df['processed_tags'] = filtered_df['tags'].apply(clean_tags)
    
    # 5. NLP/String Decomposition on Meta Tags
    # Meta tags in your JSON are just strings: ["SIM", "Wii"]
    filtered_df['processed_meta'] = filtered_df['meta_tags'].apply(
        lambda x: ",".join([str(i).lower() for i in x]) if isinstance(x, list) else ""
    )

    # 6. Select and Rename final columns
    final_df = filtered_df[[
        'id', 'name', 'name_cn', 'type', 'date', 
        'score', 'processed_tags', 'processed_meta'
    ]]
    
    return final_df

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    print(f"Starting processing of {INPUT_FILE}...")
    
    # Check if file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please run the sample data generator first.")
        return

    first_chunk = True
    total_rows = 0

    # Read JSON in chunks (lines=True assumes Newline Delimited JSON, common for big data)
    # If strictly a JSON array, standard json.load is needed, but pd.read_json handles lines best.
    try:
        with pd.read_json(INPUT_FILE, lines=True, chunksize=CHUNK_SIZE, encoding='utf-8') as reader:
            for chunk in reader:
                processed_chunk = process_chunk(chunk)
                
                if not processed_chunk.empty:
                    # Write to CSV
                    # mode='w' for first chunk, 'a' (append) for subsequent
                    mode = 'w' if first_chunk else 'a'
                    header = first_chunk # Only write header once
                    
                    processed_chunk.to_csv(OUTPUT_FILE, mode=mode, header=header, index=False, encoding='utf-8-sig')
                    
                    total_rows += len(processed_chunk)
                    first_chunk = False
                    print(f"Processed batch... Total rows saved: {total_rows}")
        
        print(f"Done! Cleaned data saved to {OUTPUT_FILE}")

    except ValueError as e:
        print("Error reading JSON. Ensure the format is Newline Delimited JSON (jsonl).")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()
