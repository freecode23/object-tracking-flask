from flask import Flask, Response, jsonify, make_response, request
from model.detector_tracker import DetectorTracker
from video import Video
from datetime import datetime

import sqlite3
import time
import numpy
import csv
import pandas as pd
import json

app = Flask(__name__)
conn = sqlite3.connect("stdev.db")
cursor = conn.cursor()
sql_create_query = """ CREATE TABLE if not exists stdev (
    second string PRIMARY KEY,
    version string NOT NULL,
    confidence_stdev integer NOT NULL,
    size_stdev integer NOT NULL,
    fps integer NOT NULL,
    num_objects integer NOT NULL
)
"""
sql_drop_query = """drop table if exists stdev"""

cursor.execute(sql_drop_query)
cursor.execute(sql_create_query)

def db_connection():
    """create sqlite db connection"""
    conn=None
    try:
        conn = sqlite3.connect(
            "stdev.db", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    except sqlite3.error as e:
        print(e)
    return conn

def append_scores(ids_scores_sizes_all, ids_scores_sizes):
    '''Look for the id of the box in ids_scores all. If it doesnt exists
    create a new key and add the scores. If it exist, just append the single value. 
    Return the new dict with scores appended'''
                
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

def get_mean_result():
    # 1. connect to db
    conn = db_connection()
    cursor = conn.cursor()
    cursor = conn.execute("SELECT * FROM stdev")
    stdev={}
    stdev["conf_stdev"] = []
    stdev["size_stdev"] = []
    stdev["versions"] = []
    stdev["fps"]=[]
    stdev["num_objects"] = []
    
    # 2. grab standard dev rows
    # for each col
    for col in cursor.fetchall():
        stdev["versions"].append(col[1])
        stdev["conf_stdev"].append(col[2])
        stdev["size_stdev"].append(col[3])
        stdev["fps"].append(col[4])
        stdev["num_objects"].append(col[5])
        
    # 3. get mean by version
    df=pd.DataFrame(stdev)
    df_mean = df.groupby("versions").mean()
    result = df_mean.to_json(orient="index")
    parsed = json.loads(result)
    print("parsed>>>>", parsed)
    return parsed


def generate_frames(camera, version="v4"):
    '''Generate multiple frames and run tracking on the frames as long as the program runs'''
    yoloDeepSort = DetectorTracker(version)

    ids_scores_all_frames = {}
    fpss=[]
    num_objects=[]
    start = time.time()
    while True:
        # 1. get first frame
        ids_scores_sizes, fps, curr_frame = camera.get_tracked_frame(
            yoloDeepSort, version)

        # 2. push scores and fpss
        ids_scores_all_frames = append_scores(
            ids_scores_all_frames, ids_scores_sizes)
        fpss.append(fps)
        num_objects.append(len(ids_scores_sizes))

        # 3. return the frame
        yield(b'--frame\r\n'
                    b'Content-Type:  image/jpeg\r\n\r\n' + curr_frame +
                    b'\r\n\r\n')
        end = time.time()
        
        # 4. get std if its been 3 seconds
        if(end-start > 3):
            print("\nSTDEV AFTER 3 SECS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # 5. get mean stdev and mean fps and mean num objects
            mean_conf_stds, mean_size_stds = get_mean_stds(ids_scores_all_frames)
            mean_conf_stds, mean_size_stds = round(
                mean_conf_stds * 100, 3), round(mean_size_stds, 3)

            mean_fps = round(sum(fpss) / len(fpss), 3)
            mean_num_objects = round((sum(num_objects) / len(num_objects)), 3)
            
            # 6. if its a valid stdevs, insert into db
            if(mean_conf_stds > 0 or mean_size_stds > 0):
                # 7. prep the dates
                now = datetime.now()
                now_string = now.strftime("%H:%M:%S")
                
                # 8. insert into db
                conn = db_connection()

                cursor = conn.cursor()
                sql_query = """INSERT INTO stdev 
                            (second, version, confidence_stdev, size_stdev, fps, num_objects)
                            VALUES (?, ?, ?, ?, ?, ?)"""
                cursor = cursor.execute(
                    sql_query, (now_string, version, mean_conf_stds, mean_size_stds, mean_fps, mean_num_objects))
                conn.commit()
                
                # 9. download as csv
                db_df = pd.read_sql_query("SELECT * FROM stdev", conn)
                db_df.to_csv('csv/database.csv', index=False)

            # 9. restart timer from 0s
            start = time.time()
            
            # reset
            fpss = []
            num_objects = []

def generate_untracked_frames(camera):
    while True:
        curr_frame =camera.get_frame()

        yield(b'--frame\r\n'
              b'Content-Type:  image/jpeg\r\n\r\n' + curr_frame +
              b'\r\n\r\n')
    
@app.route('/video_feed/query/', methods=['GET'])
def video_feed():
   
    # GET
    if request.method == 'GET':
        # 1. check if using webcam
        isWebcamStr = request.args.get("isWebcam")
        isWebcam = True
        if(isWebcamStr == "false"):
                isWebcam = False

        # 2. check if detecting
        isDetecting = request.args.get("isDetecting")
        if(isDetecting == "true"):
            
            version = request.args.get("version")
            gen = generate_frames(Video(isWebcam), version)
        else:
            gen = generate_untracked_frames(Video(isWebcam))
                
        # 3. wrap frame as response object
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
            
            # 2. grab standard dev rows
            # for each col
            for col in cursor.fetchall():
                stdev["seconds"].append(col[0])
                stdev["versions"].append(col[1])
                stdev["conf_stdev"].append(col[2])
                stdev["size_stdev"].append(col[3])
            
        if stdev is not None:
            return jsonify(stdev)


@app.route("/result", methods=['GET'])
def result():
    return get_mean_result()


if __name__ == '__main__':
    # camera can work with HTTP only on 127.0.0.1
    # for 0.0.0.0 it needs HTTPS so it needs `ssl_context='adhoc'` (and in browser it need to accept untrusted HTTPS
    #app.run(host='127.0.0.1', port=5000)#, debug=True)
    app.run(host='0.0.0.0', port=4000, threaded=True,
            use_reloader=False)
        