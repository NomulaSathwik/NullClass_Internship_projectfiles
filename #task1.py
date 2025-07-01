#task1.nullclass

import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

file_path = '/Users/sathwiknomula/Downloads/archive/googleplaystore_user_reviews.csv'
df = pd.read_csv(file_path)

filtered_df = df[(df['Sentiment'] == 'Positive') & df['Translated_Review'].notna()]
filtered_df = filtered_df[filtered_df['Translated_Review'].astype(str).str.strip() != ""]


text = " ".join(filtered_df['Translated_Review'].astype(str))

custom_stopwords = set(STOPWORDS)
custom_stopwords.update(['app', 'apps', 'game', 'play', 'really', 'get'])  # You can update more as needed



wordcloud = WordCloud(stopwords=custom_stopwords,
                      background_color='white',
                      width=800,
                      height=400).generate(text)

plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Word Cloud of Positive User Reviews", fontsize=18)
plt.show()



