import os
import cv2
import numpy as np
from tensorflow import keras
from keras.preprocessing import image
from keras.preprocessing.image import load_img, img_to_array 
from keras.models import  load_model
import calendar
from datetime import datetime
import openpyxl
import warnings
warnings.filterwarnings("ignore")
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import time

def write_to_csvhead(file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #time.sleep(1)
        # Write header
        csv_writer.writerow(['timestamp', 'Intensity', 'emotion'])



def write_to_csv(file_path, data):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #time.sleep(1)
        # Write header
            #csv_writer.writerow(['timestamp', 'Intensity', 'emotion'])
        # Write data
        csv_writer.writerows(data)

# load model
model = load_model("best_model.h5")  

face_haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
file_path1='test2.csv'
write_to_csvhead(file_path1)
emotion_data = {emotion: {'timestamps': [], 'intensities': []} for emotion in ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']}
while True:

    ret, test_img = cap.read()  # captures frame and returns boolean value and captured image
    if not ret:
        continue
    gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)

    faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)

    for (x, y, w, h) in faces_detected:
        cv2.rectangle(test_img, (x, y), (x + w, y + h), (255, 0, 0), thickness=7)
        roi_gray = gray_img[y:y + w, x:x + h]  # cropping region of interest i.e. face area from  image
        roi_gray = cv2.resize(roi_gray, (224, 224))
        img_pixels = image.img_to_array(roi_gray)
        img_pixels = np.expand_dims(img_pixels, axis=0)
        img_pixels /= 255

        predictions = model.predict(img_pixels)
       
        # find max indexed array
        max_index = np.argmax(predictions[0])

        emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
        predicted_emotion = emotions[max_index]

        emotion_data[predicted_emotion]['timestamps'].append(datetime.now())
        emotion_data[predicted_emotion]['intensities'].append(np.max(predictions[0]))

        # Your recursive data structure (example)
        data_to_write = [
            (datetime.now(), np.max(predictions[0]), predicted_emotion)
        ]
        # Specify the file path
        file_path = 'test2.csv'
        # Call the function to write data to the CSV file
        write_to_csv(file_path, data_to_write)

        cv2.putText(test_img, predicted_emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    resized_img = cv2.resize(test_img, (1000, 700))
    cv2.imshow('Facial emotion analysis ', resized_img)

    if cv2.waitKey(10) == ord('q'):  # wait until 'q' key is pressed
        break


cap.release()
cv2.destroyAllWindows

# Create lists for true and predicted labels
true_labels = []
predicted_labels = []

# Populate true and predicted labels
for emotion in emotion_data:
    true_labels.extend([emotion] * len(emotion_data[emotion]['timestamps']))
    predicted_labels.extend([emotion] * len(emotion_data[emotion]['timestamps']))

# Create a confusion matrix
cm = confusion_matrix(true_labels, predicted_labels, labels=list(emotion_data.keys()))

# Normalize the confusion matrix for better visualization
cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

# Create a heatmap
sns.set(font_scale=1.2)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt=".2f", cmap="Blues", xticklabels=list(emotion_data.keys()), yticklabels=list(emotion_data.keys()))
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()