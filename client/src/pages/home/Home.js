import React, { useState } from 'react'
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
                <img
                    src={`http://localhost:4000/video_feed/${version}`}
                    alt="Video"
                    width="800"
                />
            </div>

            <form method="post" action="/video_feed">
                <button
                    type="submit"
                    value="v4"
                    name="action1"
                    onClick={handleClick}>
                    V4
                </button>
                <button
                    type="submit"
                    value="v5"
                    name="action1"
                    onClick={handleClick}>
                    V5
                </button>
                <button
                    type="submit"
                    value="v7"
                    name="action1"
                    onClick={handleClick}>
                    V7
                </button>
            </form>
        </>
    )
}

export default Home