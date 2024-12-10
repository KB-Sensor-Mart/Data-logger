import React, { useEffect, useState } from "react";
import './App.css';
import Login from "./components/Login";
import Admin from "./components/Admin";
import Home from "./components/Home";
import Graph from "./components/Graph";
import Changepass from "./components/Changepass";
import ProtectedRoute from "./components/protectedRoutes"; 
import { Route, Routes, useNavigate } from "react-router-dom";

const AppRouter = () => {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(() => {
      const token = localStorage.getItem("token");
      const expiryTime = localStorage.getItem("expiryTime");

      if (token && expiryTime && Date.now() > Number(expiryTime)) {
        // Token expired, clear storage and redirect to login
        localStorage.removeItem("token");
        localStorage.removeItem("expiryTime");
        navigate("/");
      }
    }, 1000); // Check every second

    return () => clearInterval(interval); // Cleanup on component unmount
  }, [navigate]);

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 800);
  }, []);
  
  return (
    <>
      {loading ? (
        <div className="flex items-center justify-center h-screen">
          <img src="./images/file.png" alt="Loading..." className="w-20 h-20 animate-spin" />
        </div>
      ) : (
        <Routes>
          <Route path="/" element={<Login />} />
          <Route
            path="/Home"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />
          <Route
            path="/Live graph"
            element={
              <ProtectedRoute>
                <Graph />
              </ProtectedRoute>
            }
          />
          <Route
            path="/Admin"
            element={
              <ProtectedRoute>
                <Admin />
              </ProtectedRoute>
            }
          />
          <Route path="/Reset-password" element={<Changepass />} />
        </Routes>
      )}
    </>
  );
};

export default AppRouter;
