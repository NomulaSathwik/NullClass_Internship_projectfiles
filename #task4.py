import pandas as pd
import plotly.express as px
import pycountry
import pytz
import random
from datetime import datetime

# Load dataset
df = pd.read_csv("/Users/sathwiknomula/Downloads/archive/googleplaystore.csv")
df.columns = df.columns.str.strip().str.lower()

# Add random countries
country_list = ['India', 'United States', 'Germany', 'France', 'Brazil', 'Japan', 'Australia', 'Canada', 'Mexico', 'Russia']
df['country'] = [random.choice(country_list) for _ in range(len(df))]

# Debug: Check columns
print("✅ Columns loaded:", df.columns.tolist())

if 'category' in df.columns and 'installs' in df.columns:
    df_filtered = df[~df['category'].astype(str).str.startswith(('A', 'C', 'G', 'S'))]
    df_filtered = df_filtered.dropna(subset=['category', 'installs'])
    df_filtered['installs'] = df_filtered['installs'].astype(str).str.replace('[+,]', '', regex=True)
    df_filtered = df_filtered[df_filtered['installs'].str.isnumeric()]
    df_filtered['installs'] = df_filtered['installs'].astype(int)

    top5_categories = (
        df_filtered.groupby('category')['installs']
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index
    )

    df_top5 = df_filtered[df_filtered['category'].isin(top5_categories)]
    print("✅ Step 3 completed successfully.")

else:
    print("❌ Column 'category' or 'installs' not found.")
    exit()

# Group by country and category
df_grouped = df_top5.groupby(['country', 'category'])['installs'].sum().reset_index()

# Add ISO codes
def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

df_grouped['iso_alpha'] = df_grouped['country'].apply(get_country_code)

# Debug: Check data
print("✅ Grouped data:", df_grouped.head())

# Time filter (or bypass for testing)
def is_between_6pm_and_8pm_ist():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist).time()
    return datetime.strptime("18:00", "%H:%M").time() <= now <= datetime.strptime("20:00", "%H:%M").time()

bypass = True

# Plot
if is_between_6pm_and_8pm_ist() or bypass:
    fig = px.choropleth(
        df_grouped,
        locations='iso_alpha',
        color='installs',
        hover_name='country',
        animation_frame='category',
        color_continuous_scale='Viridis',
        title='🌍 Global Installs by App Category (Top 5 Only)'
    )
    fig.update_geos(showcountries=True, showcoastlines=True, projection_type="natural earth")
    fig.update_layout(height=600)
    fig.show()
else:
    print("⏳ This chart is only visible between 6 PM and 8 PM IST.")
