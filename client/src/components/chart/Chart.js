import axios from 'axios'
import React, { useEffect, useState } from 'react'

function Charts() {

  const [time, setTime]=useState()
  const [stdev, setStdev]=useState()

  useEffect(()=> {
    const myInterval = setInterval(fetchConfidences, 5000);

    return () => {
      // should clear the interval when the component unmounts
      clearInterval(myInterval);
    };

  }, [])

  const fetchConfidences = async () => {
    const fetchedConf = await axios.get("/stdev")
    console.log("fethced seconds", fetchedConf.data.seconds);
    console.log("fethced Conf", fetchedConf.data.conf_stdev);
    setTime(fetchedConf.data.seconds)
    setStdev(fetchedConf.data.conf_stdev)
  }

  return (
    <>
      <div>{`${time}`}</div>
      <div>{`${stdev}`}</div>
    </>
  )
}

export default Charts