import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from "react-router-dom";


const Login = () => {
  const [values, setValues] = useState({
    email: '',
    password: ''
  });
  const navigate = useNavigate();

  axios.defaults.withCredentials = true;

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await axios.post('http://localhost:4001/login', values, {
        withCredentials: true, // Ensure credentials are included
      });

      if (res.data.status === "success") {
        navigate('/');
      } else {
        alert("No record found"); // Display an alert or handle the error appropriately
      }
    } catch (err) {
      console.error("Error logging in", err);
    }
  }

  return (

    <body class="h-screen bg-gradient-to-b from-indigo-50 flex items-center justify-center ">
  <div class="flex items-center justify-center rounded-lg space-x-0 ">
    
    <div class="w-[35rem] flex justify-center">
      <img src="./images/signup.jpg" alt="Login " class=" h-[35rem] shadow-xl" />
    </div>
    
    <div class="w-[20rem] p-7 shadow-xl bg-white h-[35rem]">
      <form class="flex flex-col justify-center items-center" onSubmit={handleSubmit} >
        <label for="email" class="block mb-10 text-xl font-large text-blue-900">SIGN-IN</label>
        <div class="mb-5 w-full">
          <label for="username" class="block mb-2 text-sm font-medium text-gray-900">username</label>
          <input
            type="username"
            id="username"
            placeholder="username"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            onChange={e => setValues({...values, password: e.target.value})}
            required
          />
        </div>
        <div class="mb-5 w-full">
        <label for="password" class="block mb-2 text-sm font-medium text-gray-900">Email</label>
          <input
            type="email"
            id="email"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            placeholder="Email-id"
            onChange={e => setValues({...values, email: e.target.value})}
            required
          />
        </div>
        <div class="mb-5 w-full">
          <label for="password" class="block mb-2 text-sm font-medium text-gray-900">Password</label>
          <input
            type="password"
            id="password"
            placeholder="******"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            onChange={e => setValues({...values, password: e.target.value})}
            required
          />
        </div>
        <div class="flex items-start mb-5 w-full">
          <a href="  " class="font-medium text-blue-600 hover:underline">Change Password</a>
        </div>
        <button type="submit" class="text-white bg-yellow-400 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center">Submit</button>
      </form>
    </div>
  </div>
</body>
  );
};

export default Login;
