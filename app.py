import requests
import json
import gunicorn
from urllib.parse import urlparse
import time
from flask import Flask, request, render_template, send_file



app = Flask(__name__)

def fetch_all_data(base_url, video_id, duration, interval=300):
    session = requests.Session()
    all_data = []
    time_ranges = [(i, i + interval) for i in range(0, duration, interval)]
    
    for start_time, end_time in time_ranges:
        nonce = int(time.time() * 1000)
        url = f"{base_url}/userajax.php?c=history&m={video_id}&f={start_time}&t={end_time}&format=json&__n={nonce}&b=0&l=50"
        
        response = session.get(url)
        if response.status_code == 200:
            all_data.append(response.json())
        else:
            print(f"Failed to fetch data for range {start_time}-{end_time}: {response.status_code}")
            break
        time.sleep(0.5)  # To avoid hitting the server too frequently
    
    return all_data

def main(url):
    parsed_url = urlparse(url)
    video_id = parsed_url.path.split('/')[-1]
    base_url = f"https://{parsed_url.netloc}"
    
    # Assuming a maximum video duration of 8 hours (28800 seconds)
    video_duration = 28800
    
    all_data = fetch_all_data(base_url, video_id, video_duration)
    
    # Save fetched data to file
    with open("all_fetched_data.json", "w") as f:
        json.dump(all_data, f, indent=2)

    return "all_fetched_data.json"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        data_file = main(url)
        return send_file(data_file, as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
