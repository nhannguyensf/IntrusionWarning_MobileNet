import cv2
from imutils.video import VideoStream
from mobileNetDetect import MobileNetDetect

video = VideoStream(src=0).start()
# model mobileNetSSD
model = MobileNetDetect()
detect = False

while True:
    frame = video.read()
    frame = cv2.flip(frame, 1)
    if detect:
        frame = model.detect(frame=frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    detect = True
    # Hien anh ra man hinh
    cv2.imshow("Intrusion Warning Application", frame)
video.stop()
cv2.destroyAllWindows()

