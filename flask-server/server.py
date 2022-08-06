
from flask import Flask, Response, jsonify, make_response, request
from model.detector_tracker import DetectorTracker
from camera import Video
from datetime import datetime

import sqlite3
import time
import numpy

app = Flask(__name__)
conn = sqlite3.connect("stdev.db")
cursor = conn.cursor()
sql_create_query = """ CREATE TABLE if not exists stdev (
    second string PRIMARY KEY,
    version string NOT NULL,
    confidence_stdev integer NOT NULL,
    size_stdev integer NOT NULL
)
"""
sql_drop_query = """drop table if exists stdev"""

cursor.execute(sql_drop_query)
cursor.execute(sql_create_query)


def db_connection():
    conn=None
    try:
        conn=sqlite3.connect("stdev.db")
    except sqlite3.error as e:
        print(e)
    return conn


def append_scores(ids_scores_sizes_all, ids_scores_sizes):
    '''Look for the id of the box in ids_scores all. If it doesnt exists
    create a new key and add the scores. If it exist, just append the single value. 
    Return the new dict with scores appended'''
    # if(ids_scores):
    #     for id, score in ids_scores.items():
    #         # if id already exist, just append
    #         if(id in ids_scores_all):
    #             ids_scores_all[id].append(score)
    #         else:
    #             ids_scores_all[id] = [score]
                
    if(ids_scores_sizes):
        for id, scores_sizes in ids_scores_sizes.items():
            score = scores_sizes['score']
            size = scores_sizes['size']
            
            # if id already exist, just append
            if(id in ids_scores_sizes_all):
                ids_scores_sizes_all[id]["scores"].append(score)
                ids_scores_sizes_all[id]["sizes"].append(size)
            else:
                ids_scores_sizes_all[id] = {"scores" : [score],
                                            "sizes": [size]}
                
    return ids_scores_sizes_all


def get_error_list(scores):
    '''Given a list of scores, create a list of error between a frame and the previous'''
    errors = []
    if(len(scores) > 1):
        for i in range(1, len(scores)):
            error = scores[i]-scores[i-1]
            errors.append(error)

    return errors


def get_mean_stds(ids_scores_sizes_all):
    '''For each box id, get error of scores and of sizes between 2 frames and add to a list.
    Return a dict of object id and error list'''
    conf_stds = []
    size_stds = []
    if(len(ids_scores_sizes_all) != 0):
        for id, scores_sizes in ids_scores_sizes_all.items():
            scores = scores_sizes["scores"]
            sizes = scores_sizes["sizes"]
            
            # loop through the scores and get error by id
            score_errors = get_error_list(scores)
            size_errors = get_error_list(sizes)

            # if there is error element, get standard deviation
            if(score_errors):
                conf_arr = numpy.array(score_errors)
                conf_std = numpy.std(conf_arr, axis=0)
                conf_stds.append(conf_std)
                
                size_arr = numpy.array(size_errors)
                size_std = numpy.std(size_arr, axis=0)
                size_stds.append(size_std)
                

    if(conf_stds):
        mean_conf_stds = (sum(conf_stds) / len(conf_stds))
        mean_size_stds = (sum(size_stds) / len(size_stds))
        return mean_conf_stds, mean_size_stds
    
    else:
        return -1, -1

def generate_frames(camera, version="v4"):
    '''Generate multiple frames and run tracking on the frames as long as the program runs'''
    print('tracker_version' , version)
    yoloDeepSort = DetectorTracker(version)

    ids_scores_all_frames = {}
    start = time.time()
    while True:
        # get first frame
        ids_scores_sizes, curr_frame = camera.get_tracked_frame(
            yoloDeepSort, version)

        # push scores
        ids_scores_all_frames = append_scores(
            ids_scores_all_frames, ids_scores_sizes)

        # Question: how to yield standard dev and frame and send it over to react
        # or save to database
        yield(b'--frame\r\n'
                    b'Content-Type:  image/jpeg\r\n\r\n' + curr_frame +
                    b'\r\n\r\n')

        end = time.time()
        if(end-start > 3):
            print("\nSTDEV AFTER 3 SECS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            mean_conf_stds, mean_size_stds = get_mean_stds(ids_scores_all_frames)
            mean_conf_stds, mean_size_stds = round(
                mean_conf_stds * 100, 3), round(mean_size_stds, 3)
            now = datetime.now()
            now_string = now.strftime("%H:%M:%S")
            
            # insert into db
            conn = db_connection()
            cursor = conn.cursor()
            sql_query = """INSERT INTO stdev 
                        (second, version, confidence_stdev, size_stdev)
                        VALUES (?, ?, ?, ?)"""
            cursor = cursor.execute(
                sql_query, (now_string, version, mean_conf_stds, mean_size_stds))
            conn.commit()
            
            print("mean conf stds>>>", mean_conf_stds)
            print("mean size stds>>>", mean_size_stds)
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


@app.route("/stdev/<isResetTable>", methods=['GET'])
def stdev(isResetTable):

    if request.method == 'GET':
        # 1. connect to db
        conn = db_connection()
        cursor = conn.cursor()
        stdev= {}
        if(isResetTable == "true"):
            sql_delete_all_query = "DELETE FROM stdev;"
            cursor.execute(sql_delete_all_query)
            conn.commit()
        else :
            cursor = conn.execute("SELECT * FROM stdev")
            stdev["seconds"] = []
            stdev["conf_stdev"] = []
            stdev["size_stdev"] = []
            stdev["versions"] = []
            
            # 2. grab standard dev
            # for each col
            for col in cursor.fetchall():
                stdev["seconds"].append(col[0])
                stdev["versions"].append(col[1])
                stdev["conf_stdev"].append(col[2])
                stdev["size_stdev"].append(col[3])
            
        if stdev is not None:
            return jsonify(stdev)

if __name__ == '__main__':
    # camera can work with HTTP only on 127.0.0.1
    # for 0.0.0.0 it needs HTTPS so it needs `ssl_context='adhoc'` (and in browser it need to accept untrusted HTTPS
    #app.run(host='127.0.0.1', port=5000)#, debug=True)
    app.run(host='0.0.0.0', port=4000, threaded=True,
            use_reloader=False)
        