from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64

app = Flask(_name_)

# Step 1: Read the CSV File
df = pd.read_csv('D:\emotion_detection.csv')

# Step 2: Perform Analysis
avg_intensity_by_emotion = df.groupby('emotion')['Intensity'].mean()
count_by_emotion = df.groupby('emotion')['emotion'].count()
summary_stats = df.groupby('emotion').describe()

# Function to generate scatter plot and return base64 encoded image
def generate_scatter_plot():
    plt.figure(figsize=(10, 6))
    for emotion, data in df.groupby('emotion'):
        plt.scatter(data['timestamp'], data['Intensity'], label=emotion, alpha=0.7)

    plt.title('Scatter Plot of Timestamp vs Intensity for Different Emotions')
    plt.xlabel('Timestamp')
    plt.ylabel('Intensity')
    plt.legend()

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
    plt.figure(figsize=(8, 4))
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

# Define Flask routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/plots')
def plots():
    # Generate and get the base64 encoded images
    scatter_plot_image = generate_scatter_plot()
    avg_intensity_plot_image = generate_bar_plot(avg_intensity_by_emotion, 'Average Intensity by Emotion', 'Emotion', 'Average Intensity')
    count_plot_image = generate_bar_plot(count_by_emotion, 'Count by Emotion', 'Emotion', 'Count')

    return render_template('plots.html', scatter_plot_image=scatter_plot_image,
                           avg_intensity_plot_image=avg_intensity_plot_image,
                           count_plot_image=count_plot_image)

if _name_ == '_main_':
    app.run(debug=True)