import React, { useState, useEffect } from "react";
import './App.css';
import Login from "./components/Login";
import Admin from "./components/Admin";
import Home from "./components/Home";
import Graph from "./components/Graph";
import Changepass from "./components/Changepass";
import { BrowserRouter, Route, Routes } from "react-router-dom";

const AppRouter = () => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate a loading time for the page (e.g., loading resources, etc.)
    setTimeout(() => {
      setLoading(false); // Change loading to false after 2 seconds (or adjust as necessary)
    }, 800);
  }, []);


 return (
    <div>
      {loading ? (
        // Show the loader while loading
        <div className="flex items-center justify-center h-screen">
          <img src="./images/file.png" alt="Loading..." className="w-20 h-20 animate-spin" />
        </div>
      ) : (
        // Show the routes when loading is complete
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/home" element={<Home />} />
            <Route path="/Live graph" element={<Graph />} />
            <Route path="/Admin" element={<Admin />} />
            <Route path="/Reset-password" element={<Changepass />} />
          </Routes>
        </BrowserRouter>
      )}
    </div>
  );
};

export default AppRouter;