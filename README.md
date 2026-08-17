**EE 782 — Advanced Topics in Machine Learning, IIT Bombay**

**Guide:** Prof. Amit Sethi

# Room Guard Agent

A voice-activated room security system combining real-time webcam monitoring, dlib-based face recognition, Google ASR, Windows SAPI TTS, and rule-based intruder escalation.

## Features

* **Voice Activation:** Activates/deactivates Protect Mode using voice commands via `SpeechRecognition` + Google ASR.
* **Face Recognition:** Matches webcam faces against trusted dlib embeddings using a configurable distance threshold.
* **Intruder Escalation:** Uses a three-level voice-based verification protocol with rule-based response classification.
* **STT/TTS:** Google ASR for speech-to-text and Windows SAPI for text-to-speech.
* **Evidence Capture:** Saves intruder snapshots and speech transcripts.
* **Multithreading:** Runs voice activation independently from webcam monitoring.

## Performance

| Metric           |          Score |
| ---------------- | -------------: |
| Accuracy         |           0.90 |
| Precision        |           0.95 |
| Recall           |           0.90 |
| F1 Score         |      **0.913** |
| Voice Activation | **100% (5/5)** |

### Face Recognition by Condition

| Condition        | Accuracy |
| ---------------- | -------: |
| Background Noise |     1.00 |
| Bright Light     |     0.89 |
| Dim Light        |     0.82 |
| Unseen           |     1.00 |

## System Flow

```text
Voice / Keyboard Activation
          ↓
    Webcam Monitoring
          ↓
 Face Detection & Matching
       ↙       ↘
    Known     Unknown
      ↓          ↓
  Continue    3-Level
  Monitoring  Escalation
                 ↓
          Google ASR + Rule-Based
          Response Classification
                 ↓
        Windows SAPI TTS
                 ↓
        Evidence / Alarm
```


USAGE INSTRUCTIONS:
1. Install the required dependencies from the "requirements.txt file" using "pip install -r requirements.txt"
2. Run the "Milestone_3.py" file using "python Milestone_3.py"
3. Say "protect my room" or press "a" on the keyboard to turn on the guard mode 
4. System automatically detects trusted vs unknown persons
5. Unknown persons trigger 3-level verbal verification
6. Press 'q' to deactivate the agent
  

## Tech Stack

**Python · OpenCV · dlib · face_recognition · NumPy · SpeechRecognition · Google ASR · Windows SAPI · PyWin32 · Multithreading**

