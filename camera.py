import cv2

class Video(object):
    def __init__(self):
        self.video=cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
        
    def get_frame(self):
        success, frame=self.video.read()
        if not success:
            print("no frame captured")
            return
        ret, jpg= cv2.imencode(".jpg", frame)
        return jpg.tobytes()
    
    def get_tracked_frame(self, yoloDeepSort, version):
        sucess, frame = self.video.read()
        if not sucess:
            print("no frame captured")
            return
        
        frame = yoloDeepSort.process_frame(frame, version)
        
        # convert result to byte
        ret, jpg = cv2.imencode(".jpg", frame)
        return jpg.tobytes()
