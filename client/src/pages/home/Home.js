import React, { useState } from 'react'
import Video from '../../components/video/Video';
import SelectVersion from '../../components/selectVersion/SelectVersion';
import Chart from '../../components/chart/Chart';
import "./home.css"
function Home() {

    const [version, setVersion] = useState("v4")
    const [isClearChart, setClearChart] = useState(false)
    const [isWebcam, setIsWebCam] = useState(true)

    const handleSelectVersion = async (e) => {
        e.preventDefault();
        setVersion(e.target.value)
        setClearChart(false)
    }

    const handleClearChart = async (e) => {
        e.preventDefault();
        setClearChart(true)
    }

    const handleToggleWebcam = async (e) => {
        e.preventDefault();
        setIsWebCam(!isWebcam)
        console.log("isWebcam", isWebcam)
    }


    return (
        <>
            <div className="homeWrapper">
                <h1 className='homeTitle'>OBJECT TRACKING</h1>

                <div className='homeSelectVersion'>
                    <h3>
                        {`YOLO version used: ${version}`}
                    </h3>
                    <SelectVersion handleSelectVersion={handleSelectVersion} />
                </div>
                
                
                <div className='homeContent'>
                    <div className='homeVideo'>
                        <button className='homeButton'
                    onClick={handleToggleWebcam}>
                    {isWebcam?
                        "Use mp4 Video" : "Use Webcam"}</button>
                    <Video version={version} isWebcam={isWebcam}/>
                    </div>
                    
                    <div className='homeChart'>
                        <Chart
                            isClearChart={isClearChart}
                            handleClearChart={handleClearChart} />
                    </div>

                </div>
            </div>
        </>
    )
}

export default Home