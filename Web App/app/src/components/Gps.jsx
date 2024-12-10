import React, { useState, useEffect } from 'react';
import { useIp }from './IpContext';

const GpsDataComponent = () => {

  const {ipAddress} = useIp();
  const [gpsData, setGpsData] = useState({
    date: 'N/A',
    time: 'N/A',
    latitude: 'N/A',
    longitude: 'N/A'
  });
  const [connectionError, setConnectionError] = useState(false);

  useEffect(() => {
    // Establish WebSocket connection to the backend
    const wsUrl = `ws://${ipAddress}:8000/ws/gps`;
    const socket = new WebSocket(wsUrl); 

    //Open websocket connection 
    socket.onopen = () => {
	console.log(`Connected to websocket at ${wsUrl}`);
        setConnectionError(false);
    };

    // Handle incoming WebSocket messages (GPS data updates)
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setGpsData(data);
      } catch (e) {
        console.error("Error parsing WebSocket message:", e);
      }
    };

    // Handle WebSocket errors
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
     setConnectionError(true);
    };

    // Handle WebSocket closure
    socket.onclose = (event) => {
      console.log("WebSocket connection closed:", event);
      setConnectionError(true);
    };

    // Close WebSocket connection when component unmounts
    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);


return (
  <div className="flex flex-col items-center gps-data-container p-4">
    <h2 className="text-xl font-semibold mb-4">GPS Data</h2>
    {connectionError && (
      <p className="text-red-500 mb-4">
        Error: Unable to connect to WebSocket server.
      </p>
    )}
    <div className="grid gap-4 text-lg text-center w-full max-w-3xl bg-white rounded-md shadow-sm p-4">
      {/* Responsive Layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Label and Value Pair */}
        <div>
          <div className="font-bold">Date:</div>
          <div>{gpsData.date}</div>
        </div>
        <div>
          <div className="font-bold">Time:</div>
          <div>{gpsData.time}</div>
        </div>
        <div>
          <div className="font-bold">Latitude:</div>
          <div>{gpsData.latitude}</div>
        </div>
        <div>
          <div className="font-bold">Longitude:</div>
          <div>{gpsData.longitude}</div>
        </div>
      </div>
    </div>
  </div>
);
};


export default GpsDataComponent;


