import React from 'react'

function Video(props) {

    return (
        <div>
            <img
                src={`http://localhost:4000/video_feed/query?isDetecting=${props.isDetecting}&version=${props.version}&isWebcam=${props.isWebcam}&isNewSession=${props.isNewSession}`}
                alt="Video"
                width="700px"
            />
        </div>
    )
}

export default Video