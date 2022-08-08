import React from 'react'
import "./selectVersion.css"

function SelectVersion(props) {

    return(
        <div >
        <p className='selectVersionLabel'>Click on version to display chart:</p>
                <button
                    className='versionButton frcnn'
                    type="submit"
                    value="frcnn"
                    onClick={props.handleSelectVersion}>
                    FRCNN
                </button>
                <button
                    className='versionButton v4'
                    type="submit"
                    value="v4"
                    onClick={props.handleSelectVersion}>
                    V4
                </button>
                <button
                    className='versionButton v5'
                    type="submit"
                    value="v5"
                    onClick={props.handleSelectVersion}>
                    V5
                </button>
                <button
                    className='versionButton v7'
                    type="submit"
                    value="v7"
                    onClick={props.handleSelectVersion}>
                    V7
                </button>
        </div>
    )
}

export default SelectVersion