import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import Swal from 'sweetalert2';

const ChangePassword = () => {
  const [values, setValues] = useState({
    email: '',
    newPassword: ''
  });
  const navigate = useNavigate();

  axios.defaults.withCredentials = true;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const res = await axios.post('http://localhost:5001/api/auth/change-password', values, {
        withCredentials: true,
      });

      console.log('Backend response:', res.data);  // Add this line for debugging

      if (res.data.status === "success") {
        Swal.fire({
          title: 'Password Changed Successfully',
          text: res.data.message || '',
          icon: 'success',
          confirmButtonText: 'OK'
        }).then(() => {
          navigate('/');
        });
      } else {
        Swal.fire({
          title: 'Error Changing Password',
          text: res.data.message || '',
          icon: 'error',
          confirmButtonText: 'Try Again'
        });
      }
    } catch (err) {
      console.log('Error changing password', err);
      Swal.fire({
        title: 'Error Changing Password',
        text: 'An unexpected error occurred. Please try again later.',
        icon: 'error',
        confirmButtonText: 'Back'
      });
    }
  };

  return (
    <body className="min-h-screen bg-gradient-to-b from-indigo-50 flex items-center justify-center p-4">
      <div className="flex flex-col md:flex-row items-center justify-center rounded-lg">
        <div className="w-full md:w-[35rem] hidden md:block flex justify-center">
          <img src="./images/signup.jpg" alt="Change Password" className="w-full max-w-none h-[30rem] md:h-[35rem] shadow-xl rounded-l-lg md:rounded-l-lg" />
        </div>
        <div className="w-full md:w-[20rem] p-7 shadow-xl bg-white h-[30rem] md:h-[35rem] rounded-r-lg md:rounded-r-lg">
          <form className="flex flex-col justify-center items-center" onSubmit={handleSubmit}>
            <label htmlFor="change-password" className="block mb-10 text-xl font-large text-blue-900">CHANGE PASSWORD</label>
            <div className="mb-5 w-full">
              <label htmlFor="email" className="block mb-2 text-sm font-medium text-gray-900">Username</label>
              <input
                id="email"
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                placeholder="Username"
                onChange={e => setValues({ ...values, email: e.target.value })}
                required
              />
            </div>
            <div className="mb-5 w-full">
              <label htmlFor="newPassword" className="block mb-2 text-sm font-medium text-gray-900">New Password</label>
              <input
                type="password"
                id="newPassword"
                placeholder="******"
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                onChange={e => setValues({ ...values, newPassword: e.target.value })}
                required
              />
            </div>
            <button type="submit" className="text-white bg-yellow-400 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center">Submit</button>
          </form>
        </div>
      </div>
    </body>
  );
};

export default ChangePassword;
