import React, { useState } from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';
import { useNavigate } from 'react-router-dom';
import {useIp} from './IpContext'


const ChangePassword = () => {
  
  const [values, setValues] = useState({
    username: '',
    newPassword: '',
  });

  const navigate = useNavigate();
  const {ipAddress} = useIp();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!values.username || !values.newPassword) {
      Swal.fire({
        title: 'Error',
        text: 'Please fill in both fields.',
        icon: 'error',
        confirmButtonText: 'OK',
      });
      return;
    }

    try {
      const res = await axios.post(`http://${ipAddress}:8000/api/reset-password`, {
        username: values.username,
        new_password: values.newPassword,
      });

      console.log('Backend response:', res.data); // Debugging

      if (res.data.message === "Password reset successful") {
        navigate('/');
      } else {
                Swal.fire({
          title: 'Error!',
          text: `Incorrect Username: ${res.data.Message || ''}`,
          icon: 'error',
          confirmButtonText: 'OK'
        });
      }

    } catch (err) {
      console.error('Error:', err);
      window.alert('Error occured in changing password. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 flex items-center justify-center p-4">
      <div className="flex flex-col md:flex-row items-center justify-center rounded-lg">
        <div className="w-full md:w-[35rem] hidden md:block flex justify-center">
          <img src="./images/resetpassword.png" alt="Reset Password" className="w-full max-w-none h-[30rem] md:h-[35rem] shadow-xl rounded-l-lg md:rounded-l-lg" />
        </div>
        <div className="w-full md:w-[20rem] relative p-7 shadow-xl bg-white h-[30rem] md:h-[35rem] rounded-r-lg md:rounded-r-lg">
          <form className="flex flex-col justify-center items-center" onSubmit={handleSubmit}>
            <label htmlFor="reset-password" className="block mb-10 text-xl font-large text-blue-900">RESET PASSWORD</label>
            <div className="mb-5 w-full">
              <label className="block mb-2 text-sm font-medium text-gray-900">Username</label>
              <input
                id="username"
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                placeholder="Username"
                onChange={e => setValues({ ...values, username: e.target.value })}
                required
              />
            </div>
            <div className="mb-5 w-full">
              <label htmlFor="new-password" className="block mb-2 text-sm font-medium text-gray-900">New Password</label>
              <input
                type="password"
                id="new-password"
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
    </div>
  );
};

export default ChangePassword;
