import React from 'react'

function Video(props) {

    return (
        <div>
            <img
                src={`http://localhost:4000/video_feed/${props.version}`}
                alt="Video"
                width="700"
            />
        </div>
    )
}

export default Video