import React from "react";
import './App.css';
import Login from "./components/Login";
import Admin from "./components/Admin"
import Register from "./components/Register";
import Home from "./components/Home";
import { BrowserRouter, Route, Routes, } from "react-router-dom";


const AppRouter = () => (

  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/Admin" element={<Admin />} />
      <Route path="/Register" element={<Register />} />
     </Routes>
  </BrowserRouter>
);

export default AppRouter;
