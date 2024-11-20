
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from email.message import EmailMessage
from flask import send_from_directory
from io import BytesIO
import base64
import ssl
from matplotlib.ticker import MultipleLocator, FuncFormatter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'my super secret key'.encode('utf8')  # Replace with a strong secret key

# MongoDB client setup
client = MongoClient('mongodb://localhost:27017/')
db = client['emotracker_db']
users_collection = db['users']
emotion_collection = db['emotions']

EMAIL_SENDER = 'aryanarora5167@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'kywq bqmu rwpp rfar'  # Replace with your email password

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user in the database
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id']) 
            session['username'] = username  # Set session for the logged-in user
            with open('user_id.txt', 'w') as f:
                f.write(session['user_id'])
            print(f"Logged in as: {session.get('username')}")  # Debugging line
            print(f"{session.get('user_id')}")
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
            return "Email already exists. Please use a different one."

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

def send_email(receiver_email, subject, body):
    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = receiver_email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, receiver_email, em.as_string())
# Route to log out the user
@app.route('/logout')
def logout():
    if 'username' in session:   
        username = session.pop('username')  # User email
        user_id = session.get('user_id')
        
        if user_id is None:
            return redirect(url_for('login'))
        # Generate a report from the session data
        # emotions = list(emotion_collection.find({'user_id': session.get('user_id')}, {'_id': 0}))
        user_csv_file = f'emotion_detection_{user_id}.csv'
        # if not emotions:
        #     return "No emotions recorded for this session."

        if os.path.exists(user_csv_file):
            # Read the CSV file and analyze the most frequent emotion
            emotion_df = pd.read_csv(user_csv_file)

            if emotion_df.empty:
                return "No emotions recorded for this session."

            # Find the most frequent emotion
            most_frequent_emotion = emotion_df['emotion'].mode()[0]
            frequency = emotion_df['emotion'].value_counts()[most_frequent_emotion]

            # Email content
            subject = "Your Emotion Detection Report"
            body = (
                f"Hello {username},\n\n"
                f"Thank you for using Emotracker!\n\n"
                f"Here is your session summary:\n"
                f"Most Frequent Emotion: {most_frequent_emotion}\n"
                f"Times Recorded: {frequency}\n\n"
                f"Best Regards,\nThe Emotracker Team"
            )

            # Send email
            send_email(username, subject, body)
            print(f"Report sent to {username} with most frequent emotion: {most_frequent_emotion}")

        # Clear the user session
        session.pop('user_id', None)

        return f"Report sent to {username} with most frequent emotion: {most_frequent_emotion}."
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
df = pd.read_csv('D:/backup_minor/emotion_detection.csv')

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
    df = pd.read_csv('D:/backup_minor/emotion_detection.csv')

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


@app.route('/frames/<path:filename>')
def frames(filename):
    return send_from_directory('frames', filename)


@app.route('/angry_frames')
def angry_frames():
    emotion_data_file = 'emotion_detection.csv'
    emotion_data_df = pd.read_csv(emotion_data_file)

    # Filter rows where emotion is 'angry'
    angry_data = emotion_data_df[emotion_data_df['emotion'] == 'angry']

    # Load timeframe CSV
    timeframe_file = 'timestamps_and_frames.csv'
    timeframe_df = pd.read_csv(timeframe_file)

    try:
        # Create a dictionary mapping timestamps to frame paths
        timestamp_frame_mapping = dict(zip(timeframe_df['Timestamp'], timeframe_df['Frame Path']))

        # Find the 4 closest frame paths corresponding to 'angry' timestamps
        angry_frame_paths = []

        for angry_timestamp in angry_data['timestamp']:
            closest_timestamps = sorted(timestamp_frame_mapping.keys(), key=lambda x: abs(pd.to_datetime(x) - pd.to_datetime(angry_timestamp)))[:4]
            closest_frame_paths = [timestamp_frame_mapping[closest_timestamp] for closest_timestamp in closest_timestamps]
            angry_frame_paths.append(closest_frame_paths)

        # Create a list of image paths
        image_paths = [frame_path.replace('frames/', '') for frame_path in angry_frame_paths[0]]

        # Render HTML template with image paths
        return render_template('angry_frames.html', image_paths=image_paths)

    except KeyError as e:
        # Handle the case where the 'Frame Path' column is not present in the dataframe
        error_message = f"KeyError: {e}. Please check if 'Frame Path' column is present in timestamps_and_frames.csv."
        return render_template('error.html', error_message=error_message)



if __name__ == '__main__':
    app.run(debug=True)
