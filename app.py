
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64
from matplotlib.ticker import MultipleLocator, FuncFormatter

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'my super secret key'.encode('utf8')  # Replace with a strong secret key

# MongoDB client setup
client = MongoClient('mongodb://localhost:27017/')  # Adjust connection string as needed
db = client['emotracker_db']  # Database name
users_collection = db['users']  # Collection for user data


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user in the database
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username  # Set session for the logged-in user
            print(f"Logged in as: {session.get('username')}")  # Debugging line
            return redirect(url_for('index'))
        else:
            return "Invalid username or password. Please try again."
    return render_template('login.html')


# Route for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        if users_collection.find_one({'username': username}):
            return "Username already exists. Please choose a different one."

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for main index page (after login)
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('index.html', username=session['username'])

# Route to log out the user
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Python script execution route (unchanged from original)
@app.route('/run-main-script', methods=['POST'])
def run_python_script():
    try:
        main_process = subprocess.Popen(['python', 'main/main.py'])
        cosmic_heat_process = subprocess.Popen(['python', 'main.py'], cwd='cosmic-heat-pygame')

        # Wait for both processes to finish
        main_process.wait()
        cosmic_heat_process.wait()

        return jsonify({'status': 'success', 'message': 'Python script executed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Function to generate scatter plot
df = pd.read_csv('C:/Users/brij_/backup_minor/emotion_detection.csv')

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
    df = pd.read_csv('C:/Users/brij_/backup_minor/emotion_detection.csv')

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
