import React, { useState, useEffect } from 'react';
import { useIp } from './IpContext';  // Assuming you have IpContext for IP management

const UPSDataComponent = () => {
  const { ipAddress } = useIp();  // Extracting the IP from context
  const [upsData, setUpsData] = useState({
    voltage: 'N/A',
    current: 'N/A',
    power: 'N/A',
    percent: 'N/A',
  });

  useEffect(() => {
    // Establish WebSocket connection to the backend for UPS data
    const socket = new WebSocket(`ws://${ipAddress}:8000/ws_ups`);  // Adjust the WebSocket URL as needed

    // Handle incoming WebSocket messages (UPS data updates)
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setUpsData(data);
    };

    // Handle WebSocket errors
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Close WebSocket when component unmounts
    return () => {
      socket.close();
    };
  }, [ipAddress]);

  return (
    <div className="flex mt-10 flex-col items-center ups-data-container">
      <h2 className="text-xl font-semibold">Power Data</h2>
      <div className="text-xl w-full flex flex-col sm:flex-row sm:space-x-5 space-y-4 sm:space-y-0 ups-data-row justify-center">
        <div className="ups-item text-center p-3 rounded-md shadow-sm">
          <strong>Battery Voltage:</strong> {upsData.voltage} V
        </div>
        <div className="ups-item text-center p-3 rounded-md shadow-sm">
          <strong>Current:</strong> {upsData.current} 
        </div>
      </div>
    </div>
  );
};

export default UPSDataComponent;
