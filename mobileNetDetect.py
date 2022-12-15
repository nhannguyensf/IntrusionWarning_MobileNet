import cv2
import numpy as np
from telegram_utils import send_telegram
import datetime
import threading

class MobileNetDetect:
    def __init__(self):
        self.classnames_file = "models/classnames.txt"
        self.weights_file = "models/MobileNetSSD_deploy.caffemodel"
        self.config_file = "models/MobileNetSSD_deploy.prototxt.txt"
        self.confidence = 0.5
        self.model = cv2.dnn.readNetFromCaffe(self.config_file, self.weights_file)
        # read the class names
        self.classes = None
        self.read_class_file()
        # bounding box color
        np.random.seed(111)  # set seed to ensure color is consistent
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        # telegram sending settings
        self.last_alert = None
        self.alert_telegram_each = 5  # seconds

    def read_class_file(self):
        with open(self.classnames_file, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

    def dnn_detection_to_points(self, detection, width, height):
        x1 = int(detection[3] * width)
        y1 = int(detection[4] * height)
        x2 = int(detection[5] * width)
        y2 = int(detection[6] * height)
        return x1, y1, x2, y2

    def draw_bounding_box_with_label(self, image, x1, y1, x2, y2, label, color, thickness=2):
        """Helper function to draw a bounding box with class label

        Parameters
        ----------
        image : np.ndarray
            Image object read by cv2
        x1, y1, x2, y2 : float
            Coordinates of the bounding box (top left) to (bottom right)
        label : str
            Text to be shown in bounding box, usually classname
        color : tuple
            BGR color
        thickness : int, optional
            Thickness of the bounding box
        """
        # draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color=color, thickness=thickness)
        # draw a rectangle that contains label
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        label_size, baseline = cv2.getTextSize(label, font, font_scale, thickness=thickness)
        cv2.rectangle(image, (x1 - int(thickness / 2), y1 - label_size[1]), (x1 + label_size[0], y1), color, cv2.FILLED, )
        # draw label
        cv2.putText(image, label, (x1, y1), font, font_scale, color=(0, 0, 0))  # black label
        image = self.alert(image)

    def alert(self, img):
        cv2.putText(img, "ALARM!!!!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # New thread to send telegram after 15 seconds
        if (self.last_alert is None) or ((datetime.datetime.utcnow() - self.last_alert).total_seconds() > self.alert_telegram_each):
            self.last_alert = datetime.datetime.utcnow()
            cv2.imwrite("alert.png", img)
            thread = threading.Thread(target=send_telegram)
            thread.start()
        return img

    def detect(self, frame):
        height, width = frame.shape[:2]
        input_size = (300, 300)
        resized_image = cv2.resize(frame, dsize=input_size)
        blob = cv2.dnn.blobFromImage(resized_image, scalefactor=0.007843, size=input_size, mean=127.5)
        self.model.setInput(blob)
        detections = self.model.forward()

        # plot bounding-box
        for i in range(detections.shape[2]):
            detection = detections[0, 0, i]
            confidence = detection[2]
            # only keep strong detections
            if confidence > self.confidence:
                idx = int(detection[1])  # class index
                x1, y1, x2, y2 = self.dnn_detection_to_points(detection, width, height)
                label = "%s: %.2f" % (self.classes[idx], confidence)
                color = self.colors[idx]
                self.draw_bounding_box_with_label(frame, x1, y1, x2, y2, label=label, color=color)
        return frame
