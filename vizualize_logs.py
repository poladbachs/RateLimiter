# visualize_logs.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def visualize_logs(log_file="rate_limit_log.csv"):
    # Load logs
    df = pd.read_csv(log_file)
    
    # Convert Timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Sort by Timestamp
    df.sort_values('Timestamp', inplace=True)
    
    # Add a column for throttled calls
    df['Throttled'] = df['Status'].apply(lambda x: 1 if 'throttled' in x else 0)
    
    # Create separate dataframes for allowed and throttled
    allowed = df[df['Throttled'] == 0]
    throttled = df[df['Throttled'] == 1]
    
    # Plotting
    plt.figure(figsize=(15, 7))
    
    # Plot allowed calls
    plt.scatter(allowed['Timestamp'], allowed['API Name'], color='green', label='Allowed', alpha=0.6)
    
    # Plot throttled calls
    plt.scatter(throttled['Timestamp'], throttled['API Name'], color='red', label='Throttled', alpha=0.6)
    
    plt.title('API Call Status Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('API Name / Thread')
    plt.legend()
    plt.grid(True)
    
    # Improve x-axis formatting
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_logs()