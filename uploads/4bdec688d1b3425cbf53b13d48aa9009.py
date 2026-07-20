import pandas as pd
import subprocess

# Read CSV
df = pd.read_csv("job.csv")

# Get URLs from Career Website column
urls = (
    df["Career Website"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)

# Remove empty strings
urls = [url for url in urls if url]

if not urls:
    print("No URLs found.")
    exit()

# Path to Thorium executable
thorium_path = r"C:\Users\nishad\AppData\Local\Thorium\Application\thorium.exe"

# Open all URLs in a single Thorium window with multiple tabs
subprocess.Popen([thorium_path] + urls)

print(f"Opened {len(urls)} URLs in Thorium.")



