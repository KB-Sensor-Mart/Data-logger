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
    const socket = new WebSocket(`ws://${ipAddress}:8000/ws/ws_ups`);  // Adjust the WebSocket URL as needed

    // Handle incoming WebSocket messages (UPS data updates)
    socket.onmessage = (event) => {
	try{
      const data = JSON.parse(event.data);
      //console.log('Received data:', data);
      setUpsData(data);
	} catch (error) {
	   console.error('Error parsing WebSocket data:' , error);
	}
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
  <div className="flex flex-col items-center justify-center ups-data-container p-4">
    <h2 className="text-xl font-semibold mb-4">Power Data</h2>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-center w-full max-w-lg bg-white rounded-md shadow-sm p-4">
      {/* Labels */}
      <div className="font-bold">Battery Voltage:</div>
      <div className="font-bold">Current:</div>
      {/* Values */}
      <div>{upsData.voltage !== "N/A" ? `${upsData.voltage} V` : "N/A V"}</div>
      <div>{upsData.current !== null && upsData.current !== undefined ? `${upsData.current} A` : "N/A A"}</div>
    </div>
  </div>
);
};

export default UPSDataComponent;
