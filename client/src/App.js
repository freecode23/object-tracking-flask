import React, {useEffect, useState} from 'react'
import axios from "axios";
function App() {
  const [data, setData] = useState()

  // useEffect(() => {
  //   const fetchMembers = async () => {
  //     const fetchedMembers = await axios.get("/video");
  //     if (fetchedMembers.data) {
  //       setData(fetchedMembers.data)
  //       console.log("data>>", fetchedMembers.data);
  //     }
  //   };
  //   fetchMembers();
  // }, []) 
  return (
    <div>
    <img
        src="http://localhost:4000/video_feed"
      alt="Video"
    /></div>
  )
}

export default App