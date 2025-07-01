import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import pytz

# Load the dataset
df = pd.read_csv("/Users/sathwiknomula/Downloads/archive/googleplaystore.csv")

# Clean and convert columns
df['Reviews'] = pd.to_numeric(df['Reviews'].astype(str).str.replace(',', ''), errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Convert Size to MB
df['Size_MB'] = df['Size'].astype(str).str.replace('M', '').str.replace('k', '')
df['Size_MB'] = df['Size_MB'].replace('Varies with device', np.nan)
df['Size_MB'] = pd.to_numeric(df['Size_MB'], errors='coerce')

# Clean Installs
df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Drop rows with essential missing values
df.dropna(subset=['App', 'Rating', 'Reviews', 'Size_MB', 'Installs', 'Category'], inplace=True)

# Add Sentiment_Subjectivity column (dummy values for now if not present)
if 'Sentiment_Subjectivity' not in df.columns:
    df['Sentiment_Subjectivity'] = np.random.uniform(0.4, 1.0, size=len(df))  # Simulate for demo

# Allowed categories
allowed_categories = ['GAME', 'BEAUTY', 'BUSINESS', 'COMICS', 'COMMUNICATION', 'DATING', 'ENTERTAINMENT', 'SOCIAL', 'EVENT']

# Apply filters
df_filtered = df[
    (df['Rating'] > 3.5) &
    (df['Reviews'] > 500) &
    (~df['App'].str.contains('s', case=False, na=False)) &
    (df['Sentiment_Subjectivity'] > 0.5) &
    (df['Installs'] > 50000) &
    (df['Category'].str.upper().isin(allowed_categories))
].copy()

# Translate specific categories
translation_map = {
    'BEAUTY': 'सौंदर्य',
    'BUSINESS': 'வணிகம்',
    'DATING': 'Verabredung'
}
df_filtered['Translated_Category'] = df_filtered['Category'].str.upper().map(translation_map).fillna(df_filtered['Category'])

# Assign colors: pink for GAME
df_filtered['Color'] = df_filtered['Category'].apply(lambda x: 'pink' if x.upper() == 'GAME' else 'lightblue')

# Time Check: Show only between 5 PM and 7 PM IST
def is_between_5pm_and_7pm_ist():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    return now.hour >= 17 and now.hour < 19

# Use bypass for testing (remove later)
bypass = True

if is_between_5pm_and_7pm_ist() or bypass:
    fig = px.scatter(
        df_filtered,
        x='Size_MB',
        y='Rating',
        size='Installs',
        color='Translated_Category',
        hover_name='App',
        size_max=60,
        title='📱 App Size vs Rating (Bubble = Installs)',
        labels={'Size_MB': 'App Size (MB)', 'Rating': 'App Rating'}
    )

    fig.update_traces(marker=dict(line=dict(width=0.5, color='DarkSlateGrey')))
    fig.update_layout(legend_title_text='Translated Categories', height=600)
    fig.show()
else:
    print("⛔ Chart is only visible from 5 PM to 7 PM IST.")
