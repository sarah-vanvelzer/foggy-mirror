import cv2
import numpy as np
import mediapipe as mp

def foggy_mirror():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Foggy Mirror", cv2.WINDOW_NORMAL)

    mask = None
    hands = mp.solutions.hands.Hands(max_num_hands=1)
    wipe_size = 40
    prev_point = None
    
    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        # Create the mask one, on the first frame:
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
            fingertip = hand.landmark[8] # Index

            # Convert 0-1 position to pixels:
            height, width = frame.shape[:2]
            x = int(fingertip.x * width)
            y = int(fingertip.y * height)

            # Draw white on the mask where the finger is:
            point = (x, y)
            if prev_point is not None:
                cv2.line(mask, prev_point, point, 255, wipe_size * 2)
            cv2.circle(mask, point, wipe_size, 255, -1)
            prev_point = point

        else:
            prev_point = None

        # Combine: clear where mask is white, foggy where mask is black:
        soft_mask = cv2.GaussianBlur(mask, (41, 41), 0)
        alpha = soft_mask.astype(np.float32) / 255
        alpha = alpha[:, :, np.newaxis]
        output = (frame * alpha + fog * (1 - alpha)).astype(np.uint8)

        cv2.imshow("Foggy Mirror", output)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    foggy_mirror()