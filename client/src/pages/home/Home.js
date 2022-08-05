import React, { useState } from 'react'
import Video from '../../components/video/Video';
import Buttons from '../../components/selectVersion/SelectVersion';
import Chart from '../../components/chart/Chart';
import "./home.css"
function Home() {

    const [version, setVersion] = useState("v4")
    const handleClick = async (e) => {
        e.preventDefault();
        setVersion(e.target.value)
    }
    return (
        <>
            <div className="homeWrapper">
                <h1 className='homeTitle'>OBJECT TRACKING</h1>

                <div className='homeSelectVersion'>
                    <h3>
                        {`YOLO version used: ${version}`}
                    </h3>
                    <Buttons handleClick={handleClick} />
                </div>
                
                <div className='homeContent'>
                    <Video version={version} />
                    <Chart />
                </div>
            </div>
        </>
    )
}

export default Home