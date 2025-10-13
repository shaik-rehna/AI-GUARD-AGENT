"""
Milestone3.py - Windows SAPI Version

Complete Guard Agent System with Voice Activation, Face Recognition, and Escalation Dialogue

Milestone 1: Voice Activation & Basic Input
- Activation via speech command "protect my room" or keypress 'a'
- Real-time speech recognition for activation/deactivation

Milestone 2: Face Recognition & Trusted User Enrollment  
- Loads pre-enrolled face embeddings from trusted_faces/*.npy
- Real-time face detection and recognition using webcam
- Matches against trusted users with configurable threshold

Milestone 3: Escalation Dialogue & Full Integration
- 3-level escalation protocol for unknown persons
- Windows SAPI TTS for spoken responses
- Evidence collection (images + transcripts)
- Alarm system for maximum escalation
"""

import os
import cv2
import time
import threading
import datetime
import numpy as np
import face_recognition
import speech_recognition as sr
import winsound

# ---------- CONFIGURATION SECTION ----------
ENROLL_DIR = "trusted_faces"              # Directory containing trusted face embeddings
EVIDENCE_DIR = "evidence"                 # Directory for saving evidence files
os.makedirs(EVIDENCE_DIR, exist_ok=True) 

# Milestone 1: Activation Configuration
ACTIVATION_PHRASE = "protect my room"  # Voice command to activate guard mode
DEACTIVATION_PHRASE = "stop"           # Voice command to deactivate guard mode
ACTIVATE_KEY = ord("a")                # Keyboard key to toggle guard mode

# Milestone 2: Face Recognition Configuration
FACE_MATCH_THRESHOLD = 0.45            # Threshold set after fine-tuning

# Milestone 3: Escalation Configuration
ESCALATION_COOLDOWN = 10               # Seconds between escalation triggers
ASR_TIMEOUT = 10                       # Seconds to wait for voice response during escalation

# Alarm system configuration
ALARM_FILE = r"E:\7th SEM\EE782 ADV TOPICS IN ML\Assignment_2\alarm.wav"
if not os.path.exists(ALARM_FILE):
    raise FileNotFoundError(f"Alarm file not found: {ALARM_FILE}")

# ---------- TRUSTED FACE DATABASE LOADING ----------
# Milestone 2: Load pre-enrolled face embeddings for recognition
trusted_encodings = []  # List to store face encoding vectors
trusted_names = []      # List to store corresponding names

# Load all .npy files from the trusted_faces directory
for f in os.listdir(ENROLL_DIR):
    if f.endswith(".npy"):
        path = os.path.join(ENROLL_DIR, f)
        name = os.path.splitext(f)[0]  # Extract name from filename (without extension)
        arr = np.load(path, allow_pickle=True)  # Load face embeddings array
        
        for enc in arr:
            trusted_encodings.append(enc)
            trusted_names.append(name)

print("[INFO] Trusted users:", set(trusted_names))
print("[INFO] Total embeddings:", len(trusted_encodings))

# ---------- GLOBAL SYSTEM STATE ----------
protect_mode = False               # Main guard mode state (True = active, False = inactive)
listening_thread_running = True    # Control flag for activation listener thread
last_escalation_time = 0.0         # Timestamp of last escalation to prevent spam

# ---------- TEXT-TO-SPEECH (TTS) SETUP ----------
# Milestone 3: Windows SAPI for reliable text-to-speech
try:
    import win32com.client
    SAPI_AVAILABLE = True
    print("[TTS] Initializing Windows SAPI...")
    sapi_speaker = win32com.client.Dispatch("SAPI.SpVoice")  # Create SAPI speaker object
    print("[TTS] Windows SAPI initialized successfully")
except ImportError:
    SAPI_AVAILABLE = False
    print("[TTS WARNING] pywin32 not available, SAPI TTS disabled")
except Exception as e:
    SAPI_AVAILABLE = False
    print(f"[TTS ERROR] SAPI initialization failed: {e}")

def speak(text):
    """
    Milestone 1 & 3: Convert text to speech using Windows SAPI
    Provides audible feedback for system state and escalation prompts
    """
    print(f"[TTS] Speaking: {text}")
    
    if not SAPI_AVAILABLE:
        print(f"[TTS FALLBACK] {text}")  # Fallback to console output if SAPI unavailable
        return
        
    try:
        # Speak synchronously (blocks until speech completes)
        sapi_speaker.Speak(text)
        # Small pause after speaking to ensure clarity
        time.sleep(0.3)
    except Exception as e:
        print(f"[TTS ERROR] {e}")

# ---------- SPEECH RECOGNITION (ASR) SETUP ----------
# Milestone 1: Google Speech Recognition for voice commands
recognizer = sr.Recognizer()

def write_log(msg):
    """Utility function for timestamped log messages"""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

