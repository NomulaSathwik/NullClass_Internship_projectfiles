#task2
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz


df = pd.read_csv("/Users/sathwiknomula/Downloads/archive/googleplaystore.csv")  # use your dataset path
df.dropna(subset=['Installs', 'Size', 'Android Ver', 'Content Rating', 'App'], inplace=True)

# Convert installs and size
df['Installs'] = df['Installs'].str.replace('[+,]', '', regex=True).astype(int)
df['Size'] = df['Size'].replace('Varies with device', pd.NA)

# Convert size to MB
def convert_size(size):
    if isinstance(size, str) and 'M' in size:
        return float(size.replace('M', ''))
    elif isinstance(size, str) and 'k' in size:
        return float(size.replace('k', '')) / 1024  # convert KB to MB
    else:
        return pd.NA

df['Size'] = df['Size'].apply(convert_size)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# Simulate revenue (if not available in dataset)
import numpy as np
df['Revenue'] = df['Installs'] * np.where(df['Type'] == 'Paid', 0.5, 0)  # assume 0.5$ per paid install


# Apply conditions
filtered_df = df[
    (df['Installs'] >= 10000) &
    (df['Revenue'] >= 10000) &
    (df['Android Ver'].str.extract(r'(\d+\.?\d*)')[0].astype(float) > 4.0) &
    (df['Size'] > 15) &
    (df['Content Rating'] == 'Everyone') &
    (df['App'].str.len() <= 30)
]


top_categories = (
    filtered_df.groupby('Category')['Installs']
    .sum()
    .sort_values(ascending=False)
    .head(3)
    .index.tolist()
)

df_top = filtered_df[filtered_df['Category'].isin(top_categories)]


grouped = df_top.groupby(['Category', 'Type']).agg({
    'Installs': 'mean',
    'Revenue': 'mean'
}).reset_index()


def is_between_1pm_and_2pm_ist():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    return now.hour == 13  # 13 means 1 PM IST


if is_between_1pm_and_2pm_ist():
    print("✅ It's 1–2 PM IST — display chart here")
    # Add your plotting code here
else:
    print("❌ This chart is only visible between 1 PM and 2 PM IST.")


if is_between_1pm_and_2pm_ist():
    fig = go.Figure()

    for category in top_categories:
        for app_type in ['Free', 'Paid']:
            data = grouped[(grouped['Category'] == category) & (grouped['Type'] == app_type)]

            fig.add_trace(go.Bar(
                x=[f"{category} ({app_type})"],
                y=data['Installs'],
                name=f"{category} ({app_type}) - Installs",
                yaxis='y1'
            ))

            fig.add_trace(go.Scatter(
                x=[f"{category} ({app_type})"],
                y=data['Revenue'],
                mode='lines+markers',
                name=f"{category} ({app_type}) - Revenue",
                yaxis='y2'
            ))

    fig.update_layout(
        title="Avg Installs vs Revenue for Free vs Paid Apps (Top 3 Categories)",
        yaxis=dict(title='Avg Installs'),
        yaxis2=dict(title='Avg Revenue', overlaying='y', side='right'),
        xaxis=dict(title='App Type by Category'),
        legend=dict(orientation='h'),
        width=1000,
        height=600
    )

    fig.show()
else:
    print("❌ This chart is only visible between 1 PM and 2 PM IST.")





