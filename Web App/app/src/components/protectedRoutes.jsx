import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  const expiryTime = localStorage.getItem("expiryTime");

  // Check if the token is valid
  if (!token || !expiryTime || Date.now() > Number(expiryTime)) {
    // If no valid token, redirect to login
    localStorage.removeItem("token");
    localStorage.removeItem("expiryTime");
    return <Navigate to="/" />;
  }

  // Render the child component if authorized
  return children;
};

export default ProtectedRoute;
        
