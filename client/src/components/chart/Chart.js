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
  const [sessionResult, setSessionResult] = useState({})
  
  // 2. Get colors
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

  // 3. Init data to plot
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

  // 4. useEffect for interval
  useEffect(()=> {
    const myInterval = setInterval(fetchStdev, 3000);
    return () => {
      // should clear the interval when the component unmounts
      clearInterval(myInterval);
    };
  })

  // 5. useEffect for Mean values
  useEffect(()=> {
    const fetchMean = async() => {
      const res = await axios.get("/result")

      // 1. create map of version and the mean values
      const mapRes = Object.entries(res.data)
        .map(([version, means]) => {
          
          // get array
          const meanArr = Object.values(means).map((value, index) => {
            return value
          })              
 
          return [`${version}`, meanArr]
        })
      
      // 2. convert map to obejct
      const objectRes = Object.fromEntries(mapRes)
      setSessionResult(objectRes) 
    }

    if(props.isClearChart) {
      fetchMean();
    }
  }, [props.isClearChart])

  // 6. fetch 
  const fetchStdev = async () => {
    const fetchedStdev = await axios.get(`/stdev/${props.isClearChart}`)

    // X axis - time
    setLabels(fetchedStdev.data.seconds)

    // Y axis - confStdev
    setConf(fetchedStdev.data.conf_stdev)
    setSize(fetchedStdev.data.size_stdev)

    // set version
    setVersions(fetchedStdev.data.versions)
  }


  const versionHeaderJSX = Object.keys(sessionResult).map((version) => {
    // For each version create a header
    return (
      <th key={version} className="chartResultTableHeader">
        {version}
      </th>
    )
  })

  
  const confStdevJSX = Object.keys(sessionResult).map((version) => {
    // For each version:
    // - get the mean values
    const conf_stdev = sessionResult[version][0]
    const fps = sessionResult[version][1]
    const num_objects = sessionResult[version][2]
    const size_stdev = sessionResult[version][3]

    console.log("sessionResult[version]", sessionResult[version]);
    console.log("stdev...s", conf_stdev);
    // - create a single row
    return (
      <span key={version} className="chartResultVersion">
        <tr>
          <td>{conf_stdev}</td>
        </tr>

        <tr>
          <td>{fps}</td>
        </tr>

        <tr>
          <td>{num_objects}</td>
        </tr>

        <tr>
          <td>{size_stdev}</td>
        </tr>

      </span>
    )
  })


  // 8. Return
  return (
    <>
      <div className='chartWrapper'>
        <button
            className='chartClearButton'
            onClick={props.handleClearChart}>
              Reset Session
        </button>

        {props.isClearChart &&
          <div className='chartResultTable'>
            <table>
              <tr>
                <th>metric</th>
                {versionHeaderJSX}
              </tr>
                
              {confStdevJSX}
              
            </table>
          </div>
        }
     

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