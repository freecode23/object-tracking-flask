from flask import Flask, render_template, Response
from YoloDeepSort import Tracker
from camera import Video 

app=Flask(__name__)

# create home route
@app.route("/")
def index():
    return render_template('index.html')


def generate_frame(camera):
    yoloDeepSort = Tracker()
    while True:
        # detect and track
        frame = camera.get_tracked_frame(yoloDeepSort)
        yield(b'--frame\r\n'
              b'Content-Type:  image/jpeg\r\n\r\n' + frame +
              b'\r\n\r\n')

# get image from video
@app.route("/video")
def video():
    
    # return frame
    return Response(generate_frame(Video()),
    mimetype = 'multipart/x-mixed-replace; boundary=frame')

app.run(debug=True)