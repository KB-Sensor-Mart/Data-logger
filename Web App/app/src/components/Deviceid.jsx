import React, { useEffect, useState } from "react";
import { useIp }from './IpContext';

const DeviceID = () => {
  const {ipAddress} = useIp();
  const [deviceID, setDeviceID] = useState(null);
  const [error, setError] = useState(null);


  useEffect(() => {
    // Fetch device ID from the backend
    const fetchDeviceID = async () => {
      try {
        const response = await fetch(`http://${ipAddress}:8000/api/device_id`); // Adjust URL if needed
        if (!response.ok) {
          throw new Error("Failed to fetch device ID");
        }
        const data = await response.json();
        setDeviceID(data.device_id);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchDeviceID();
  },[ipAddress]);

  if (error) {
    return (
		<div className="flex items-center justify-center h-screen">
		 <div className="text-red-500 text-lg font-bold">
			Error: {error}
		 </div>
		</div>
	);
  }

  if (!deviceID) {
  return(
	<div className="flex items-center justify-center h-screen">
		<div className="text-gray-600 text-lg font-semibold">
		    Loading device id...
		 </div>
	</div>
    );
  }

return (
  <div className="flex flex-col items-center justify-center mx-auto p-4">
    <h2 className="text-xl font-bold text-black mb-4">Device Information</h2>
    <div className="bg-white shadow-sm rounded-lg w-full max-w-sm p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <p className="text-lg font-medium">
          <strong className="text-gray-900">MAC Address:</strong> {deviceID.mac_address}
        </p>
        <p className="text-lg font-medium">
          <strong className="text-gray-900">Serial Number:</strong> {deviceID.serial_number}
        </p>
      </div>
    </div>
  </div>
);
};

export default DeviceID;
