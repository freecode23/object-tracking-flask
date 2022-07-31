import cv2
import numpy as np
from object_detection import ObjectDetection
from deep_sort.deep_sort import Deep
import os
print("import os")
weight_path=os.path.abspath("dnn_model/yolov4.weights")
print("finish weight path")
config_path = os.path.abspath("dnn_model/yolov4.cfg")
class_path = os.path.abspath("dnn_model/classes.txt")
# !pip install --upgrade pip
# !pip install -r requirements.txt
# !pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt
# !pip3 install --upgrade tensorflow==2.4


# 1. Load Detector
yolov4 = ObjectDetection(weight_path, config_path)
yolov4.load_class_names(class_path)
yolov4.load_detection_model(image_size=832,  # 416 - 1280
                            nmsThreshold=0.4,
                            confThreshold=0.3)
# yolov5 = torch.hub.load('ultralytics/yolov5', 'yolov5s')


# 2. Load Tracker (Deepsort)
deep = Deep(max_distance=0.7,
            nms_max_overlap=1,
            n_init=3,
            max_age=15,
            max_iou_distance=0.7)
tracker = deep.sort_tracker()

def detect(model, frame):
    '''Given results from yolov5, extract classs ids, scores and boxes as numpy array'''

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



# capture frame
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    """ 1. Object Detection per frame"""
    # Question : Insert new model but will give error because its running on mps (need nvidia gpu)
    # >>>>>>>>>>>>>>>>>>>>>>>>>> yoloV5 >>>>>>>>>>>>>>>>>>
    # (class_ids, scores, boxes) = detect(yolov5, frame)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    (class_ids, scores, boxes) = yolov4.detect(frame)
    print(yolov4)
    print("class_ids>>>>>>>>>>>>>>", class_ids)
    print("scores>>>>>>>>>>>>>>", scores)
    print("boxes>>>>>>>>>>>>>>", boxes)

    """ 2. Object Tracking """
    features = deep.encoder(frame, boxes)
    detections = deep.Detection(boxes, scores, class_ids, features)

    tracker.predict()
    (class_ids, object_ids, boxes) = tracker.update(detections)
    print("after:class_ids>>>>>>>>>>>>>>", class_ids)
    print(type(class_ids))
    print("after:boxes>>>>>>>>>>>>>>", boxes)

    for class_id, object_id, box in zip(class_ids, object_ids, boxes):

        (x, y, x2, y2) = box
        class_name = yolov4.classes[class_id]
        color = yolov4.colors[class_id]

        cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
        cv2.rectangle(frame, (x, y), (x + len(class_name)
                      * 20, y - 30), color, -1)
        cv2.putText(frame, class_name + " " + str(object_id),
                    (x, y - 10), 0, 0.75, (255, 255, 255), 2)

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
