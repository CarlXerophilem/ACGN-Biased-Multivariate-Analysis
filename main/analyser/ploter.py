import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from collections import Counter

# ==========================================
# CONFIGURATION & PATHS
'''
Passing `palette` without assigning `hue` is deprecated and will be removed in v0.14.0. Assign the `y` variable to `hue` and set `legend=False` for the same effect.
sns.barplot(x='Count', y='Tag', data=tag_df, palette='viridis')
'''
# ==========================================
# Using raw strings (r"...") to handle Windows backslashes correctly
INPUT_PATH = r"C:\\Users\\Administrator\\Desktop\\mathss\\math 3570 MULTI\\3570project\\src\\main\\analyser\\clean_categorical_table.csv"
OUTPUT_DIR = r"C:\\Users\\Administrator\\Desktop\\mathss\\math 3700\\project\\src\\plots"

# Font settings for Chinese character support (Microsoft YaHei)
plt.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False # Fix minus sign display

# Subject Type Mapping (Bangumi standard)
# 1: Book, 2: Anime, 3: Music, 4: Game, 6: Real
TYPE_MAP = {
    1: 'Book',
    2: 'Anime',
    3: 'Music',
    4: 'Game',
    6: 'Real'
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def load_and_prep_data():
    if not os.path.exists(INPUT_PATH):
        print(f"Error: Data file not found at {INPUT_PATH}")
        return None

    print("Loading data...")
    df = pd.read_csv(INPUT_PATH)
    
    # 1. Map Types
    df['type_label'] = df['type'].map(TYPE_MAP).fillna('Unknown')
    
    # 2. Parse Year
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year.fillna(0).astype(int)
    
    # 3. Parse Tags (String "tag1,tag2" -> List ["tag1", "tag2"])
    # Handle NaN values by converting to empty string first
    df['tags_list'] = df['processed_tags'].fillna("").apply(
        lambda x: [t.strip() for t in str(x).split(',') if t.strip()]
    )
    
    return df

# ==========================================
# PLOTTING FUNCTIONS
# ==========================================

def plot_cake_distribution(df):
    """
    1. Cake Plot (Pie Chart): Distribution of Data Types
    """
    print("Generating Cake Plot (Type Distribution)...")
    
    type_counts = df['type_label'].value_counts()
    
    plt.figure(figsize=(10, 8))
    
    # Colors suitable for ACG (Anime/Game) themes
    colors = sns.color_palette('pastel')[0:len(type_counts)]
    
    patches, texts, autotexts = plt.pie(
        type_counts, 
        labels=type_counts.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors,
        pctdistance=0.85
    )
    
    # Draw circle for Donut chart style (Optional, looks modern)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.title('Data Distribution by Media Type (Cake Plot)', fontsize=16)
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, 'cake_plot_types.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

def plot_count_bar(df, target_type='Music'):
    """
    2. Count Plot: Top Tags for a specific category (e.g., Music)
    """
    print(f"Generating Count Plot for {target_type}...")
    
    # Filter data
    target_df = df[df['type_label'] == target_type]
    
    if target_df.empty:
        print(f"Warning: No data found for type '{target_type}'. Skipping count plot.")
        return

    # Flatten tags list
    all_tags = [tag for tags in target_df['tags_list'] for tag in tags]
    
    if not all_tags:
        print("No tags found. Skipping.")
        return

    # Count frequencies
    tag_counts = Counter(all_tags).most_common(30) # Top 30
    
    tag_df = pd.DataFrame(tag_counts, columns=['Tag', 'Count'])
    
    plt.figure(figsize=(12, 10))
    sns.barplot(x='Count', y='Tag', data=tag_df, palette='viridis')
    
    plt.title(f'Top 30 Tags in {target_type} (Count Plot)', fontsize=16)
    plt.xlabel('Frequency')
    plt.ylabel('Tag')
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, f'count_plot_{target_type.lower()}.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

def plot_heat_map(df, target_type='Music'):
    """
    3. Heat Plot: Tag popularity over Years for a specific category
    """
    print(f"Generating Heat Plot for {target_type}...")
    
    target_df = df[df['type_label'] == target_type]
    
    if target_df.empty:
        print(f"Warning: No data found for type '{target_type}'. Skipping heat plot.")
        return

    # Explode the dataframe so each tag has its own row with the year
    exploded = target_df.explode('tags_list')
    exploded = exploded[exploded['tags_list'].notna()] # Remove empties
    
    # Filter for reasonable year range (e.g., 2000-2024) to keep heatmap readable
    exploded = exploded[(exploded['year'] >= 2000) & (exploded['year'] <= 2025)]
    
    if exploded.empty:
        print("Not enough yearly data for heatmap.")
        return

    # Get Top Tags overall to keep heatmap manageable (Top 25)
    top_tags = exploded['tags_list'].value_counts().head(25).index.tolist()
    filtered_data = exploded[exploded['tags_list'].isin(top_tags)]
    
    # Create Cross-tabulation (Pivot Table)
    heatmap_data = pd.crosstab(filtered_data['tags_list'], filtered_data['year'])
    
    plt.figure(figsize=(16, 10))
    sns.heatmap(heatmap_data, cmap="YlGnBu", linewidths=.5)
    
    plt.title(f'{target_type} Tag Trends by Year (Heat Plot)', fontsize=16)
    plt.xlabel('Year')
    plt.ylabel('Tag')
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, f'heat_plot_{target_type.lower()}.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    ensure_dir(OUTPUT_DIR)
    
    df = load_and_prep_data()
    
    if df is not None:
        # 1. Cake Plot (Global distribution)
        plot_cake_distribution(df)
        
        # 2. Count Plot (Focus on Music as requested)
        # Note: If your previous washer filtered out Type 3, this might be empty.
        # Ideally, ensure your dataset includes Type 3 data now.
        plot_count_bar(df, target_type='Music')
        
        # 3. Heat Plot (Focus on Music)
        plot_heat_map(df, target_type='Music')
        
        # Optional: Generate Anime plots too if useful
        plot_count_bar(df, target_type='Anime')

if __name__ == "__main__":
    main()