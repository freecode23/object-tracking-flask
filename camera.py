import cv2
import time
class Video(object):
    def __init__(self):
        self.video=cv2.VideoCapture(0)
        self.fps=self.video.get(cv2.CAP_PROP_FPS)
        # print("Frames per second camera: {0}".format(self.fps))
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
        
        # 2. start time
        start = time.time()
        
        # 3. process frame
        ids_scores, frame = yoloDeepSort.process_frame(frame, version)
        
        # 4. time elapsed
        end = time.time()
        seconds = end-start

        # 5. fps
        num_frames = 1
        fps = num_frames / seconds
        
        cv2.putText(frame, "FPS: " + str(round(fps)), (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0))
        
        # convert result to byte
        ret, jpg = cv2.imencode(".jpg", frame)
        return ids_scores, jpg.tobytes()
