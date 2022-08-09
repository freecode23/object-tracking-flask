import React, { useEffect, useState } from 'react'
import Video from '../../components/video/Video';
import SelectVersion from '../../components/selectVersion/SelectVersion';
import Chart from '../../components/chart/Chart';
import "./home.css"
function Home() {

    const [version, setVersion] = useState("none")
    const [isDetecting, setDetection] = useState(false)
    const [isClearChart, setClearChart] = useState(false)
    const [isWebcam, setIsWebCam] = useState(true)

    const handleSelectVersion = async (e) => {
        e.preventDefault();
        setVersion(e.target.value)
        setDetection(true)
        setClearChart(false)
    }

    const handleClearChart = async (e) => {
        e.preventDefault();
        setDetection(false)
        setVersion("none")
        setClearChart(true)
    }

    const handleToggleWebcam = async (e) => {
        e.preventDefault();
        setIsWebCam(!isWebcam)
        
    }

    // reset app if isDetecting change
    useEffect(() => {
    
    },[isDetecting])


    return (
        <>
            <div className="homeWrapper">
                <h1 className='homeTitle'>OBJECT TRACKING</h1>

                <div className='homeSelectVersion'>
                    <h3>
                        {`Model used: ${version}`}
                    </h3>
                    <SelectVersion handleSelectVersion={handleSelectVersion} />
                </div>
                
                
                <div className='homeContent'>
                    <div className='homeVideo'>
                        <button className='homeButton'
                    onClick={handleToggleWebcam}>
                    {isWebcam?
                        "Use mp4 Video" : "Use Webcam"}</button>
                    <Video version={version} isWebcam={isWebcam} isDetecting={isDetecting}/>
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