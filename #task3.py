import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# Step 1: Load the dataset
df = pd.read_csv("/Users/sathwiknomula/Downloads/archive/googleplaystore.csv")

# Step 2: Check time condition (3 PM – 5 PM IST)
def is_between_3pm_and_5pm_ist():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    return now.hour == 15 or now.hour == 16

# Step 3: Data cleaning and filtering
df_filtered = df.copy()

# Clean 'Size' column to MB
df_filtered['Size_MB'] = df_filtered['Size'].apply(lambda x: float(str(x).replace('M', '')) if 'M' in str(x) else None)

# Parse 'Last Updated' to datetime and extract month
df_filtered['Last_Updated'] = pd.to_datetime(df_filtered['Last Updated'], errors='coerce')
df_filtered['Update_Month'] = df_filtered['Last_Updated'].dt.month

# Convert Reviews to numeric (if not already)
df_filtered['Reviews'] = pd.to_numeric(df_filtered['Reviews'], errors='coerce')

# Apply filters
df_filtered = df_filtered[
    (df_filtered['Rating'] >= 4.0) &
    (df_filtered['Size_MB'] >= 10) &
    (df_filtered['Update_Month'] == 1)
]

# Step 4: Group and aggregate
grouped = df_filtered.groupby('Category').agg({
    'Rating': 'mean',
    'Reviews': 'sum',
    'Installs': 'sum'
}).reset_index()

# Get top 10 categories by Installs
top_10_categories = grouped.sort_values(by='Installs', ascending=False).head(10)

# Step 5: Plot only between 3 PM and 5 PM IST
if is_between_3pm_and_5pm_ist():
    fig = go.Figure(data=[
        go.Bar(name='Avg Rating', x=top_10_categories['Category'], y=top_10_categories['Rating']),
        go.Bar(name='Total Reviews', x=top_10_categories['Category'], y=top_10_categories['Reviews'])
    ])

    fig.update_layout(
        barmode='group',
        title='Average Rating and Total Reviews by Top 10 Categories (3 PM – 5 PM)',
        xaxis_title='App Category',
        yaxis_title='Values',
        width=1000,
        height=600
    )
    fig.show()
else:
    print("❌ This chart is only visible between 3 PM and 5 PM IST.")
