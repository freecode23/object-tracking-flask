import React from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home/Home";

function App() {
  // const [version, setVersion] = useState("v4")
  // const handleClick = async (e) => {
  //   e.preventDefault();
  //   setVersion(e.target.value)
  

  return (
    <>
      <Router>
        <Routes>
          <Route
            path="/"
            element={<div><Home /></div>}
          />
        </Routes>
      </Router>
    </>
  )
}

export default App