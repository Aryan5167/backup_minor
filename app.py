from flask import Flask, render_template, jsonify
import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64
from matplotlib.ticker import MultipleLocator,FuncFormatter

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-main-script', methods=['POST'])
def run_python_script():
    try:
        # Execute your Python script (replace 'your_script.py' with the actual name)
        # subprocess.run(['python', 'main/main.py'])
         
        # # subprocess.run(['python', 'cosmic-heat-pygame/main.py'])
        # subprocess.run(['python', 'main.py'], cwd='cosmic-heat-pygame')
        main_process = subprocess.Popen(['python', 'main/main.py'])

        # Set the working directory to 'cosmic-heat-pygame' and then execute main.py
        cosmic_heat_process = subprocess.Popen(['python', 'main.py'], cwd='cosmic-heat-pygame')

        # Wait for both processes to finish
        main_process.wait()
        cosmic_heat_process.wait()
        

        return jsonify({'status': 'success', 'message': 'Python script executed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


df = pd.read_csv('D:\minor_project\emotion_detection.csv')

def format_timestamp(value , _):
    return pd.to_datetime(value, unit='s').strftime('%H:%M:%S')


def generate_scatter_plot():
    plt.figure(figsize=(10, 6))
    for emotion, data in df.groupby('emotion'):
        plt.scatter(data['timestamp'], data['Intensity'], label=emotion, alpha=0.7)

    plt.title('Scatter Plot of Timestamp vs Intensity for Different Emotions')
    plt.xlabel('Timestamp')
    plt.ylabel('Intensity')
    plt.legend()

    plt.xticks(rotation =45 , ha='right')
    plt.gca().xaxis.set_major_locator(MultipleLocator(10))
    plt.gca().xaxis.set_major_formatter(FuncFormatter(format_timestamp))
    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Encode the image to base64 for embedding in HTML
    img_base64 = base64.b64encode(img.getvalue()).decode()

    return img_base64

# Function to generate bar plot and return base64 encoded image
def generate_bar_plot(data, title, xlabel, ylabel):
    plt.figure(figsize=(8, 6))
    data.plot(kind='bar', color='skyblue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Encode the image to base64 for embedding in HTML
    img_base64 = base64.b64encode(img.getvalue()).decode()

    return img_base64


@app.route('/plots')
def plots():
    # Generate and get the base64 encoded images
    df = pd.read_csv('D:\minor_project\emotion_detection.csv')

    avg_intensity_by_emotion = df.groupby('emotion')['Intensity'].mean()
    count_by_emotion = df.groupby('emotion')['emotion'].count()
    
    # summary_stats_table=generate_summary_stats_table()

    scatter_plot_image = generate_scatter_plot()
    avg_intensity_plot_image = generate_bar_plot(avg_intensity_by_emotion, 'Average Intensity by Emotion', 'Emotion', 'Average Intensity')
    count_plot_image = generate_bar_plot(count_by_emotion, 'Count by Emotion', 'Emotion', 'Count')

    return render_template('plots.html', scatter_plot_image=scatter_plot_image,
                           avg_intensity_plot_image=avg_intensity_plot_image,
                           count_plot_image=count_plot_image)
                        #    summary_stats_table= summary_stats_table)

if __name__ == '__main__':
    app.run(debug=True)
