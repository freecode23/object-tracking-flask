import cv2
import numpy as np
from object_detection import ObjectDetection
from deep_sort.deep_sort import Deep
import torch
import os

# !pip install --upgrade pip
# !pip install -r requirements.txt
# !pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt
# !pip3 install --upgrade tensorflow==2.4


class Tracker(object):
    def __init__(self):
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        # 1. Load Detector
        self.yolov4 = ObjectDetection(
            "dnn_model/yolov4.weights", "dnn_model/yolov4.cfg")
        self.yolov4.load_class_names("dnn_model/classes.txt")
        self.yolov4.load_detection_model(image_size=832,  # 416 - 1280
                                         nmsThreshold=0.4,
                                         confThreshold=0.3)
        self.yolov5 = torch.hub.load('ultralytics/yolov5', 'yolov5s')

        # 2. Load Tracker (DeepSORT)
        self.deep = Deep(max_distance=0.7,
                         nms_max_overlap=1,
                         n_init=3,
                         max_age=15,
                         max_iou_distance=0.7)

        self.tracker = self.deep.sort_tracker()

    def get_features(self, frame, boxes):
        """Given BGR color image and a matrix of
        bounding boxes in format `(x, y, w, h)` and returns a matrix of
        corresponding feature vectors."""

        return self.deep.encoder(frame, boxes)

    def update_features(self, detections):
        """Given a new detections, perform Kalman filter measurement update step and update the feature"""
        return self.tracker.update(detections)

    def kalman_predict(self):
        """Propagate the state distribution to the current time step using a
        Kalman filter prediction step"""
        self.tracker.predict()

    def detect_yolov5(self, frame):
        """Given results from yolov5, extract classs ids, scores and boxes as numpy array"""
        model = self.yolov5
        results = model(frame)
        result_pandas = results.pandas().xyxy[0]
        print(result_pandas)
        result_list = results.xyxy[0].cpu().detach().tolist()
        class_ids = []
        scores = []
        boxes = []

        for i in range(len(result_list)):
            class_ids.append(result_list[i][5])
            scores.append(result_list[i][4])
            boxes.append(result_list[i][0:4])

        class_ids = np.asarray(class_ids, dtype=np.int32)
        scores = np.asarray(scores, dtype=np.float64)
        boxes = np.asarray(boxes, dtype=np.float64)

        return class_ids, scores, boxes

    def detect_yolov4(self, frame):
        """Detect the object in a given frame using yolov4 model and
        return the class ids, scores and boxes as numpy array"""
        return self.yolov4.detect(frame)

    def create_detections_object(self, boxes, scores, class_ids, features):
        """Given results from yolov, and features create a detection object to perform Kalman filter measurement update"""
        return self.deep.Detection(
            boxes, scores, class_ids, features)

    def process_frame(self, frame):
        """ 1. Object Detection per frame"""
        # Question : Insert new model but will give error because its running on mps (need nvidia gpu)
        # https://github.com/pytorch/pytorch/issues/77851
        # >>>>>>>>>>>>>>>>>>>>>>>>>> yoloV5 >>>>>>>>>>>>>>>>>>
        # (class_ids, scores, boxes) = self.detect_yolov5(frame)
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        (class_ids, scores, boxes) = self.detect_yolov4(frame)
        print("class_ids>>>>>>>>>>>>>>", class_ids)
        print("scores>>>>>>>>>>>>>>", scores)
        print("boxes>>>>>>>>>>>>>>", boxes)

        """ 2. Object Tracking """
        features = self.get_features(frame, boxes)
        detections = self.create_detections_object(
            boxes, scores, class_ids, features)

        self.kalman_predict()
        (class_ids, object_ids, boxes) = self.update_features(detections)
        print("after:class_ids>>>>>>>>>>>>>>", class_ids)
        print("after:boxes>>>>>>>>>>>>>>", boxes)

        for class_id, object_id, box in zip(class_ids, object_ids, boxes):

            (x, y, x2, y2) = box
            class_name = self.yolov4.classes[class_id]
            color = self.yolov4.colors[class_id]

            cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
            cv2.rectangle(frame, (x, y), (x + len(class_name)
                                          * 20, y - 30), color, -1)
            cv2.putText(frame, class_name + " " + str(object_id),
                        (x, y - 10), 0, 0.75, (255, 255, 255), 2)

        return frame
    
    
    
def main():
    # capture frame
    cap = cv2.VideoCapture(0)

    # create YoloDeepSort tracker
    yoloDeepSort=Tracker()

    while True:
        # create frame
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = yoloDeepSort.process_frame(frame)
        
        # show
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
