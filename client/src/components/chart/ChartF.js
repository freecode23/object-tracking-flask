import React from "react";
import { Line } from "react-chartjs-2";

const labels = ["January", "February", "March", "April", "May", "June", "July"];

export const data = {
    labels,
    datasets: [
        {
            label: "Dataset 1",
            data: [6, 16, 22, 14, 10, 123, 123, 124],
            borderColor: "rgb(255, 99, 132)",
            backgroundColor: "rgba(255, 99, 132, 0.5)"
        }
    ]
};

function ChartF() {
    return (
        <>
            <p>Hello</p>
            {/* <Line data={data} />; */}
        </>
    )
}


export default ChartF