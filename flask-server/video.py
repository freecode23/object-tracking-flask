import cv2
import time
class Video(object):
    def __init__(self, isWebcam):
        self.isWebcam = isWebcam
        if(isWebcam):
            self.cap=cv2.VideoCapture(0)
        else:
            self.cap = cv2.VideoCapture("videos/traffic.mp4")

            # Get length of the video.
            self.video_length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Initialize count.
            self.current_count = 0
            
        self.fps=self.cap.get(cv2.CAP_PROP_FPS)

    def __del__(self):
        self.cap.release()
        
    def get_frame(self):
        # print("self.isWebcam", self.isWebcam)
        if(not self.isWebcam):
            # print("self.current_count", self.current_count)
            # print("self.video length", self.video_length)
            # Check length of the video.
            if self.current_count == self.video_length:
                # Reset to the first frame. Returns bool.
                _ = self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.current_count = 0
        
        success, frame=self.cap.read()
        if not success:
            print("no frame captured")
            return
        ret, jpg= cv2.imencode(".jpg", frame)
        if(not self.isWebcam):
            self.current_count += 1 
        return jpg.tobytes()
    
    def get_tracked_frame(self, yoloDeepSort, version):
        if(not self.isWebcam):
            # Check length of the video.
            if self.current_count == self.video_length:
                # Reset to the first frame. Returns bool.
                _ = self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.current_count = 0
        
        # 1. get frame
        sucess, frame = self.cap.read()
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
        if(not self.isWebcam):
            self.current_count += 1 
        return ids_scores_sizes, fps, jpg.tobytes()
