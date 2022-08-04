import axios from 'axios'
import React, { useEffect, useState } from 'react'

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
  const labels = ["January", "February", "March", "April", "May", "June", "July"];

  const data = {
    labels,
    datasets: [
      {
        label: 'Dataset 1',
        data: [1, 2, 3, 4, 5, 6, 7, 8, 99, 0],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      }
    ],
  };


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
      <Line data={data} />
    </>
  )
}


export default Chart;