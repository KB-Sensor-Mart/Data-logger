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

  useEffect(() => {
    // Establish WebSocket connection to the backend
    const socket = new WebSocket(`ws://${ipAddress}:8000/ws/gps`); // Adjust the WebSocket URL as needed

    // Handle incoming WebSocket messages (GPS data updates)
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGpsData(data);
    };

    // Handle WebSocket errors
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Close WebSocket when component unmounts
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="flex flex-col items-center mx-auto p-4 max-w-lg">
      <h2 className="text-3xl font-semibold mb-6">GPS Data</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
        <div className="gps-item bg-gray-100 p-4 rounded-lg shadow-md text-center">
          <strong className="block font-medium text-lg">Date:</strong> 
          <span className="text-gray-700">{gpsData.date}</span>
        </div>
        <div className="gps-item bg-gray-100 p-4 rounded-lg shadow-md text-center">
          <strong className="block font-medium text-lg">Time:</strong> 
          <span className="text-gray-700">{gpsData.time}</span>
        </div>
        <div className="gps-item bg-gray-100 p-4 rounded-lg shadow-md text-center">
          <strong className="block font-medium text-lg">Latitude:</strong> 
          <span className="text-gray-700">{gpsData.latitude}</span>
        </div>
        <div className="gps-item bg-gray-100 p-4 rounded-lg shadow-md text-center">
          <strong className="block font-medium text-lg">Longitude:</strong> 
          <span className="text-gray-700">{gpsData.longitude}</span>
        </div>
      </div>
    </div>
  );
};

export default GpsDataComponent;