# ---------- ALARM SYSTEM ----------
# Milestone 3: Audio alarm for maximum escalation level
def play_alarm():
    """Play alarm sound asynchronously in a separate thread"""
    threading.Thread(target=lambda: winsound.PlaySound(ALARM_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC), daemon=True).start()

# ---------- ESCALATION SYSTEM ----------
# Milestone 3: Multi-level escalation protocol for unknown persons
ESCALATION_PROMPTS = {
    1: "Hello. Who are you and why are you in this room?",           # Level 1: Friendly inquiry
    2: "This is not your room. Leave the room immediately",          # Level 2: Firm warning  
    3: "Leave this room right now. I am recording this."             # Level 3: Final warning
}

def judge_reply(text):
    """
    Milestone 3: Analyze user's verbal response during escalation
    Returns classification of user's intent based on keyword matching
    """
    if not text:
        return "no_response"  # No speech detected
    
    t = text.lower()  # Convert to lowercase for case-insensitive matching
    
    # Cooperative responses - user agrees to leave
    if any(kw in t for kw in ["sorry", "i will leave", "i will go", "i will get out", "i'm leaving"]):
        return "ok"
    
    # Defiant responses - user refuses to cooperate  
    if any(kw in t for kw in ["no", "i will not", "i'm not", "none of your business", "refuse"]):
        return "refuse"
    
    # Very short or unclear responses
    if len(t) < 3:
        return "no_response"
    
    # Default classification for unclear but substantial responses
    return "suspicious"

def escalate_interaction(frame):
    """
    Milestone 3: Execute 3-level escalation protocol with unknown person
    Each level: Speak prompt -> Listen for response -> Judge response -> Act accordingly
    """
    write_log("[ESCALATION] Starting escalation process")
    mic = sr.Microphone()
    transcripts = []  # Store all conversation transcripts for evidence

    # Execute each escalation level sequentially
    for level in (1, 2, 3):
        prompt = ESCALATION_PROMPTS[level]
        write_log(f"[ESCALATION] Level {level} prompt: {prompt}")

        # Speak the escalation prompt using TTS
        speak(prompt)
        write_log(f"[ESCALATION] Level {level} prompt spoken")

        # Wait after speaking to ensure the person hears and processes the message
        time.sleep(1.0)

        # Listen for verbal response from the person
        transcript = ""
        with mic as source:
            try:
                write_log("[ESCALATION] Listening for response...")
                # Listen for speech with timeout limits
                audio = recognizer.listen(source, timeout=ASR_TIMEOUT, phrase_time_limit=ASR_TIMEOUT)
                write_log("[ESCALATION] Processing speech...")
                # Convert speech to text using Google Speech Recognition
                transcript = recognizer.recognize_google(audio)
            except sr.WaitTimeoutError:
                write_log("[ESCALATION] Listen timeout - no response")
            except sr.UnknownValueError:
                write_log("[ESCALATION] Could not understand speech")
            except Exception as e:
                write_log(f"[ESCALATION ERROR] {e}")
                
        write_log(f"[ASR] Level {level} transcript: {transcript}")
        transcripts.append((level, transcript))  # Store for evidence

        # Analyze the person's response
        judgement = judge_reply(transcript)
        write_log(f"[JUDGEMENT] {judgement}")

        # Handle cooperative response - de-escalate
        if judgement == "ok":
            speak("Thank you. I will stand down.")
            return {"action": "stand_down", "level": level, "transcript": transcript}
        
        # Handle defiant response - escalate immediately
        elif judgement == "refuse":
            speak("You are not authorized. Recording evidence.")
            play_alarm()  # Trigger alarm for defiance
            
            # Save evidence (image + transcript)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(os.path.join(EVIDENCE_DIR, f"unknown_{ts}.jpg"), frame)
            with open(os.path.join(EVIDENCE_DIR, f"unknown_{ts}.txt"), "w") as f:
                f.write(transcript)
                
            return {"action": "record_and_warn", "level": level, "transcript": transcript}

        # Brief pause before next escalation level
        time.sleep(2.0)

    # Level 3 fallback - maximum escalation reached without resolution
    speak("Final warning. Recording evidence and triggering alarm.")
    play_alarm()  # Trigger maximum alarm
    
    # Save comprehensive evidence
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(os.path.join(EVIDENCE_DIR, f"unknown_{ts}.jpg"), frame)
    with open(os.path.join(EVIDENCE_DIR, f"unknown_{ts}.txt"), "w") as f:
        for lev, txt in transcripts:
            f.write(f"L{lev}: {txt}\n")  # Save all level transcripts
            
    return {"action": "record_and_warn", "level": 3, "transcript": "|".join([t for _, t in transcripts])}

