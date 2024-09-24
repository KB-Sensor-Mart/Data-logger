import React from 'react';
import ReactDOM from 'react-dom';
import AppRouter from './App';
import './App.css';
import reportWebVitals from './reportWebVitals';
import { IPProvider } from './components/IpContext';

ReactDOM.render(
  <React.StrictMode>
    <IPProvider>
      <AppRouter />
    </IPProvider>
  </React.StrictMode>,
  document.getElementById('root')
);

reportWebVitals();
