import cv2
import numpy as np
from darknet_model import DarknetModel
from deep_sort.deep_sort import Deep
import torch
import torchvision
import os
import torchvision.transforms as T

# !pip install -r requirements.txt
# !pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt


class DetectorTracker(object):
    def __init__(self, version):
        # os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        weight_file = ""
        cfg_file = ""
        self.frcnn = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            pretrained=True)
        # 1. Load yolo
        if(version == "v7" or version == "v4"):
            if(version == "v7"):
                weight = "yolov7-tiny.weights"
                cfg = "yolov7-tiny.cfg"
            else:
                weight = "yolov4-tiny.weights"
                cfg = "yolov4-tiny.cfg"

            weight_file = os.path.abspath("model/weights_configs/" + weight)
            cfg_file = os.path.abspath("model/weights_configs/" + cfg)
            self.yolo = DarknetModel(
                weight_file, cfg_file)

            self.yolo.load_detection_model(image_size=416,  # 416 - 1280
                                           nmsThreshold=0.4,
                                           confThreshold=0.3)
            
        else:
            # need to do force_reload otherwise will give error because its running on mps (need nvidia gpu)
            self.yolov5 = torch.hub.load(
                'ultralytics/yolov5', 'yolov5s')

        # 2. load Classes
        self.classes = []
        self.colors = np.random.uniform(0, 255, size=(80, 3))
        self.load_class_names("model/weights_configs/classes.txt")
        
        # 0 classes for frcnn
        self.classes_frcnn = [
            '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
            'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
            'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
            'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

        # 3. Load Tracker (DeepSORT)
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

    def load_class_names(self, classes_path):
        with open(classes_path, "r") as file_object:
            for class_name in file_object.readlines():
                class_name = class_name.strip()
                self.classes.append(class_name)

    def get_prediction(self, frame):
        """
        get_prediction

            
        """
    
    def detect_frcnn(self, frame):
        #FRCNN
        # transform the image to tensor
        transform = T.Compose([
            T.ToTensor(),
        ])
        image = transform(frame)
        image = image.unsqueeze(0)  # add a batch dimension
        self.frcnn.eval()
        outputs = self.frcnn(image)  # get the predictions on the image
        # print the results individually
        # print(f"BOXES: {outputs[0]['boxes']}")
        # print(f"LABELS: {outputs[0]['labels']}")
        # print(f"SCORES: {outputs[0]['scores']}")
        # get all the predicited class names
        pred_class_ids = [class_id
                        for class_id in outputs[0]['labels'].cpu().numpy()]
        
        # get score for all the predicted objects
        pred_scores = outputs[0]['scores'].detach().cpu().numpy()

        # get all the predicted bounding boxes
        pred_bboxes = outputs[0]['boxes'].detach().cpu().numpy()
        threshold = 0.4
        # 1. get class ids
        class_ids=[]
        for i in range(len(pred_scores)):
            if(pred_scores[i] >= threshold):
                class_ids.append(pred_class_ids[i])
        
        # 2. get scores
        scores = pred_scores[pred_scores >=
                             threshold]
        
        # 3. get box x, y, w, h
        boxes_thresh = pred_bboxes[pred_scores >=
                                   threshold].astype(np.int32)
    
        boxes = []
        for i in range(len(boxes_thresh)):
            # get a single bounding box:
            x = boxes_thresh[i][0]
            y = boxes_thresh[i][1]
            width = boxes_thresh[i][2]-boxes_thresh[i][0]
            height = boxes_thresh[i][3]-boxes_thresh[i][1]
            
            box = []
            box.append(x)
            box.append(y)
            box.append(width)
            box.append(height)
            boxes.append(box)
        
        # Delete invalid
        invalid_index = {i for i in range(
            len(class_ids)) if class_ids[i] >= len(self.classes_frcnn)}
        boxes = [v for i, v in enumerate(boxes) if i not in invalid_index]
        scores = [v for i, v in enumerate(scores) if i not in invalid_index]
        class_ids = [v for i, v in enumerate(class_ids) if i not in invalid_index]

        return class_ids, scores, boxes
            
    def detect_yolov5(self, frame):
        """Given results from yolov5, extract classs ids, scores and boxes as numpy array"""
        yolov5 = self.yolov5
        results = yolov5(frame)
        
        result_pandas = results.pandas().xyxy[0]
        result_list = results.xyxy[0].cpu().detach().tolist()
        class_ids = []
        scores = [] 
        boxes = []

        for i in range(len(result_list)):
            class_ids.append(result_list[i][5])
            scores.append(result_list[i][4])

            # get a single bounding box:
            x = result_list[i][0]
            y = result_list[i][1]
            width = result_list[i][2]-result_list[i][0]
            height = result_list[i][3]-result_list[i][1]

            box = []
            box.append(x)
            box.append(y)
            box.append(width)
            box.append(height)
            boxes.append(box)

        class_ids = np.asarray(class_ids, dtype=np.int32)
        scores = np.asarray(scores, dtype=np.float64)
        boxes = np.asarray(boxes, dtype=np.float64)

        return class_ids, scores, boxes

    def detect_yolo(self, frame):
        """Detect the object in a given frame using yolov4 model and
        return the class ids, scores and boxes as numpy array"""
        return self.yolo.detect(frame)

    def create_detections_object(self, boxes, scores, class_ids, features):
        """Given results from yolov, and features create a detection object to perform Kalman filter measurement update"""
        return self.deep.Detection(
            boxes, scores, class_ids, features)

    def process_frame(self, frame, modelVersion):
        """ 1. Object Detection per frame"""
        if(modelVersion == "frcnn"):
            (class_ids, scores, boxes) = self.detect_frcnn(frame)
        elif(modelVersion =="v5"):
            (class_ids, scores, boxes)=self.detect_yolov5(frame)
        else:
            (class_ids, scores, boxes) = self.detect_yolo(frame)


        """ 2. Object Tracking """
        
        features = self.get_features(frame, boxes)
        detections = self.create_detections_object(
            boxes, scores, class_ids, features)
        self.kalman_predict()
        (class_ids, object_ids, boxes) = self.update_features(detections)
        
        # 1. get bounding box size in eaxh box
        frame_size = frame.shape[0] * frame.shape[1]
        box_sizes=[]
        for box in boxes:
            box_size = (box[2] * box[3]) / frame_size
            box_sizes.append(box_size)
            
        for class_id, object_id, box in zip(class_ids, object_ids, boxes):
            (x, y, x2, y2) = box
            
            if(modelVersion == "frcnn"):
                class_name = self.classes_frcnn[class_id]
            else:
                class_name = self.classes[class_id]
            color = self.colors[class_id]

            cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
            cv2.rectangle(frame, (x, y), (x + len(class_name)
                                          * 20, y - 30), color, -1)
            cv2.putText(frame, class_name + " " + str(object_id),
                        (x, y - 10), 0, 0.75, (255, 255, 255), 2)

        # 2. grab ids, scores, and sizes of each bounding box
        ids_scores_sizes ={}
        if(len(object_ids) > 0 and len(scores) > 0):

            # 3. use the length of minimum
            if(len(scores) >= len(object_ids)):
                # get ids, scores, and sizes depending on length of object_id
                for i in range(len(object_ids)):
                    ids_scores_sizes[object_ids[i]] = {
                        "score": scores[i],
                        "size": box_sizes[i]}
                    
                
            if(len(object_ids) > len(scores)):
                # get ids, scores, and sizes depending on length of scores
                for i in range(len(scores)):
                    ids_scores_sizes[object_ids[i]] = {
                                        "score": scores[i],
                                        "size": box_sizes[i]
                                        }

        # print("ids_scores_sizes:", ids_scores_sizes)
        return ids_scores_sizes, frame


def main():

    # capture frame
    cap = cv2.VideoCapture(0)

    # create YoloDeepSort tracker
    yoloDeepSort = DetectorTracker("v4")

    while True:
        # create frame
        ret, frame = cap.read()
        if not ret:
            break

        score, frame = yoloDeepSort.process_frame(frame, "v4")

        # show
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
