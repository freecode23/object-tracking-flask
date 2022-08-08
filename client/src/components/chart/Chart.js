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

function Chart(props) {

  const [labels, setLabels] = useState([]) // x time
  const [confStdev, setConf] = useState([]) // y axis
  const [sizeStdev, setSize] = useState([]) // y axis
  const [versions, setVersions] = useState()
  
  const getColorAtx = (ctx) => {
    const rowIdx = ctx.p0.parsed.x
    if (versions[rowIdx] === "frcnn") {
      return 'rgb(128, 0, 128)'
    } else if (versions[rowIdx] === "v4") {
      return 'rgb(250, 0, 0)'
    } else if (versions[rowIdx] === "v5") {
      return 'rgb(0, 255, 0)'
    } else {
      return 'rgb(0, 0, 255)'
    }
  }



  // plot
  const ConfData = {
    labels,
    datasets: [
      {
        label: 'Confidence Standard Deviation(%) every 3 seconds interval',
        data: confStdev,
        backgroundColor: 'rgba(20, 20, 20, 0.5)', // dot
        segment: {
          borderColor: ctx => getColorAtx(ctx)
        }
      },
    ],
  };

  const SizeData = {
    labels,
    datasets: [
      {
        label: 'Size Standard Deviation (pixel) every 3 seconds interval',
        data: sizeStdev,
        backgroundColor: 'rgba(20, 20, 20, 0.5)', // dot
        segment: {
          borderColor: ctx => getColorAtx(ctx)
        }
      },
    ],
  };


  useEffect(()=> {
    const myInterval = setInterval(fetchConfStdev, 3000);

    return () => {
      // should clear the interval when the component unmounts
      clearInterval(myInterval);
    };

  })

  const fetchConfStdev = async () => {
    const fetchedConf = await axios.get(`/stdev/${props.isClearChart}`)

    // X axis - time
    setLabels(fetchedConf.data.seconds)

  
    // Y axis -confStdev
    setConf(fetchedConf.data.conf_stdev)
    setSize(fetchedConf.data.size_stdev)

    // set version
    setVersions(fetchedConf.data.versions)
    
  }



  return (
    <>
      <div className='chartWrapper'>
        <button
            className='chartClearButton'
            onClick={props.handleClearChart}>
              Clear Chart
        </button>

        <div>
          <Line data={ConfData} />
        </div>
        
        <div>
            <Line data={SizeData} />
        </div>
    </div>
    </>
  )
}


export default Chart;