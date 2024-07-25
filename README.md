
This project combines a game with emotion detection, using OpenCV and the MobileNet model to analyze players' emotional states during gameplay. Here's an overview of the key components:

1. Game Interface:
   - Implemented using Pygame 

2. Emotion Detection:
   - Uses OpenCV for image processing and face detection
   - Employs the MobileNet model for emotion classification
   - Detects emotions like sadness, happiness, anger, surprise, and fear in real-time

3. Data Collection:
   - Records emotion intensities in "timestamps_and_frames.csv"
   - Captures video frames during gameplay, focusing on moments of anger

4. Post-Game Analysis:
   - Generates emotion graphs from collected data
   - Displays frames showing angry expressions

5. Web Interface:
   - Uses HTML templates, CSS, and JavaScript for result presentation

6. Project Goal:
   - Increase emotional self-awareness during gaming
   - Encourage anger management by visualizing emotional responses

OpenCV plays a crucial role in this project, likely handling tasks such as:
- Real-time video capture from the user's camera
- Face detection in video frames
- Image preprocessing before emotion classification
- Potentially assisting in frame analysis and selection for the anger detection feature

TO RUN THE PROJECT 
cd cosmic-heat-pygame
python -m venv env
./env/Scripts/activate
pip install -r requirements.txt
cd ..
python app.py

https://github.com/user-attachments/assets/17414707-f252-41da-809a-f542da28da88

