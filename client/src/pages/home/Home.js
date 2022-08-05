import React, { useState } from 'react'
import Video from '../../components/video/Video';
import SelectVersion from '../../components/selectVersion/SelectVersion';
import Chart from '../../components/chart/Chart';
import "./home.css"
function Home() {

    const [version, setVersion] = useState("v4")
    const [isClearChart, setClearChart] = useState(false)

    const handleSelectVersion = async (e) => {
        e.preventDefault();
        setVersion(e.target.value)
        setClearChart(false)
    }

    const handleClearChart = async (e) => {
        e.preventDefault();
        setClearChart(true)
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
                    <Video version={version} />
                    <Chart
                    isClearChart={isClearChart}
                    handleClearChart={handleClearChart} />
                </div>
            </div>
        </>
    )
}

export default Home