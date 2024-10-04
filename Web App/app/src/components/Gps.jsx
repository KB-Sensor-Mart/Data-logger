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
<div className="flex mt-10 flex-col items-center gps-data-container ">
  <h2 className="text-xl font-semibold">GPS Data</h2>
  <div className="text-xl w-full flex flex-col sm:flex-row sm:space-x-5 space-y-4 sm:space-y-0 gps-data-row justify-center">
    <div className="gps-item text-center p-3 rounded-md shadow-sm">
      <strong>Date:</strong> {gpsData.date}
    </div>
    <div className="gps-item text-center p-3 rounded-md shadow-sm">
      <strong>Time:</strong> {gpsData.time}
    </div>
    <div className="gps-item text-center p-3 rounded-md shadow-sm">
      <strong>Latitude:</strong> {gpsData.latitude}
    </div>
    <div className="gps-item text-center p-3 rounded-md shadow-sm">
      <strong>Longitude:</strong> {gpsData.longitude}
    </div>
  </div>
</div>
  );
};

export default GpsDataComponent;


