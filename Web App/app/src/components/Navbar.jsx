import React, { useEffect, useState } from "react";
import { TiThMenuOutline } from "react-icons/ti";
import { useNavigate } from "react-router-dom";
import Swal from 'sweetalert2';
import axios from 'axios';
import { useIp } from "./IpContext";

const Navbar = () => {
  const [isOpenMenu, setOpenMenu] = useState(false);
  const {ipAddress} = useIp();
  const navigate = useNavigate();

  const handleToggleMenu = () => {
    setOpenMenu(!isOpenMenu);
  };


const handleShutdown = async (e) => {
  e.preventDefault();

  // Show the confirmation dialog
  Swal.fire({
    title: 'Are you sure?',
    text: "Do you really want to shut down the system?",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, shut down',
    cancelButtonText: 'Cancel'
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        // Trigger the shutdown command only if the user confirms
        const res = await axios.post(`http://${ipAddress}:8000/shutdown`);

        console.log('Backend response:', res.data); // Debugging line

        if (res.data.message === "Shutdown command issued") {
          // After confirming the shutdown, show the timer
          Swal.fire({
            title: 'Shutdown Initiated',
            html: 'System will shut down in <b>5</b> seconds.<br/>You can remove power after that.',
            icon: 'success',
            timer: 5000, // Set the timer for 5 seconds
            timerProgressBar: true,
            didOpen: () => {
              const b = Swal.getHtmlContainer().querySelector('b');
              let timerInterval = setInterval(() => {
                const remainingTime = Math.round(Swal.getTimerLeft() / 1000); // Get remaining time in seconds
                b.textContent = remainingTime;
              }, 1000);
              Swal.showLoading();
              
              const timeLeft = Swal.getTimerLeft();
              console.log(timeLeft);
            },
            willClose: () => {
              // Perform any additional actions after the timer ends, if necessary
            }
          });
        } else if (res.data.message === "unauthorized") {
          // Handle unauthorized shutdown attempt
          Swal.fire({
            title: 'Error!',
            text: `Unable to shutdown`,
            icon: 'error',
            confirmButtonText: 'OK'
          });
        }

      } catch (err) {
        console.error('Error:', err);

        // SweetAlert for general error
        Swal.fire({
          title: 'Error!',
          text: 'An error occurred. Please try again.',
          icon: 'error',
          confirmButtonText: 'OK'
        });
      }
    }
  });
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
    <button className="text-white rounded text-bold p-1 bg-red-600 text-black hover:bg-green-500 transition duration-300" onClick={handleShutdown}>Shutdown</button>
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
