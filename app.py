from flask import Flask,  Response, render_template, redirect, url_for, request
from object_tracker import Tracker
from camera import Video 

app=Flask(__name__)

# create home route
@app.route("/")
def index():
    if (request.args.to_dict() == {}):
        version="v4"
    else:
        version = request.args.get("version")
    return render_template('index.html', value=version)


def generate_frames(camera, version="v4"):
    yoloDeepSort = Tracker(version)

    while True:
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
        return redirect(url_for('index', version=version))

    elif request.method == 'GET':
        return Response(generate_frames(Video(), request.args.get("version")),
        mimetype = 'multipart/x-mixed-replace; boundary=frame')

app.run(host="0.0.0.0", port=80, debug=True)