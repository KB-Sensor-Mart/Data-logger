import React, { useState } from 'react';

function OfflineCaptcha() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [input, setInput] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Function to generate a new math question
  const generateQuestion = () => {
    const num1 = Math.floor(Math.random() * 10) + 1;
    const num2 = Math.floor(Math.random() * 10) + 1;
    setQuestion(`${num1} + ${num2} = ?`);
    setAnswer(num1 + num2);
  };

  // Function to handle form submission
  const handleSubmit = (e) => {
    e.preventDefault(input);
    if (parseInt(input) === answer) {
      setErrorMessage('learn some Maths');
      alert('captcha passed')
      // Continue with form submission or other logic
    } else {
      setErrorMessage('Incorrect answer. Please try again.');
    }
  };

  // Generate a new question when the component mounts
  React.useEffect(() => {
    generateQuestion();
  }, []);

  return (
    <div className="captcha-container">
      <form onSubmit={handleSubmit}>
        <div>
           
          <label
          className=' text-white  hover:bg-blue-800 focus:ring-4 focus:outline-none  focus:ring-blue-300 font-medium rounded-sm text-sm w-full sm:w-auto px-2 py-1 text-center" bg-yellow-400 mb-[7rem]' >{question}</label>
          <input 
            className= " mt-3 bg-gray-100 border border-gray-300 text-gray-900 text-md rounded-sm focus:ring-blue-500 focus:border-blue-500 block w-auto "
            type="text"
            placeholder='Enter Captcha'
            value={input}
            onChange={(e) => setInput(e.target.value)}
            required
          />
        </div>
        <button id='sub' type="submit"></button>
        {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
      </form>
    </div>
  );
}

export default OfflineCaptcha;
