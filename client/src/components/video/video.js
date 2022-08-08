import React from 'react'

function Video(props) {

    return (
        <div>
            <img
                src={`http://localhost:4000/video_feed/query?version=${props.version}&isWebcam=${props.isWebcam}`}
                alt="Video"
                width="700px"
            />
        </div>
    )
}

export default Video