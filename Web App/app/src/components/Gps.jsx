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
 <div className="flex gps-data-container">
      <h2></h2>
      <div className="text-xl space-x-5 m-5 mx-auto flex  gps-data-row">
        <div className="gps-item">
          <strong>Date:</strong> {gpsData.date}
        </div>
        <div className="gps-item">
          <strong>Time:</strong> {gpsData.time}
        </div>
        <div className="gps-item">
          <strong>Latitude:</strong> {gpsData.latitude}
        </div>
        <div className="gps-item">
          <strong>Longitude:</strong> {gpsData.longitude}
        </div>
      </div>
    </div>
  );
};

export default GpsDataComponent;
