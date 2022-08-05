import React from 'react'
import "./button.css"

function Buttons(props) {

    return(
        <div>
            <form method="post" action="/video_feed">
                <button
                    type="submit"
                    value="v4"
                    name="action1"
                    onClick={props.handleClick}>
                    V4
                </button>
                <button
                    type="submit"
                    value="v5"
                    name="action1"
                    onClick={props.handleClick}>
                    V5
                </button>
                <button
                    type="submit"
                    value="v7"
                    name="action1"
                    onClick={props.handleClick}>
                    V7
                </button>
            </form>
        </div>
    )
}

export default Buttons