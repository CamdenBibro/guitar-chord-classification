import streamlit as st
import random
import sounddevice as sd
import wave
import os
import numpy as np

# Directory containing chord images
chord_images_dir = "/Users/camdenbibro/Documents/Guitar-Chord-Classification/test_chord_images"  # Replace with the actual path to your chord images directory

# List of chords
chords = [
    "Ab", "G#m", "Ab6", "Ab7", "Ab9", "G#m6", "G#m7", "Abmaj7",
    "A", "Am", "A6", "A7", "A9", "Am6", "Am7", "Amaj7",
    "Bb", "Bbm", "Bb6", "Bb7", "Bb9", "Bbm6", "Bbm7", "Bbmaj7",
    "B", "Bm", "B6", "B7", "B9", "Bm6", "Bm7", "Bmaj7",
    "C", "Cm", "C6", "C7", "C9", "Cm6", "Cm7", "Cmaj7",
    "D", "Dm", "D6", "D7", "D9", "Dm6", "Dm7", "Dmaj7",
    "E", "Em", "E6", "E7", "E9", "Em6", "Em7", "Emaj7",
    "F", "Fm", "F6", "F7", "F9", "Fm6", "Fm7", "Fmaj7",
    "G", "Gm", "G6", "G7", "G9", "Gm6", "Gm7", "Gmaj7"
]

# Generate descriptions dynamically
def generate_description(chord):
    styles = ["loud", "softly", "quickly", "slowly", "relaxed", "quietly"]
    directions = ["with a downward strum", "with an upward strum"]
    style = random.choice(styles)
    direction = random.choice(directions)
    return f"{chord}_{style}_{direction}"

# Directory to save recordings
output_dir = "recordings"
os.makedirs(output_dir, exist_ok=True)

# Function to record audio
def record_audio(duration, filename):
    st.info("Recording...")
    samplerate = 44100  # 44.1 kHz
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()  # Wait for the recording to finish
    st.success("Recording complete!")
    # Save the recording as a WAV file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # Sample width in bytes
        wf.setframerate(samplerate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    return filename

# Streamlit app
st.title("Record your Chords")

# Persistent state for chord and description
if "selected_chord" not in st.session_state:
    st.session_state["selected_chord"] = random.choice(chords)
    st.session_state["description"] = generate_description(st.session_state["selected_chord"])
    st.session_state["last_recording"] = None
    st.session_state["recording_saved"] = False

# Display the selected chord image and description
chord_name = st.session_state["selected_chord"]
description = st.session_state["description"]
image_path = os.path.join(chord_images_dir, f"{chord_name}.png")
st.image(image_path, caption=f"Chord: {chord_name}", width=300)
st.subheader(f"Please play this chord: {description.replace('_', ' ')}")

# Record button
duration = st.slider("Select recording duration (seconds)", 1, 10, 3, key="duration_slider")
if st.button("Record"):
    filename = f"{output_dir}/{description}_{random.randint(1000, 9999)}.wav"
    record_audio(duration, filename)
    st.session_state["last_recording"] = filename
    st.session_state["recording_saved"] = False  # Mark recording as not saved yet
    st.write(f"Recording saved as: `{filename}`")

# Play, save, or discard the recording
if st.session_state.get("last_recording"):
    if st.button("Play Recording"):
        st.audio(st.session_state["last_recording"], format="audio/wav")

    if not st.session_state.get("recording_saved", False):
        if st.button("Approve and Save Recording"):
            st.success("Recording approved and saved.")
            st.session_state["recording_saved"] = True
            # Move to the next chord
            st.session_state["selected_chord"] = random.choice(chords)
            st.session_state["description"] = generate_description(st.session_state["selected_chord"])
            st.session_state["last_recording"] = None
            st.session_state["recording_saved"] = False

    if st.button("Discard Recording"):
        os.remove(st.session_state["last_recording"])
        del st.session_state["last_recording"]
        st.warning("Recording deleted.")
        # Move to the next chord
        st.session_state["selected_chord"] = random.choice(chords)
        st.session_state["description"] = generate_description(st.session_state["selected_chord"])
        st.session_state["last_recording"] = None
        st.session_state["recording_saved"] = False