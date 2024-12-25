# visualize_logs.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

log_file = "rate_limit_log.csv"
df = pd.read_csv(log_file)

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Minute'] = df['Timestamp'].dt.floor('min')

# Normalize 'Status' by mapping any 'throttled*' to 'throttled'
df['Status'] = df['Status'].apply(lambda x: 'throttled' if 'throttled' in x else x)

time_series = df.groupby(['Minute', 'API Name', 'Status']).size().reset_index(name='Count')
pivot_time = time_series.pivot_table(index=['Minute', 'API Name'], columns='Status', values='Count', fill_value=0).reset_index()

bar_data = df.groupby(['API Name', 'Status']).size().reset_index(name='Count')
pivot_bar = bar_data.pivot(index='API Name', columns='Status', values='Count').fillna(0)

pivot_bar.plot(kind='bar', figsize=(10, 6))
plt.title('Allowed vs Throttled API Calls per Exchange')
plt.xlabel('API Name')
plt.ylabel('Number of Calls')
plt.xticks(rotation=0)
plt.legend(title='Status')
plt.tight_layout()
plt.show()
