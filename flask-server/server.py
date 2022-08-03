
from flask import Flask, Response, render_template, redirect, url_for, request
from model.detector_tracker import DetectorTracker
from camera import Video
import time
import numpy

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.js')


def generate_frames(camera, version="v4"):
    '''Generate multiple frames and run tracking on the frames as long as the program runs'''
    yoloDeepSort = DetectorTracker(version)

    start = time.time()
    while True:
        # get first frame
        id_scores_box, curr_frame = camera.get_tracked_frame(
            yoloDeepSort, version)

        yield(b'--frame\r\n'
              b'Content-Type:  image/jpeg\r\n\r\n' + curr_frame +
              b'\r\n\r\n')



@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(Video()),
                           mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, threaded=True, use_reloader=False)
        