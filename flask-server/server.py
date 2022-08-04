
from flask import Flask, Response, make_response, request
from model.detector_tracker import DetectorTracker
from camera import Video
import sqlite3
import time
import numpy

conn = sqlite3.connect("stdev.sqlite")
app = Flask(__name__)
def append_scores(ids_scores_all, id_score_box):
    '''Look for the id of the box in ids_scores all. If it doesnt exists
    create a new key and add the scores. If it exist, just append the single value. 
    Return the new dict with scores appended'''
    if(id_score_box):
        for id, score in id_score_box.items():
            if(id in ids_scores_all):
                ids_scores_all[id].append(score)
            else:
                ids_scores_all[id] = [score]
    return ids_scores_all


def get_error_list(scores):
    '''Given a list of scores, create a list of error between a frame and the previous'''
    errors = []
    if(len(scores) > 1):
        for i in range(1, len(scores)):
            error = scores[i]-scores[i-1]
            errors.append(error)

    return errors

def get_mean_stds(ids_scores_all):
    '''For each box id, get error scores between 2 frames and add to a list.
    Return a dict of object id and error list'''
    stds = []
    if(len(ids_scores_all) != 0):
        for id, scores in ids_scores_all.items():
            # loop through the scores and get error by id
            errors = get_error_list(scores)

            # if there is error element, get standard deviation
            if(errors):
                arr = numpy.array(errors)
                std = numpy.std(arr, axis=0)
                stds.append(std)

    if(stds):
        return sum(stds) / len(stds)
    else:
        return -1

def generate_frames(camera, version="v4"):
    '''Generate multiple frames and run tracking on the frames as long as the program runs'''
    print('tracker_version' , version)
    yoloDeepSort = DetectorTracker(version)

    ids_scores_all = {}
    start = time.time()
    while True:
        # get first frame
        id_scores_box, curr_frame = camera.get_tracked_frame(
            yoloDeepSort, version)

        # push scores
        ids_scores_all = append_scores(ids_scores_all, id_scores_box)

        # Question: how to yield standard dev and frame and send it over to react
        # or save to database
        yield(b'--frame\r\n'
                    b'Content-Type:  image/jpeg\r\n\r\n' + curr_frame +
                    b'\r\n\r\n')

        end = time.time()
        if(end-start > 3):
            print("\nSTDEV AFTER 3 SECS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            mean_stds = get_mean_stds(ids_scores_all)
            print(mean_stds * 100)
            # yield("helllo")
            start = time.time()
            
@app.route('/video_feed/<version>', methods=['GET', 'POST'])
def video_feed(version):
    # POST
    if request.method == 'POST':
        if request.form.get('action1') == 'v4':
            version="v4"
        elif(request.form.get('action2') == 'v5'):
            version = "v5"
        else:
            version="v7"
        return version

    # GET
    elif request.method == 'GET':
        # 1. single yield
        gen = generate_frames(Video(), version)
        
        # 2. wrap frame as response object        
        # multipart/x-mixed-replace is a single HTTP request response model.
        # If the network is interrupted, the video stream will be terminated abnormally and must be reconnected
        frame_res = Response(gen,
                       mimetype='multipart/x-mixed-replace; boundary=frame')
        return frame_res

if __name__ == '__main__':
    # camera can work with HTTP only on 127.0.0.1
    # for 0.0.0.0 it needs HTTPS so it needs `ssl_context='adhoc'` (and in browser it need to accept untrusted HTTPS
    #app.run(host='127.0.0.1', port=5000)#, debug=True)
    app.run(host='0.0.0.0', port=4000, threaded=True,
            use_reloader=False)
        