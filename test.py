# import re
# import matplotlib.pyplot as plt
# from wordcloud import WordCloud
# from collections import Counter
# from nltk.corpus import stopwords
# import nltk

# # Download stopwords if not already downloaded
# nltk.download('stopwords', quiet=True)

# # Sample YouTube comments
# comments = [
#     "This video is amazing! Loved the editing.",
#     "Great content, keep it up!",
#     "Not a fan of this, could be better.",
#     "Wow, the quality is superb!",
#     "This is boring, I didn’t like it.",
#     "Awesome video, very informative.",
#     "I love this channel, always great videos!",
#     "The music is too loud, I couldn't hear the speaker."
# ]

# # 🔹 Step 1: Preprocess comments (remove punctuation, stopwords, etc.)
# stop_words = set(stopwords.words("english"))

# def clean_text(text):
#     text = re.sub(r'\W+', ' ', text.lower())  # Remove special characters & lowercase
#     words = [word for word in text.split() if word not in stop_words]  # Remove stopwords
#     return " ".join(words)

# cleaned_comments = [clean_text(comment) for comment in comments]

# # 🔹 Step 2: Create a Word Cloud
# wordcloud_text = " ".join(cleaned_comments)
# word_counts = Counter(wordcloud_text.split())
# print(word_counts.most_common(10))  # Show top 10 words

# *****************Text Emotion detection*****************
# from transformers import pipeline

# # Load a pre-trained emotion detection model
# emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# # Test with example sentences
# texts = [
#     "I am a software developer", 
#     "I feel really sad and depressed.", 
#     "I am so angry at this!", 
#     "Wow, that was a big surprise!", 
#     "I love this song!", 
#     "I am scared of the dark."
# ]

# # Get emotion predictions
# results = emotion_classifier(texts)

# # Print results
# for text, result in zip(texts, results):
#     print(f"Text: {text} -> Emotion: {result['label']}, Score: {result['score']:.2f}")


# **********************Train model on facial expression dataset using YOLO **********************
from ultralytics import YOLO
from transformers import pipeline

classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
def text_emotion(text):
    result = classifier(text)

    # Print results
    # for emotion in result[0]:
    print(result)


if __name__ == "__main__":
    # model = YOLO("yolov8n.pt")
    # model.train(data="C:\Projects\my-web\dataset\YOLO_format\data.yaml", epochs=10, imgsz=640, batch=16, device='cuda')

    # model = YOLO("C:/Projects/my-web/runs/detect/train/weights/best.pt")
    # images = ['happy.jpg', 'sad.jpg', 'anger.jpg', 'surprise.jpg', 'neutral.jpg', 'disgust.jpg', 'fear.jpg']
    # # results = model('fear.jpg')
    # import cv2
    # from deepface import DeepFace

    # # Load face cascade classifier
    # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # for img in images:
    #     frame = cv2.imread(img)
    #     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
    #     faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    #     for (x, y, w, h) in faces:
    #         face_roi = rgb_frame[y:y + h, x:x + w]
    #     result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
    #     print('Result:', result[0]['dominant_emotion'])

    # Start capturing video
    # cap = cv2.VideoCapture(0)

    # while True:
    #     # Capture frame-by-frame
    #     ret, frame = cap.read()

    #     # Convert frame to grayscale
    #     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #     # Convert grayscale frame to RGB format
    #     rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

    #     # Detect faces in the frame
    #     faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    #     for (x, y, w, h) in faces:
    #         # Extract the face ROI (Region of Interest)
    #         face_roi = rgb_frame[y:y + h, x:x + w]


    #         # Perform emotion analysis on the face ROI
    #         result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)

    #         # Determine the dominant emotion
    #         emotion = result[0]['dominant_emotion']

    #         # Draw rectangle around face and label with predicted emotion
    #         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #         cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    #     # Display the resulting frame
    #     cv2.imshow('Real-time Emotion Detection', frame)

    #     # Press 'q' to exit
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # # Release the capture and close all windows
    # cap.release()
    # cv2.destroyAllWindows()
    
    # while True:
    #     command = input('Ask a question: ')
    #     result = text_emotion(command)
    print('ajay'.capitalize())
