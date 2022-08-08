import cv2
import time
class Video(object):
    def __init__(self, isWebcam):
        if(isWebcam):
            self.video=cv2.VideoCapture(0)
        else:
            self.video = cv2.VideoCapture("videos/bangkok.mp4")
        self.fps=self.video.get(cv2.CAP_PROP_FPS)

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
        # 1. get frame
        sucess, frame = self.video.read()
        if not sucess:
            print("no frame captured")
            return
        
        
        # 2. process frame
        # get acc scores and sizes
        start = time.time()
        ids_scores_sizes, frame = yoloDeepSort.process_frame(
            frame, version)
        
        end = time.time()
        seconds = end-start

        # 3.  get fps
        num_frames = 1
        fps = num_frames / seconds
        
        cv2.putText(frame, "FPS: " + str(round(fps)), (50, 50),
                    cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0))
        
        # convert result to byte
        ret, jpg = cv2.imencode(".jpg", frame)
        return ids_scores_sizes, fps, jpg.tobytes()
