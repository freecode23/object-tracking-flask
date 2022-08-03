import React, { useState } from 'react'
import Video from '../../components/video/Video';
import Buttons from '../../components/buttons/Buttons';
import Chart from '../../components/chart/Chart';
function Home() {

    const [version, setVersion] = useState("v4")
    const handleClick = async (e) => {
        e.preventDefault();
        setVersion(e.target.value)
    }
    return (
        <>
            <div>
                <h1>OBJECT TRACKING</h1>
                <h3>{`version used: ${version}`}</h3>
                <Video version={version}/>
                <Buttons handleClick={handleClick}/>
                <Chart />
            </div>
        </>
    )
}

export default Home