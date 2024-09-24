import React, { useState } from "react";
import { TiThMenuOutline } from "react-icons/ti";
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const [isOpenMenu, setOpenMenu] = useState(false);
  const navigate = useNavigate();

  const handleToggleMenu = () => {
    setOpenMenu(!isOpenMenu);
  };

  return (
   <nav className="w-full flex justify-between items-center p-4 bg-transparent backdrop-blur-md shadow-lg shadow-black/10 z-10">
  {/* Left side: Logo and Company Name */}
  <div className="flex items-center">
    <img src="./images/file.png" alt="Logo" className="w-[40px] animate-bounce-once h-auto mr-2" />
    <span className="text-lg text-black font-bold">Shri Pvt Ltd</span>
    <span className="m-2 text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400">BHU SENSE</span>
  </div>

  {/* Right side: Links or Hamburger Menu (depending on screen size) */}
  <div className="hidden md:flex space-x-4">
    <button className="text-black hover:text-gray-300 transition duration-300" onClick={() => navigate("/")}>Login</button>
    <button className="text-black hover:text-gray-300 transition duration-300" onClick={() => navigate("/admin")}>Admin</button>
    <button className="text-black hover:text-gray-300 transition duration-300" onClick={() => navigate("/register")}>Reset Password</button>
  </div>

  {/* Hamburger Menu Icon */}
  <div className="md:hidden">
    <TiThMenuOutline className="text-black text-2xl cursor-pointer" onClick={handleToggleMenu} />
  </div>

  {/* Dropdown Menu */}
  {isOpenMenu && (
    <div className="absolute top-[60px] right-4 bg-black shadow-lg rounded-lg flex flex-col space-y-2 p-4 z-50 md:hidden">
      <button className="text-white hover:text-gray-500 transition duration-300" onClick={() => navigate("/login")}>Login</button>
      <button className="text-white hover:text-gray-500 transition duration-300" onClick={() => navigate("/admin")}>Admin</button>
      <button className="text-white hover:text-gray-500 transition duration-300" onClick={() => navigate("/register")}>Register</button>
    </div>
  )}
</nav>

  );
};

export default Navbar;
