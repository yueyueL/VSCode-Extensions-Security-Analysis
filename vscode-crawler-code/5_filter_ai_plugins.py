import csv
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
import random
from datetime import datetime
import sys
import io
from dateutil import parser
import os


# Increase the CSV field size limit
csv.field_size_limit(sys.maxsize)

def is_ai_related(text):
    keywords = [
        'GPT', 'OpenAI', 'Claude', 'Copilot',  'DALL-E',
        'Generative AI', 'ChatGPT', 'Artificial Intelligence', 'Machine Learning',
        'Neural Network', 'Deep Learning', 'NLP', 'Natural Language Processing',
        'Text Generation', 'Language Model', 'Transformer', 
        'Chatbot', 'Virtual Assistant', 'AI Assistant', 'AI Tool',
        'AI Writing', 'AI Art', 'AI Image', 'AI Video', 'AI Audio',
        'AI Analytics', 'AI Automation', 'Prompt Engineering',
        'Large Language Model', 'Diffusion Model',
        'Stable Diffusion', 'Midjourney', "LLAMA", "Gemini", "GenAI", "Anthropic", "Hugging Face", 'GPT-3', 'GPT-4', 'Perplexity AI',
        'Whisper AI', 'Jasper AI', 'Cohere', "LangChain", 'AI Model', 'AI API',
        'AI Integration', 'AI-Powered', 'AI-Driven', 'AI-Based', "IntelliCode", "Code Chat",  "AI chat", "AI Code"
    ]
    text = text.lower()
    matched_keywords = [keyword for keyword in keywords if keyword.lower() in text]
    return matched_keywords

