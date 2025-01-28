import os
import random
import uuid
from flask import Flask, session, render_template, request, jsonify
from google.cloud import storage
from google.cloud import secretmanager
from datetime import datetime

app = Flask(__name__)


def get_secret():
    """Fetch the Flask secret key from Google Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/<your-project-id>/secrets/flask-secret-key/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error fetching secret: {e}")
        return os.environ.get("FLASK_SECRET_KEY", "fallback-key")  # Fallback for local testing

# Set the Flask secret key
app.secret_key = get_secret()

# Path to the local static folder containing guitar chords
CHORD_IMAGES_FOLDER = os.path.join('static', 'guitar_chords')

# Generate a list of chord images from the local folder
images = [os.path.join(CHORD_IMAGES_FOLDER, file) for file in os.listdir(CHORD_IMAGES_FOLDER) if file.endswith(('.png', '.jpg', '.jpeg'))]

@app.before_request
def assign_user_id():
    """Assign a unique user ID to each session."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]  # Generate a short unique ID

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/get_chord', methods=['GET'])
def get_chord():
    """Return a random guitar chord image and instructions."""
    global current_chord, current_instruction
    try:
        # Randomly select a chord image
        current_chord = random.choice(images)

        # Generate random instructions
        strum_patterns = ["upward", "downward"]
        playing_styles = ["loudly", "softly", "relaxed", "fast", "slow"]
        strum = random.choice(strum_patterns)
        style = random.choice(playing_styles)
        current_instruction = f"{strum}_{style}"

        # Return the path to the selected chord and the instructions
        return jsonify({
            "chord_image": current_chord,
            "instruction": f"Strum {strum} and play {style}."
        })
    except Exception as e:
        print(f"Error in /get_chord: {e}")
        return jsonify({"error": str(e)})

@app.route('/save_recording', methods=['POST'])
def save_recording():
    """Save the uploaded audio file to Google Cloud Storage."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    try:
        # Generate a unique filename
        user_id = session.get('user_id', 'unknown_user')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chord_name = os.path.basename(current_chord).split('.')[0]  # Extract chord name from filename
        filename = f"{chord_name}_{current_instruction}_{user_id}_{timestamp}.wav"

        # Save the file temporarily to /tmp (App Engine standard environment allows writes only here)
        temp_path = os.path.join("/tmp", filename)
        file.save(temp_path)

        # Upload to Google Cloud Storage
        client = storage.Client()
        bucket = client.bucket("bibroce-guitar-bucket")
        blob = bucket.blob(f"recordings/{filename}")  # Save under 'recordings/' folder in the bucket
        blob.upload_from_filename(temp_path)

        # Clean up the temporary file
        os.remove(temp_path)

        return jsonify({"message": f"Recording saved as {filename} in the cloud."})
    except Exception as e:
        print(f"Error in /save_recording: {e}")
        return jsonify({"error": "Failed to upload file."}), 500


@app.route('/skip', methods=['POST'])
def skip_chord():
    """Clear the current recording and fetch a new chord."""
    global current_chord, current_instruction
    current_chord = None
    current_instruction = None
    return get_chord()

if __name__ == '__main__':
    app.run(debug=True)
