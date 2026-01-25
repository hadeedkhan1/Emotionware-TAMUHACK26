import cv2
import csv
import time
import math
from collections import deque
from deepface import DeepFace
import serial
import os
import requests
from dotenv import load_dotenv
from collections import Counter
import json

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

USE_ARDUINO = False  # ANOTHER SWITCH!!!! test CV model or tes w/ arduino (final version))
if USE_ARDUINO:
    COMX = "COM5"
    ser = serial.Serial(COMX, 9600, timeout=1)
    time.sleep(6)
    print("connected:", ser.is_open)


USE_PRESAGE = False  # THE SWITCH!!!!
PRESAGE_API_KEY = os.getenv("PRESAGE_API_KEY")



def presage_interpret(emotion, stability):

    if not USE_PRESAGE or PRESAGE_API_KEY is None:
        if emotion in ["sad", "angry"] and stability > 0.6:
            return "distressed", 0.3
        if emotion == "happy":
            return "positive", 0.8
        return "neutral", 0.6
    
    try:
        headers = {
            "Authorization": f"Bearer {PRESAGE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "emotion": emotion,
            "stability": stability,
            "timestamp": time.time()
        }
        r = requests.post("https://api.presagetech.com/analyze",
                          json=payload, headers=headers, timeout=1)
        if r.status_code == 200:
            data = r.json()
            return data.get("affect", "neutral"), data.get("engagement", 0.5)
    except:
        pass

    # neutral fallback
    return "neutral", 0.6


#load in fd
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)


last_arduino_send = {} 
SEND_INTERVAL = 5.0     
next_face_id = 0
faces_tracked = {}
face_emotions = {} #tracking what specifically like which ones
face_emotions_history = {}   # deque
frame_counter = 0
SMOOTHING_FRAMES = 13        # SOOTHING FRAMES 5 to 10 to 15 to 13


# fps
prev_time = time.time()

#csv log start
log_file = open("emotion_log.csv", "w", newline="")
csv_writer = csv.writer(log_file)
csv_writer.writerow(["timestamp", "face_id", "emotion"])


color_map = {
    "happy": (0, 255, 0),
    "sad": (255, 0, 0),
    "angry": (0, 0, 255),
    "surprise": (0, 255, 255),
    "neutral": (200, 200, 200),
    "fear": (128, 0, 128),
    "disgust": (0, 128, 0),
    "unknown": (255, 255, 255)
}

print("Running face + emotion tracking with smoothing...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(
        gray, 1.1, 7, minSize=(60, 60)
    )

    new_faces = {}
    frame_counter += 1

    for (x, y, w, h) in detected_faces:
        cx = x + w // 2
        cy = y + h // 2

        #?
        #mathed id
        matched_id = None
        min_dist = 60
        for fid, (px, py) in faces_tracked.items():
            dist = math.hypot(cx - px, cy - py)
            if dist < min_dist:
                matched_id = fid
                min_dist = dist

        if matched_id is None:
            matched_id = next_face_id
            next_face_id += 1

        new_faces[matched_id] = (cx, cy)

        # emotion detection every 10 frames
        if frame_counter % 10 == 0:
            try:
                face_img = frame[y:y+h, x:x+w]
                analysis = DeepFace.analyze(
                    face_img,
                    actions=["emotion"],
                    enforce_detection=False
                )
                current_emotion = analysis[0]["dominant_emotion"]
            except:
                current_emotion = "unknown"

            #smoothen with deque
            if matched_id not in face_emotions_history:
                face_emotions_history[matched_id] = deque(maxlen=SMOOTHING_FRAMES)
            face_emotions_history[matched_id].append(current_emotion)

            # recent mathematical mode
            smoothed_emotion = max(set(face_emotions_history[matched_id]), 
                                key=face_emotions_history[matched_id].count)
            face_emotions[matched_id] = smoothed_emotion



            # stability = smoothed emotion frames / all recent frames
            counts = face_emotions_history[matched_id].count(smoothed_emotion)
            stability = counts / len(face_emotions_history[matched_id])

            affect, engagement = presage_interpret(smoothed_emotion, stability)
            if USE_ARDUINO and ser and ser.is_open:
                now = time.time()
                last_time = last_arduino_send.get(matched_id, 0)
                if stability >= 0.6 and (now - last_time) >= SEND_INTERVAL:
                    ser.write(f"{smoothed_emotion}\n".encode())  # send to Arduino
                    print(f"[Face {matched_id}] Sent to Arduino: {smoothed_emotion}")
                    #CSV log
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    csv_writer.writerow([timestamp, matched_id, smoothed_emotion, affect, round(stability, 2)])
                    last_arduino_send[matched_id] = now
            else:
                now = time.time()
                last_time = last_arduino_send.get(matched_id, 0)
                if stability >= 0.6 and (now - last_time) >= SEND_INTERVAL:
                    print(f"[Face {matched_id}] Sent to File: {smoothed_emotion}")
                    #CSV log
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    csv_writer.writerow([timestamp, matched_id, smoothed_emotion, affect, round(stability, 2)])
                    last_arduino_send[matched_id] = now
    
            print(f"[Face {matched_id}] Emotion: {smoothed_emotion} | Stability: {stability:.2f}")




        # last known smoothed emotion for display
        emotion = face_emotions.get(matched_id, "detecting...")


        box_color = color_map.get(emotion, (255, 255, 255))
        cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
        label = f"ID {matched_id} | {emotion}"
        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )

        if matched_id in face_emotions_history:
            bar_x = x
            bar_y = y + h + 15
            bar_width = w
            bar_height = 10
            counts = {}
            for e in face_emotions_history[matched_id]:
                counts[e] = counts.get(e, 0) + 1
            total = sum(counts.values())
            start = bar_x
            for e, cnt in counts.items():
                w_len = int((cnt / total) * bar_width)
                cv2.rectangle(frame, (start, bar_y), (start + w_len, bar_y + bar_height), color_map.get(e, (255,255,255)), -1)
                start += w_len

    faces_tracked = new_faces

    # fps calc
    now = time.time()
    fps = int(1 / (now - prev_time))
    prev_time = now
    cv2.putText(
        frame,
        f"FPS: {fps}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )

    cv2.imshow("Face + Emotion Tracker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
log_file.close()



emotion_counts = Counter()
total_rows = 0

with open("emotion_log.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        emotion_counts[row["emotion"]] += 1
        total_rows += 1

summary_payload = {
    "total_samples": total_rows,
    "emotion_distribution": dict(emotion_counts)
}

prompt = f"""
You are analyzing anonymized emotion trend data from a single session.

Rules:
- Do NOT diagnose mental health
- Do NOT make assumptions about the person
- Be neutral, factual, and supportive
- 4–6 sentences max

Data:
{summary_payload}
"""

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",  # oopenrouter
    "X-Title": "Emotionware Hackathon"
}

data = {
    "model": "google/gemini-2.5-flash-lite",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    data=json.dumps(data),
    timeout=30
)

response.raise_for_status()
gemini_text = response.json()["choices"][0]["message"]["content"]


with open("session_summary.txt", "w") as f:
    f.write(gemini_text)
