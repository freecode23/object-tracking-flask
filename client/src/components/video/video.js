import React, {useEffect} from 'react'
import axios from "axios"

function Video(props) {
    // useEffect(() => {
    //   const fetchVideo = async() => {
    //       const vidFrame = await axios.get(`http://localhost:4000/video_feed/${props.version}`);
    //       console.log(vidFrame);
    //   }
    //   fetchVideo();
    // }, [props.version])
    
    return (
        <div>
            <img
                src={`http://localhost:4000/video_feed/${props.version}`}
                alt="Video"
                width="800"
            />
        </div>
    )
}

export default Video