# ---------- ACTIVATION LISTENER THREAD ----------
# Milestone 1: Continuous voice activation in background thread
def listen_for_activation():
    """
    Background thread that continuously listens for activation/deactivation voice commands
    Runs independently of main webcam loop for responsive voice control
    """
    global protect_mode, listening_thread_running
    write_log("[ASR] Initializing activation listener...")
    
    try:
        # Initialize microphone with ambient noise adjustment
        mic = sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
        write_log("[ASR] Activation listener started.")
    except Exception as e:
        write_log(f"[ASR ERROR] Microphone initialization failed: {e}")
        return

    # Continuous listening loop
    while listening_thread_running:
        try:
            with mic as source:
                # Listen for speech with 4-second phrase limit and 10-second timeout
                audio = recognizer.listen(source, phrase_time_limit=4, timeout=10)
            
            # Convert speech to text
            text = recognizer.recognize_google(audio).lower()
            write_log(f"[ASR] Heard: {text!r}")
            
            # Check for activation phrase when system is inactive
            if ACTIVATION_PHRASE in text and not protect_mode:
                protect_mode = True
                speak("Guard mode activated.")
                write_log("[STATE] Protect Mode -> ON")
                
            # Check for deactivation phrase when system is active  
            elif DEACTIVATION_PHRASE in text and protect_mode:
                protect_mode = False
                speak("Guard mode deactivated.")
                write_log("[STATE] Protect Mode -> OFF")
                
        # Handle various speech recognition exceptions
        except sr.WaitTimeoutError:
            continue  # No speech detected, continue listening
        except sr.UnknownValueError:
            continue  # Speech detected but not understandable
        except sr.RequestError as e:
            write_log(f"[ASR ERROR] {e}")
            time.sleep(2.0)  # Brief pause on service errors
        except Exception as e:
            write_log(f"[ASR UNEXPECTED ERROR] {e}")
            time.sleep(2.0)  # Brief pause on unexpected errors

# Start the activation listener in a background thread
listener_thread = threading.Thread(target=listen_for_activation, daemon=True)
listener_thread.start()

# ---------- MAIN WEBCAM SURVEILLANCE LOOP ----------
def main_loop():
    """
    Main surveillance loop combining all milestones:
    - Real-time webcam feed display
    - Face detection and recognition when protect_mode is active
    - Escalation triggering for unknown persons
    - Keyboard input handling
    """
    global protect_mode, last_escalation_time, listening_thread_running
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        write_log("[ERROR] Cannot open webcam")
        return

    write_log("Starting main loop. Press 'a' to toggle guard or 'q' to quit.")

    # Main video processing loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Create display frame with status overlay
        display = frame.copy()
        status_txt = f"Protect Mode: {'ON' if protect_mode else 'OFF'}"
        # Green text when active, red when inactive
        color = (0, 255, 0) if protect_mode else (0, 0, 255)
        cv2.putText(display, status_txt, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, color, 2)

        # Milestone 2: Face recognition when protect mode is active
        if protect_mode:
            # Convert frame to RGB for face recognition library
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Detect face locations in the frame
            boxes = face_recognition.face_locations(rgb_frame)
            
            if boxes:  # If faces are detected
                # Extract face encodings for recognized faces
                encodings = face_recognition.face_encodings(rgb_frame, boxes)
                if encodings:
                    # Process first detected face 
                    top, right, bottom, left = boxes[0]
                    enc = encodings[0]
                    
                    # Calculate distances to all trusted face embeddings
                    distances = face_recognition.face_distance(trusted_encodings, enc) if trusted_encodings else []
                    name = "Unknown"  # Default to unknown
                    
                    # Find closest match if trusted faces exist
                    if distances.size > 0:
                        idx = np.argmin(distances)
                        # Check if closest match is within threshold
                        if distances[idx] < FACE_MATCH_THRESHOLD:
                            name = trusted_names[idx]

                    # Draw bounding box and label (green for trusted, red for unknown)
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(display, (left, top), (right, bottom), color, 2)
                    cv2.putText(display, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                    # Milestone 3: Trigger escalation for unknown persons with cooldown
                    if (name == "Unknown" and 
                        (time.time() - last_escalation_time) > ESCALATION_COOLDOWN):
                        
                        last_escalation_time = time.time()  # Update cooldown timer
                        write_log("[EVENT] Unknown detected: starting escalation")
                        speak("Unknown person detected. Starting verification.")
                        
                        # Take snapshot for evidence and start escalation
                        snapshot = frame.copy()
                        res = escalate_interaction(snapshot)
                        write_log(f"[ESCALATION RESULT] {res}")

        # Display the annotated frame
        cv2.imshow("Guard Agent (press 'q' to quit)", display)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ACTIVATE_KEY:  # 'a' key toggles guard mode
            protect_mode = not protect_mode
            speak("Guard mode activated." if protect_mode else "Guard mode deactivated.")
            write_log(f"[STATE] Protect Mode toggled -> {protect_mode}")
        elif key == ord('q'):  # 'q' key quits the application
            break

    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()
    listening_thread_running = False  # Signal listener thread to stop
    write_log("Shutting down.")

if __name__ == "__main__":
    main_loop()