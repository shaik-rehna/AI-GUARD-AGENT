# AI-GUARD-AGENT
### EE782 - Advanced Topics in Machine Learning
#### Team Members: Yashaswini K, Rehna Afroz Shaik
---

## Voice-Activated Intelligent Room Security System  

## Overview
This project implements an **autonomous, voice-controlled security system** that protects a personal room using **speech recognition**, **facial recognition**, and **multithreaded monitoring**.  
It activates on the voice command **“protect my room”**, monitors through a webcam, and interacts with intruders via **speech and reasoning** — all running **offline**.

---

## Features
- **Voice Activation & Control** – Uses the `speech_recognition` library to detect commands like *“protect my room”* and toggle *Protect Mode*.  
- **Real-Time Monitoring** – Displays live webcam feed with system status overlay using **OpenCV**.  
- **Face Recognition** – Matches detected faces against trusted embeddings using **face_recognition (dlib)**.  
- **Interactive Escalation** – Engages unknown persons via voice dialogue (Windows SAPI).  
- **Evidence Logging** – Saves intruder images, transcripts, and logs for accountability.  
- **Fully Offline** – No cloud dependency; all processing happens locally.  
- **Multithreaded Execution** – Voice and video run concurrently for real-time responsiveness.

---

## System Modules

### 1. Voice-Controlled Protection System 
- Activates *Protect Mode* on hearing **“protect my room”**.
- Logs all recognized commands with timestamps in `command_log.txt`.
- Accuracy achieved: **100% (5/5 test cases)**.

### 2. Face Recognition & Evaluation System
- **Enrollment Phase**: Captures and stores trusted face embeddings in `trusted_faces/`.
- **Testing Phase**: Compares unknown faces from `test_cases/` against stored embeddings.
- **Performance Metrics:**
  - Accuracy: **0.90**
  - Precision: **0.95**
  - Recall: **0.90**
  - F1 Score: **0.913**

#### Per-Condition Accuracy:
| Condition | Accuracy |
|------------|-----------|
| Background Noise | 1.00 |
| Bright Light | 0.89 |
| Dim Light | 0.82 |
| Unseen | 1.00 |

### 3. Integrated System 
Combines **voice**, **vision**, and **intelligent dialogue** into one unified system that:
- Listens for activation commands  
- Detects and verifies faces  
- Engages intruders verbally  
- Records evidence (frames + audio logs)  
- Triggers alarms when needed  

---

## System Architecture

```plaintext
┌────────────────────────────┐
│ Voice / Key Activation     │
│ "Protect my room" / 'a'    │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│ Camera Monitoring (OpenCV) │
│ Face Detection & Matching  │
└──────────────┬─────────────┘
       Known   │
        Face   ▼
    Continue Monitoring
               │
       Unknown ▼
┌────────────────────────────┐
│ Intruder Dialogue          │
│ Speech Recognition         │
│ Reply Classification       │
└──────────────┬─────────────┘
               ▼
┌────────────────────────────┐
│ Evidence & Alarm Handling  │
│ Save Frame + Transcript    │
└────────────────────────────┘
```
USAGE INSTRUCTIONS:
1. Install the required dependencies from the "requirements.txt file" using "pip install -r requirements.txt"
2. Run the "Milestone_3.py" file using "python Milestone_3.py"
3. Say "protect my room" or press "a" on the keyboard to turn on the guard mode 
4. System automatically detects trusted vs unknown persons
5. Unknown persons trigger 3-level verbal verification
6. Press 'q' to deactivate the agent
  



