import React, { useState } from "react";
import { TiThMenuOutline } from "react-icons/ti";
import { useNavigate } from "react-router-dom";
import Swal from 'sweetalert2';
import axios from 'axios';
import { useIp } from "./IpContext";

const Navbar = () => {
  const [isOpenMenu, setOpenMenu] = useState(false);
  const [isShuttingDown, setIsShuttingDown] = useState(false); // For shutdown state
  const { ipAddress } = useIp();
  const navigate = useNavigate();

  const handleToggleMenu = () => {
    setOpenMenu(!isOpenMenu);
  };

  const handleShutdown = async (e) => {
    e.preventDefault();

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

          if (res.data.message === "Shutdown command issued") {
            // Show shutdown animation or message before the actual shutdown
            setIsShuttingDown(true);

            // Wait for 5 seconds before turning off the UI completely
            setTimeout(() => {
              document.body.innerHTML = ''; // Clears the entire UI
            }, 5000); // 5-second delay
          } else if (res.data.message === "unauthorized") {
            Swal.fire({
              title: 'Error!',
              text: 'Unable to shutdown',
              icon: 'error',
              confirmButtonText: 'OK'
            });
          }

        } catch (err) {
          console.error('Error:', err);
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
    <div>
      {isShuttingDown ? (
<div className="shutdown-screen h-screen flex flex-col justify-center items-center bg-sky-400 text-center">
  <div className="loader border-t-4 border-white border-solid rounded-full w-16 h-16 animate-spin mb-4"></div>
  <h1 className="text-3xl font-bold">System Shutting Down...</h1>
  <p className="text-xl mt-2">Goodbye!</p>
</div>

      ) : (
        <nav className="w-full flex justify-between items-center p-4 bg-transparent backdrop-blur-md shadow-lg shadow-black/10 z-10">
          <div className="flex items-center">
            <img src="./images/file.png" alt="Logo" className="w-[40px] animate-bounce-once h-auto mr-2" />
            <span className="text-lg text-black font-bold">Shri Pvt Ltd</span>
            <span className="m-2 text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400">BHU SENSE</span>
          </div>

          <div className="hidden md:flex space-x-4">
            <button className="text-white rounded text-bold p-1 bg-red-600 text-black hover:bg-green-500 transition duration-300" onClick={handleShutdown}>Shutdown</button>
            <button className="text-black hover:text-gray-300 transition duration-300" onClick={() => navigate("/")}>Login</button>
            <button className="text-black hover:text-gray-300 transition duration-300" onClick={() => navigate("/admin")}>Admin</button>
            <button className="text-black hover:text-gray-300 transition duration-300" onClick={() => navigate("/register")}>Reset Password</button>
          </div>

          <div className="md:hidden">
            <TiThMenuOutline className="text-black text-2xl cursor-pointer" onClick={handleToggleMenu} />
          </div>

          {isOpenMenu && (
            <div className="absolute top-[60px] right-4 bg-black shadow-lg rounded-lg flex flex-col space-y-2 p-4 z-50 md:hidden">
                <button className="text-white rounded text-bold p-1 bg-red-600 text-black hover:bg-green-500 transition duration-300" onClick={handleShutdown}>Shutdown</button>
              <button className="text-white hover:text-gray-500 transition duration-300" onClick={() => navigate("/login")}>Login</button>
              <button className="text-white hover:text-gray-500 transition duration-300" onClick={() => navigate("/admin")}>Admin</button>
              <button className="text-white hover:text-gray-500 transition duration-300" onClick={() => navigate("/register")}>Register</button>
            </div>
          )}
        </nav>
      )}
    </div>
  );
};

export default Navbar;