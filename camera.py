import cv2
from YoloDeepSort import Tracker

class Video(object):
    def __init__(self):
        self.video=cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
        
    def get_frame(self):
        ret, frame=self.video.read()
        if not ret:
            print("no frame captured")
            return
        ret, jpg= cv2.imencode(".jpg", frame)
        return jpg.tobytes()
    
    
  