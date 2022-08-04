import React from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home/Home";
function App() {
  
  return (
    <>
      <Router>
        <Routes>
          {/* <Route
            path="/"
            element={<div><Home /></div>}
          /> */}
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