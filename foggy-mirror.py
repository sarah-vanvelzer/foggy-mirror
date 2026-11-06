import cv2
import numpy as np
import mediapipe as mp
import sounddevice as sd

def finger_is_up(hand, tip, knuckle): # Returns True if tip above knuckle
    return hand.landmark[tip].y < hand.landmark[knuckle].y

mic_volume = 0.0

def audio_callback(indata, frames, time, status):
    global mic_volume
    # Standard way to measure loudness:
    mic_volume = float(np.sqrt(np.mean(indata**2)))

def foggy_mirror():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Foggy Mirror", cv2.WINDOW_NORMAL)

    mask = None
    hands = mp.solutions.hands.Hands(max_num_hands=1)
    wipe_size = 30
    prev_point = None

    # Starting listening:
    stream = sd.InputStream(callback=audio_callback, channels=1)
    stream.start()
    breath_threshold = 0.02
    
    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        # Create the mask once, on the first frame:
        if mask is None:
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        # Blur the frame:
        blurred = cv2.GaussianBlur(frame, (55, 55), 0)

        # Make plain white image the same size as the frame:
        white = np.full_like(frame, 255)

        # Mix them: 60% blurry picture + 40% white:
        fog = cv2.addWeighted(blurred, 0.6, white, 0.4, 0)

        # Find the hand:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            height, width = frame.shape[:2]

            middle_up = finger_is_up(hand, 12, 10)
            ring_up = finger_is_up(hand, 16, 14)
            pinky_up = finger_is_up(hand, 20, 18)

            if middle_up and ring_up and pinky_up:
                # OPEN HAND: wipe with whole palm
                points = np.array([(int(lm.x * width), int(lm.y * height))
                                   for lm in hand.landmark])
                hull = cv2.convexHull(points)
                cv2.fillConvexPoly(mask, hull, 255)
                prev_point = None
            else:
                # POINTING: write with fingertip
                fingertip = hand.landmark[8]
                point = (int(fingertip.x * width), int(fingertip.y * height))
                if prev_point is not None:
                    cv2.line(mask, prev_point, point, 255, wipe_size * 2)
                cv2.circle(mask, point, wipe_size, 255, -1)
                prev_point = point

        else:
            prev_point = None

        # Breathing brings back the fog:
        if mic_volume > breath_threshold:
            mask = cv2.subtract(mask, 20)

        # Combine: clear where mask is white, foggy where mask is black:
        soft_mask = cv2.GaussianBlur(mask, (41, 41), 0)
        alpha = soft_mask.astype(np.float32) / 255
        alpha = alpha[:, :, np.newaxis]
        output = (frame * alpha + fog * (1 - alpha)).astype(np.uint8)
        cv2.putText(output, f"{mic_volume:.3f}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

        cv2.imshow("Foggy Mirror", output)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    stream.stop()
    stream.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    foggy_mirror()