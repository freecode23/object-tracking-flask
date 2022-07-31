from flask import Flask, render_template, Response, request
from YoloDeepSort import Tracker
from camera import Video 

app=Flask(__name__)

# create home route
@app.route("/")
def index():
    return render_template('index.html')


def generate_frames(camera, version="v4"):
    yoloDeepSort = Tracker(version)
    print("generate frames")
    while True:
        # detect and track
        frame = camera.get_tracked_frame(yoloDeepSort, version)
        yield(b'--frame\r\n'
              b'Content-Type:  image/jpeg\r\n\r\n' + frame +
              b'\r\n\r\n')

# get image from video
@app.route("/video", methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        if request.form.get('action1') == 'v4':
            version="v4"
        elif(request.form.get('action2') == 'v5'):
            version = "v5"
        else:
            version="v7"
            
        return Response(generate_frames(Video(), version),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
    elif request.method == 'GET':
        print("get")
        return Response(generate_frames(Video()),
        mimetype = 'multipart/x-mixed-replace; boundary=frame')

app.run(host="0.0.0.0", port=80, debug=True)