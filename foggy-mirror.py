import cv2
import numpy as np

def foggy_mirror():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Foggy Mirror", cv2.WINDOW_NORMAL)
    
    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)

        # Blur the frame:
        blurred = cv2.GaussianBlur(frame, (55, 55), 0)

        # Make plain white image the same size as the frame:
        white = np.full_like(frame, 255)

        # Mix them: 60% blurry picture + 40% white:
        fog = cv2.addWeighted(blurred, 0.6, white, 0.4, 0)

        cv2.imshow("Foggy Mirror", fog)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    foggy_mirror()