import React from "react";
import './App.css';
import Login from "./components/Login";
import Admin from "./components/Admin"
import Home from "./components/Home";
import Graph from "./components/Graph"
import Changepass from "./components/Changepass"
import { BrowserRouter, Route, Routes, } from "react-router-dom";


const AppRouter = () => (

  <BrowserRouter>
    <Routes>
    <Route path="/" element={<Login />} />
      <Route path="/Home" element={<Home />} />
      <Route path="/Live graph" element={<Graph/>}/>
      <Route path="/Admin" element={<Admin />} />
      <Route path="/Reset-password" element={<Changepass/>}  />
     </Routes>
  </BrowserRouter>
);

export default AppRouter;
