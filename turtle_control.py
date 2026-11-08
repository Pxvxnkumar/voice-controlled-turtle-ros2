import os
import time
import math
import subprocess
import tempfile
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from faster_whisper import WhisperModel
from llm_parser import llm_parser


class TurtleController(Node):

    def __init__(self):
        super().__init__("voice_turtle_controller")

        self.publisher = self.create_publisher(
            Twist, "/turtle1/cmd_vel", 10
        )

        self.reset_client = self.create_client(
            Empty, "/reset"
        )

        self.linear_speed = 2.0
        self.angular_speed = 1.5

        print("Turtle Controller Ready!")

    def publish_velocity(self, linear, angular):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.publisher.publish(msg)

    def stop(self):
        self.publish_velocity(0.0, 0.0)
        print("Turtle stopped")

    def move_for(self, linear, angular, duration):
        end_time = time.monotonic() + duration

        while time.monotonic() < end_time:
            self.publish_velocity(linear, angular)
            time.sleep(0.1)

        self.stop()

    def draw_circle(self):
        print("Drawing circle")
        self.move_for(1.0, 1.5, 6)

    def draw_square(self):
        print("Drawing square")

        for _ in range(4):
            self.move_for(2.0, 0.0, 1.5)
            self.move_for(0.0, 1.5, math.pi / 2 / 1.5)

    def draw_triangle(self):
        print("Drawing triangle")

        for _ in range(3):
            self.move_for(2.0, 0.0, 1.5)
            self.move_for(0.0, 1.5, 2 * math.pi / 3 / 1.5)

    def reset_turtle(self):
        print("Resetting turtle")

        if not self.reset_client.wait_for_service(timeout_sec=2.0):
            print("Reset service unavailable")
            return

        future = self.reset_client.call_async(Empty.Request())
        rclpy.spin_until_future_complete(self, future)

        print("Turtle reset complete")

    def execute(self, intent):

        if intent == "forward":
            self.publish_velocity(self.linear_speed, 0.0)

        elif intent == "backward":
            self.publish_velocity(-self.linear_speed, 0.0)

        elif intent == "left":
            self.publish_velocity(0.0, self.angular_speed)

        elif intent == "right":
            self.publish_velocity(0.0, -self.angular_speed)

        elif intent == "stop":
            self.stop()

        elif intent == "faster":
            self.linear_speed = min(4.0, self.linear_speed + 0.5)
            print("Speed increased:", self.linear_speed)

        elif intent == "slower":
            self.linear_speed = max(0.5, self.linear_speed - 0.5)
            print("Speed decreased:", self.linear_speed)

        elif intent == "circle":
            self.draw_circle()

        elif intent == "square":
            self.draw_square()

        elif intent == "triangle":
            self.draw_triangle()

        elif intent == "spin":
            self.move_for(0.0, 3.0, 3)

        elif intent == "reset":
            self.stop()
            self.reset_turtle()


def record_audio(duration=4):

    filename = tempfile.mktemp(suffix=".wav")

    subprocess.run(
        [
            "timeout", str(duration),
            "parec",
            "--device=RDPSource",
            "--file-format=wav",
            filename
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if os.path.exists(filename) and os.path.getsize(filename) > 1000:
        return filename

    print("Microphone recording failed")
    return None


def recognize_command(text):

    text = text.lower().strip()

    commands = {
        "forward": [
            "forward", "move forward", "go forward",
            "aage", "आगे", "ಮುಂದೆ", "munde"
        ],

        "backward": [
            "backward", "back", "go back",
            "peeche", "पीछे", "ಹಿಂದೆ", "hinde"
        ],

        "left": [
            "turn left", "left", "baayein",
            "बाएं मुड़ो", "बाएँ", "ಎಡಕ್ಕೆ", "edakke"
        ],

        "right": [
            "turn right", "right", "daayein",
            "दाएं मुड़ो", "दाएँ", "ಬಲಕ್ಕೆ", "balakke"
        ],

        "stop": [
            "stop", "halt", "ruko", "रुको",
            "ನಿಲ್ಲು", "nillu"
        ],

        "faster": [
            "faster", "increase speed", "go faster",
            "तेज चलो", "ವೇಗವಾಗಿ ಚಲಿಸು"
        ],

        "slower": [
            "slower", "decrease speed", "go slower",
            "धीरे चलो", "ನಿಧಾನವಾಗಿ ಚಲಿಸು"
        ],

        "circle": [
            "draw circle", "circle", "गोला बनाओ",
            "ವೃತ್ತ ಬಿಡಿಸು"
        ],

        "square": [
            "draw square", "square", "वर्ग बनाओ",
            "ಚೌಕ ಬಿಡಿಸು"
        ],

        "triangle": [
            "draw triangle", "triangle", "त्रिकोण बनाओ",
            "ತ್ರಿಕೋನ ಬಿಡಿಸು"
        ],

        "spin": [
            "spin", "spin around", "rotate",
            "घूमो", "ಸುತ್ತು"
        ],

        "reset": [
            "reset", "reset turtle", "रीसेट करो",
            "ಮರುಹೊಂದಿಸು"
        ]
    }

    for intent, phrases in commands.items():
        if any(phrase in text for phrase in phrases):
            return intent

    return None


def main():

    rclpy.init()
    turtle = TurtleController()

    print("\nLoading Faster-Whisper...")
    model = WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8"
    )

    print("\nVOICE CONTROLLED TURTLE")
    print("Languages: English, Hindi, Kannada")
    print("12 available intents")
    print("Press Enter to speak or type exit to quit")

    try:

        while rclpy.ok():

            user_input = input("\nPress Enter to speak: ")

            if user_input.strip().lower() == "exit":
                break

            filename = record_audio(4)

            if filename is None:
                continue

            try:

                segments, info = model.transcribe(
                    filename,
                    vad_filter=False
                )

                text = " ".join(
                    segment.text for segment in segments
                ).strip()

                print("\nDetected language:", info.language)
                print("Recognized speech:", text)

                if not text:
                    print("No speech detected")
                    continue

                # Keyword parser
                keyword_intent = recognize_command(text)

                # Local LLM parser
                llm_result = llm_parser(text)

                llm_intent = llm_result.get("intent", "unknown")
                confidence = llm_result.get("confidence", 0.0)

                print("Keyword Parser:", keyword_intent)
                print("LLM Parser:", llm_result)

                valid_intents = [
                    "forward", "backward", "left", "right",
                    "stop", "faster", "slower", "circle",
                    "square", "triangle", "spin", "reset"
                ]

                if (
                    llm_intent in valid_intents
                    and isinstance(confidence, (int, float))
                    and confidence >= 0.70
                ):
                    print("Executing:", llm_intent)
                    turtle.execute(llm_intent)

                else:
                    print("Command not understood. Try again.")

            except Exception as error:
                print("Error:", error)

            finally:
                if os.path.exists(filename):
                    os.remove(filename)

    except KeyboardInterrupt:
        pass

    finally:
        turtle.stop()
        turtle.destroy_node()
        rclpy.shutdown()
        print("Voice controller stopped.")


if __name__ == "__main__":
    main()