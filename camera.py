import cv2

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
    
    def get_tracked_frame(self, yoloDeepSort):
       
        ret, frame = self.video.read()
        if not ret:
            print("no frame captured")
            return
        
        frame = yoloDeepSort.process_frame(frame)

        # convert result to byte
        ret, jpg = cv2.imencode(".jpg", frame)
        return jpg.tobytes()
