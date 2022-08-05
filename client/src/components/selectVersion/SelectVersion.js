import React from 'react'
import "./selectVersion.css"

function SelectVersion(props) {

    return(
        <div >
        <p className='selectVersionLabel'>Click on version to display chart:</p>
            <form method="post" action="/video_feed">
                <button
                    className='versionButton v4'
                    type="submit"
                    value="v4"
                    name="action1"
                    onClick={props.handleSelectVersion}>
                    V4
                </button>
                <button
                    className='versionButton v5'
                    type="submit"
                    value="v5"
                    name="action1"
                    onClick={props.handleSelectVersion}>
                    V5
                </button>
                <button
                    className='versionButton v7'
                    type="submit"
                    value="v7"
                    name="action1"
                    onClick={props.handleSelectVersion}>
                    V7
                </button>
            </form>
        </div>
    )
}

export default SelectVersion