import os
import csv
import subprocess
from datetime import datetime

BASE_DIR = "voice_dataset"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
CSV_FILE = os.path.join(BASE_DIR, "metadata.csv")

os.makedirs(AUDIO_DIR, exist_ok=True)

intents = [
    "forward", "backward", "left", "right",
    "stop", "faster", "slower", "circle",
    "square", "triangle", "spin", "reset"
]

languages = ["English", "Hindi", "Kannada"]

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "speaker_id",
            "language",
            "intent",
            "transcript",
            "audio_file",
            "timestamp"
        ])


def record_audio(filename, duration=4):

    print("\nRecording starts now. Speak clearly!")

    result = subprocess.run([
        "timeout", str(duration),
        "parec",
        "--device=RDPSource",
        "--file-format=wav",
        filename
    ])

    if os.path.exists(filename) and os.path.getsize(filename) > 1000:
        print("Recording saved!")
        return True

    print("Recording failed. Check your microphone.")
    return False


print("VOICE DATASET COLLECTION")
print("------------------------")

speaker_id = input("Enter speaker ID (example S01): ").strip().upper()

if not speaker_id:
    print("Speaker ID is required.")
    raise SystemExit

consent = input(
    "Has this speaker given informed consent to record their voice? (yes/no): "
).strip().lower()

if consent != "yes":
    print("Recording cancelled. Consent is required.")
    raise SystemExit

for language in languages:

    print("\nLanguage:", language)

    for intent in intents:

        print("\nIntent:", intent)

        transcript = input(
            "Enter the exact sentence spoken by the speaker: "
        ).strip()

        if not transcript:
            print("Skipping empty transcript.")
            continue

        filename = (
            f"{speaker_id}_{language}_{intent}.wav"
        )

        filepath = os.path.join(AUDIO_DIR, filename)

        confirm = input("Press Enter to record or type skip: ")

        if confirm.lower() == "skip":
            continue

        success = record_audio(filepath, 4)

        if success:

            timestamp = datetime.now().isoformat()

            with open(
                CSV_FILE, "a", newline="", encoding="utf-8"
            ) as f:

                writer = csv.writer(f)

                writer.writerow([
                    speaker_id,
                    language,
                    intent,
                    transcript,
                    filename,
                    timestamp
                ])

print("\nDataset collection session completed!")
print("Metadata saved in:", CSV_FILE)