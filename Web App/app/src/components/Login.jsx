import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useIp } from './IpContext';

const Login = () => {
  const [values, setValues] = useState({
    username: '',
    password: '',
  });
  const navigate = useNavigate();
  const { ipAddress } = useIp();

  // Check for token and expiry time on component mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    const expiryTime = localStorage.getItem('expiryTime');

    if (token && expiryTime) {
      const now = Date.now();
      if (now < Number(expiryTime)) {
        // Token is valid, navigate to the next page
        navigate('/home');
      } else {
        // Token expired, clear it from localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('expiryTime');
        Swal.fire({
          title: 'Session Expired!',
          text: 'Please log in again.',
          icon: 'warning',
          confirmButtonText: 'OK',
        });
      }
    }
  }, [navigate]);


  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await axios.post(`http://${ipAddress}:8000/api/login`, values);

      if (res.data.message === 'Login successful') {
        const { token, expiryTime } = res.data;

        localStorage.setItem('token', token);
        localStorage.setItem('expiryTime', new Date(expiryTime).getTime());

        navigate('/home');
      } else {
        Swal.fire({
          title: 'Error!',
          text: res.data.message || 'Invalid credentials',
          icon: 'error',
          confirmButtonText: 'OK',
        });
      }
    } catch (err) {
      console.error('Error:', err);
      Swal.fire({
        title: 'Error!',
        text: 'An error occurred. Please try again.',
        icon: 'error',
        confirmButtonText: 'OK',
      });
    }
  };

  return (
    <>
      <div className="flex flex-col min-h-screen">
        <Navbar />

        {/* Main Section - Center the login form */}
        <div className="flex-1 flex items-center pt-5 pb-5 justify-center bg-gradient-to-b from-indigo-50">
          <div className="flex flex-col md:flex-row items-center justify-center rounded-lg w-full max-w-4xl">
            <div className="w-full md:w-[35rem] animate-bounce bg-gradient-to-b from-indigo-10 hidden md:block flex justify-center">
              <img src="./images/newlogin.png" alt="Login" />
            </div>
            <div className="bg-blue-400 w-full md:w-[20rem] p-7 shadow-xl bg-white h-[30rem] md:h-[35rem] rounded-r-lg">
              <form className="flex flex-col justify-center items-center" onSubmit={handleSubmit}>
                <label htmlFor="email" className="block mb-10 text-3xl font-bold font-large text-blue-900">LOG-IN</label>
                <div className="mb-5 w-full">
                  <label className="block mb-2 text-sm font-medium text-gray-900">Username</label>
                  <input
                    id="email"
                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    placeholder="Username"
                    onChange={e => setValues({ ...values, username: e.target.value })}
                    required
                  />
                </div>
                <div className="mb-5 w-full">
                  <label htmlFor="password" className="block mb-2 text-sm font-medium text-gray-900">Password</label>
                  <input
                    type="password"
                    id="password"
                    placeholder="******"
                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                    onChange={e => setValues({ ...values, password: e.target.value })}
                    required
                  />
                </div>
                
                <div className="flex items-start mb-5 w-full">
                  <a href="/Reset-password" className="font-medium text-blue-600 hover:underline">Change Password</a>
                </div>
                <button type="submit" className="text-white bg-yellow-400 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full px-5 py-2.5 text-center">Submit</button>
              </form>
            </div>
          </div>
        </div>

        <Footer />
      </div>
    </>
  );
};

export default Login;

