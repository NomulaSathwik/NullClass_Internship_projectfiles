import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pytz

# Load the dataset
df = pd.read_csv("/Users/sathwiknomula/Downloads/archive/googleplaystore.csv")

# Time condition: 6 PM – 9 PM IST
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist)
if not (18 <= current_time.hour < 21):
    print("⏰ This chart is only visible between 6 PM and 9 PM IST.")
else:
    df_filtered = df.copy()

    # Drop missing 'Installs' or 'Last Updated'
    df_filtered = df_filtered.dropna(subset=['Installs', 'Last Updated'])

    # Clean 'Installs' column
    df_filtered['Installs'] = df_filtered['Installs'].astype(str).str.replace(r'[+,]', '', regex=True)
    df_filtered = df_filtered[df_filtered['Installs'].str.isnumeric()]
    df_filtered['Installs'] = df_filtered['Installs'].astype(int)

    # Parse 'Last Updated' as datetime
    df_filtered['Last Updated'] = pd.to_datetime(df_filtered['Last Updated'], errors='coerce')
    df_filtered.dropna(subset=['Last Updated'], inplace=True)
    df_filtered['Month_Year'] = df_filtered['Last Updated'].dt.to_period('M')

    # Filter by Reviews
    df_filtered['Reviews'] = pd.to_numeric(df_filtered['Reviews'], errors='coerce')
    df_filtered = df_filtered[df_filtered['Reviews'] > 500]

    # Remove Apps starting with X/Y/Z or containing 's'
    df_filtered = df_filtered[~df_filtered['App'].str.lower().str.startswith(('x', 'y', 'z'))]
    df_filtered = df_filtered[~df_filtered['App'].str.contains('s', case=False, na=False)]

    # Keep categories starting with B, C, or E
    df_filtered = df_filtered[df_filtered['Category'].str.upper().str.startswith(('B', 'C', 'E'))]

    # Translate category names
    category_translations = {
        'BEAUTY': 'सौंदर्य',
        'BUSINESS': 'வணிகம்',
        'DATING': 'Partnersuche'
    }

    df_filtered['Category_Translated'] = df_filtered['Category'].apply(
        lambda x: category_translations.get(str(x).upper(), x)
    )

    # Aggregate installs by Month-Year and Category
    df_grouped = df_filtered.groupby(['Month_Year', 'Category_Translated'])['Installs'].sum().reset_index()
    df_grouped['Month_Year'] = df_grouped['Month_Year'].astype(str)
    df_grouped.sort_values(by=['Category_Translated', 'Month_Year'], inplace=True)

    # Compute MoM growth
    df_grouped['Growth'] = df_grouped.groupby('Category_Translated')['Installs'].pct_change()

    # Plotting
    plt.figure(figsize=(14, 7))
    sns.set(style="whitegrid")

    for category in df_grouped['Category_Translated'].unique():
        data = df_grouped[df_grouped['Category_Translated'] == category]
        plt.plot(data['Month_Year'], data['Installs'], label=category)

        # Fill area with growth > 20%
        high_growth = data['Growth'] > 0.2
        plt.fill_between(
            data['Month_Year'], data['Installs'],
            where=high_growth, alpha=0.3, label=f'{category} >20% growth'
        )

    plt.xticks(rotation=45)
    plt.xlabel('Month-Year')
    plt.ylabel('Total Installs')
    plt.title('📈 Monthly Install Trends by Category (with >20% Growth Highlighted)')
    plt.legend(title='App Categories')
    plt.tight_layout()
    plt.show()