def remove_null_bytes(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    content = content.replace(b'\x00', b'')
    return io.StringIO(content.decode('utf-8', errors='ignore'))

def process_csv(data_file, desc_file):
    ai_extensions = []
    keyword_counts = Counter()
    total_apps = 0
    descriptions = {}
    
    # Load descriptions
    desc_file_content = remove_null_bytes(desc_file)
    reader = csv.DictReader(desc_file_content)
    for row in reader:
        descriptions[row.get('extensionId', '')] = row.get('Description', '') + " " + row.get('shortDescription', '')
    
    # Process main data
    data_file_content = remove_null_bytes(data_file)
    reader = csv.DictReader(data_file_content)
    
    # Print column names for debugging
    print("Available columns in the data file:", reader.fieldnames)
    
    for row in reader:
        total_apps += 1
        ext_id = row.get('extensionId', '')
        if not ext_id:
            print("Warning: Missing extensionId in row:", row)
            continue
        
        description = descriptions.get(ext_id, '')
        text = f"{row.get('extensionName', '')} {description}"
        matched_keywords = is_ai_related(text)
        if matched_keywords:
            ai_extensions.append({
                'id': ext_id,  # Add this line
                'title': row.get('displayName', ''),
                'users': int(row.get('install', '0')) if row.get('install', '').isdigit() else 0,
                'category': row.get('categories', '').split(',')[0] if row.get('categories') else 'None',
                'rating': float(row.get('averagerating', '0')) if row.get('averagerating') else 0,
                'last_updated': row.get('lastUpdated', '')  # Capture the full timestamp
            })
            keyword_counts.update(matched_keywords)

        
    
    return ai_extensions, keyword_counts, total_apps, descriptions 

def plot_distribution(data, key, title, filename):
    counter = Counter(item[key] for item in data)
    labels, values = zip(*counter.most_common(10))
    
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    colors = ['#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac']
    bars = plt.bar(labels, values, color=colors[:len(labels)])
    # plt.title(title, fontsize=18, fontweight='bold')
    plt.xlabel(key.capitalize(), fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.ylabel('Count', fontsize=18)
    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        bar.set_edgecolor('black')
        bar.set_linewidth(1)
    
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    
    plt.tight_layout()
    plt.savefig(f'data/fig/{filename}', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    colors = ['#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac']
    return random.choice(colors)

def create_wordcloud(titles):
    text = ' '.join(titles)
    text = re.sub(r'\b(for|the|a|an|and|or|but|in|on|at|to|of)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s]', '', text)
    
    wordcloud = WordCloud(width=800, height=400, 
                          background_color='white', 
                          color_func=color_func,
                          contour_width=1,
                          contour_color='black').generate(text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    # plt.title('Word Cloud of AI Plugins Titles', fontsize=18, fontweight='bold')
    
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    
    plt.tight_layout(pad=0)
    plt.savefig('data/fig/title_wordcloud.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

def plot_keyword_counts(keyword_counts):
    keywords, counts = zip(*keyword_counts.most_common(20))
    
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    colors = ['#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac']
    bars = plt.barh(keywords, counts, color=colors[:len(keywords)])
    # plt.title('Top 20 AI-related Keywords in VSCode Plugins', fontsize=18, fontweight='bold')
    plt.xlabel('Number of Plugins', fontsize=18)
    plt.ylabel('Keywords', fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    for bar in bars:
        bar.set_edgecolor('black')
        bar.set_linewidth(1)
    
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    
    plt.tight_layout()
    plt.savefig('data/fig/keyword_counts.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

def plot_last_updated_distribution(ai_extensions, all_extensions):
    ai_counts = Counter()
    all_counts = Counter()
    
    for ext in all_extensions:
        try:
            date = parser.parse(ext.get('lastUpdated', '')).year
            if date > 2018:
                all_counts[date] += 1
        except (ValueError, KeyError, TypeError):
            continue
    
    for ext in ai_extensions:
        try:
            date = parser.parse(ext.get('last_updated', '')).year
            if date > 2018:
                ai_counts[date] += 1
        except (ValueError, KeyError, TypeError):
            continue
    
    sorted_years = sorted(set(all_counts.keys()) | set(ai_counts.keys()))
    ai_extension_counts = [ai_counts[year] for year in sorted_years]
    ai_percentages = [ai_counts[year] / all_counts[year] * 100 if all_counts[year] > 0 else 0 for year in sorted_years]
    
    if not sorted_years:
        print("No valid years found. Skipping chart creation.")
        return
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    colors = ['#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac']
    bars = ax1.bar([str(year) for year in sorted_years], ai_extension_counts, color=colors[-1], label='AI Plugins')
    
    for bar in bars:
        bar.set_edgecolor('black')
        bar.set_linewidth(1)
    
    ax1.set_xlabel('Year', fontsize=20)
    ax1.set_ylabel('Number of AI Plugins', fontsize=20)
    ax1.tick_params(axis='x', labelsize=20)
    ax1.tick_params(axis='y', labelsize=20)
    ax2 = ax1.twinx()
    ax2.plot([str(year) for year in sorted_years], ai_percentages, color='#b2182b', marker='o', linestyle='-', linewidth=2, markersize=8, label='AI Extensions Proportion')
    ax2.set_ylabel('AI Plugins Proportion (%)', fontsize=20)
    ax2.tick_params(axis='y', labelsize=20)
    y1_max = max(ai_extension_counts)
    y2_max = max(ai_percentages)
    ax1.set_ylim(0, y1_max * 1.1)
    ax2.set_ylim(0, y2_max * 1.1)
    
    y1_ticks = [300, 600, 900, 1200, 1500]
    ax1.set_yticks(y1_ticks)
    ax1.set_yticklabels([f'{tick:,}' for tick in y1_ticks])
    
    y2_ticks = [2, 4, 6, 8, 10]
    ax2.set_yticks(y2_ticks)
    ax2.set_yticklabels([f'{tick}%' for tick in y2_ticks])
    
    ax2.yaxis.set_ticks_position('right')
    ax2.yaxis.set_label_position('right')
    
    # plt.title('Growth of AI Plugins and Their Proportion (After 2018)', fontsize=18, fontweight='bold')
    plt.xticks(rotation=45)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=20)
    
    for ax in [ax1, ax2]:
        ax.spines['top'].set_color('black')
        ax.spines['bottom'].set_color('black') 
        ax.spines['left'].set_color('black')
        ax.spines['right'].set_color('black')
    
    plt.tight_layout()
    plt.savefig('data/fig/last_updated_distribution.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

    print("AI extension counts:", ai_extension_counts)
    print("All extension counts:", all_counts)
    print("AI percentages:", ai_percentages)

def main():
    data_file = 'data/vscode_extension_metadata.csv'
    desc_file = 'data/vscode_extension_description.csv'
    ai_extensions_saved = 'data/ai_plugins.csv'
    ai_extensions, keyword_counts, total_apps, descriptions = process_csv(data_file, desc_file)

    # save the ai_extensions to a csv file
    with open(ai_extensions_saved, 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['id', 'title', 'users', 'category', 'rating', 'last_updated'])
        writer.writeheader()
        for ext in ai_extensions:
            writer.writerow(ext)
    
    with open(data_file, 'r', encoding='utf-8') as csvfile:
        all_extensions = list(csv.DictReader(csvfile))
    
    print(f"Total applications in CSV: {total_apps}")
    print(f"Total AI-related extensions: {len(ai_extensions)}")
    
    print("\nKeyword match counts:")
    for keyword, count in keyword_counts.most_common():
        print(f"{keyword}: {count}")
    
    plot_keyword_counts(keyword_counts)
    
    top_by_users = sorted(ai_extensions, key=lambda x: x['users'], reverse=True)[:30]
    print("\nTop 10 AI-related extensions by Users:")
    for ext in top_by_users[:30]:
        # Get the matched keywords for this extension
        text = f"{ext['title']} {descriptions.get(ext['id'], '')}"
        matched_keywords = is_ai_related(text)
        print(f"{ext['title']}: {ext['users']} users")
        print(f"  Matched AI keywords: {', '.join(matched_keywords)}")
        print()  
    
    user_ranges = [0, 100, 1000, 10000, 100000, float('inf')]
    user_labels = ['0-99', '100-999', '1k-9.9k', '10k-99.9k', '100k+']
    user_dist = [sum(1 for ext in ai_extensions if user_ranges[i] <= ext['users'] < user_ranges[i+1]) for i in range(len(user_ranges)-1)]
    
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    colors = ['#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7']
    bars = plt.bar(user_labels, user_dist, color=colors)
    print("User distribution:", user_dist)
    # plt.title('Distribution of AI-related Plugins by User Count', fontsize=18, fontweight='bold')
    plt.xlabel('Number of Users', fontsize=18)
    plt.ylabel('Number of Plugins', fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    for bar in bars:
        bar.set_edgecolor('black')
        bar.set_linewidth(1)
    
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    
    plt.tight_layout()
    plt.savefig('data/fig/users_distribution.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()
    
    plot_distribution(ai_extensions, 'category', 'Distribution of AI-related Plugins by Category', 'category_distribution.pdf')
    
    rating_ranges = [0, 1, 2, 3, 4, 5]
    rating_labels = ['0-0.9', '1-1.9', '2-2.9', '3-3.9', '4-5']
    rating_dist = [sum(1 for ext in ai_extensions if rating_ranges[i] <= ext['rating'] < rating_ranges[i+1]) for i in range(len(rating_ranges)-1)]
    
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    colors = ['#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7']
    bars = plt.bar(rating_labels, rating_dist, color=colors)
    # plt.title('Distribution of AI-related Plugins by Rating', fontsize=18, fontweight='bold')
    plt.xlabel('Rating', fontsize=18)
    plt.ylabel('Number of Plugins', fontsize=18)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    for bar in bars:
        bar.set_edgecolor('black')
        bar.set_linewidth(1)
    
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    
    plt.tight_layout()
    plt.savefig('data/fig/rating_distribution.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()
    
    plot_last_updated_distribution(ai_extensions, all_extensions)
    
    create_wordcloud([ext['title'] for ext in ai_extensions])

if __name__ == "__main__":
    main()