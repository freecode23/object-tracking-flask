import axios from 'axios'
import React, { useEffect, useState } from 'react'
import "./chart.css"

// Chart JS
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

export const options = {
  responsive: true,
};

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function Chart() {

  const [time, setTime] = useState([])
  const [stdev, setStdev] = useState([])
  const [labels, setLabels] = useState([])
  const xydata = {
    labels,
    datasets: [
      {
        label: 'Dataset 1',
        data: stdev,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      }
    ],
  };

  // const [xydata, setXyData] = useState({})

  useEffect(()=> {
    const myInterval = setInterval(fetchConfidences, 3000);

    return () => {
      // should clear the interval when the component unmounts
      clearInterval(myInterval);
    };

  }, [])

  const fetchConfidences = async () => {
    const fetchedConf = await axios.get("/stdev")
    console.log("fethced seconds", fetchedConf.data.seconds);
    console.log("fethced Conf", fetchedConf.data.conf_stdev);
    // X axis - time
    setLabels(fetchedConf.data.seconds)

    // Y axis -stdev
    setStdev(fetchedConf.data.conf_stdev)

    // border color - depends on version


  }



  return (
    <>
      <div>{`${stdev}`}</div>
      <div className='chart-wrapper'>
        <Line data={xydata} />
      </div>
    </>
  )
}


export default Chart;