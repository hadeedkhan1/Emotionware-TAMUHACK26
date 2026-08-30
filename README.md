## Inspiration

We learned how critical data smoothing and stability thresholds are for real-time predictions. We also learned a lot about combining software and hardware feedback in a meaningful way. Beyond the technical side, we realized how important it is to iterate quickly, test often, and keep the user experience in mind, even in a hackathon setting. Stanford, Google, and Meta all have tried to do something similar in the past without much success.

## What it does

Our system tracks emotions in real time using a webcam using DeepFace and Presage SDK (which will be Meta RayBans Smart Glasses in the Future), detects and assigns IDs to multiple faces, predicts their emotional state, and logs everything to a CSV. At the end of a session, the system sends the data to Google Gemini via OpenRouter to generate a clear, human-readable summary onto a secure dashboard.

We also integrated wearable feedback. Using a glove, bracelet, ring, or even a smartwatch, the system can send subtle vibrations corresponding to detected emotions. The feedback is haptic and customizable, so it could work in multiple form factors depending on the user’s needs.

Finally, the web dashboard reads the CSV and displays a live session overview: dominant emotion, stability, and an AI-generated summary. You can even track trends over time, making it a powerful tool for both personal and educational use.

## How we built it

We built the system in layers:

* **Computer Vision & Emotion Tracking:** OpenCV detects faces while DeepFace and Presage SDK predict emotions. Each face gets a consistent ID across frames, and a deque smooths predictions to reduce jitter.
* **Data Logging & AI Summary:** Stable predictions are logged to CSV. After the session, the data is sent to OpenRouter using Google Gemini 2.5 Flash, producing a neutral, factual, and supportive summary of emotional trends.
* **Wearable Haptic Feedback:** We started with coin motors on a glove, but the first iteration didn’t work — they were inconsistent and weak. We redesigned the system to use a single strong motor with tuned signals. The wearable could also be adapted to a ring, watch, or other form factors.
* **Web Dashboard:** The dashboard reads the CSV, calculates dominant emotions and average stability, and displays the AI summary. It’s visually intuitive and works in real time for quick analysis.
* **Optional Presage Integration:** For users with access, Presage can be used to further interpret emotions and engagement, adding an extra layer of intelligence to the analysis.

## Challenges we ran into

* **Stability:** Raw emotion predictions fluctuate heavily frame to frame. Without smoothing, the data was noisy and unreliable.
* **Hardware feedback:** The coin motors didn’t work on the first try. They came broken and we had to solder new connections ourselves. We had to rethink the design, using a single stronger coin motor and tuning signals for meaningful haptic feedback.
* **Hackathon time constraints:** Integrating computer vision, AI summaries, wearables, and a live dashboard all in one session was ambitious. We had to prioritize features that mattered most for a functional demo.

## Accomplishments that we're proud of

* Built a real-time emotion tracking system with AI-generated summaries.
* Created a wearable feedback system that can be adapted to a glove, ring, watch, or any other device.
* Learned a lot about autism and emotional interpretation, making the project meaningful beyond coding.
* Successfully integrated Presage, Gemini, CSV logging, and a web dashboard in a single system.
* Turned a broken hardware setup into something that actually works for live haptic feedback.

## What we learned

* Real-time emotion tracking is tricky; smoothing and thresholds are essential.
* Hardware feedback design takes testing and iteration; the first solution rarely works.
* Talking to real educators and learning about autism made us understand why this system matters.
* Integrating software and hardware teaches you to balance ambition with practicality.

  <img width="761" height="573" alt="image" src="https://github.com/user-attachments/assets/f0919859-7061-473c-962b-cadc04de9998" />
