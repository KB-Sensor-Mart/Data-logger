import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import OfflineCaptcha from '../components/Captcha'; // Ensure correct path
import Swal from 'sweetalert2';

const Login = () => {
  const [values, setValues] = useState({
    email: '',
    password: '',
  });
  const [captchaValid, setCaptchaValid] = useState(false);
  const navigate = useNavigate();

  axios.defaults.withCredentials = true;

  const handleCaptchaValidation = (isValid) => {
    setCaptchaValid(isValid);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (captchaValid) {
      Swal.fire({
        title: 'CAPTCHA Required',
        text: 'Please solve the CAPTCHA first.',
        icon: 'warning',
        confirmButtonText: 'OK',
      });
      return;
    }

    try {
      const res = await axios.post('http://localhost:5001/api/auth/login', values, {
        withCredentials: true, // Ensure credentials are included
      });

      console.log('Backend response:', res.data); // Add this line for debugging

      if (res.data.status === "success") {
        navigate('/home');
      } else {
        Swal.fire({
          title: 'Incorrect Password or Email',
          text: res.data.Message || '',
          icon: 'error',
          confirmButtonText: 'Back',
        });
      }
    } catch (err) {
      console.log('Error logging in', err);
      Swal.fire({
        title: 'Error logging in',
        text: 'An unexpected error occurred. Please try again later.',
        icon: 'error',
        confirmButtonText: 'Back',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 flex items-center justify-center p-4">

      <div className="flex flex-col md:flex-row items-center justify-center rounded-lg">
        <div className="w-full md:w-[35rem] hidden md:block flex justify-center">
          <img src="./images/login.png" alt="Login" className="w-full max-w-none h-[30rem] md:h-[35rem] shadow-xl rounded-l-lg md:rounded-l-lg" />
        </div>
        <div className="w-full md:w-[20rem] relaive p-7 shadow-xl bg-white h-[30rem] md:h-[35rem] rounded-r-lg md:rounded-r-lg">
          <form className="flex flex-col justify-center items-center" onSubmit={handleSubmit}>
  
            <label htmlFor="email" className=" block mb-10 text-xl font-large text-blue-900">LOG-IN</label>
            <div className="mb-5 w-full">
              <label className="block mb-2 text-sm font-medium text-gray-900">Username</label>
              <input
                id="email"
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                placeholder="Username"
                onChange={e => setValues({ ...values, email: e.target.value })}
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

            <OfflineCaptcha onCaptchaValid={handleCaptchaValidation} />
            <div className="flex items-start mb-5 w-full">
              <a href="/Reset-password" className="font-medium text-blue-600 hover:underline">Change Password</a>
            </div>
            <button type="submit" className="text-white bg-yellow-400 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center">Submit</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
