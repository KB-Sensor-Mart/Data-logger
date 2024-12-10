import React, { useEffect, useState } from "react";
import { useIp } from './IpContext';

const StorageStatus = () => {
  const { ipAddress } = useIp();
  const [storageStatus, setStorageStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Update WebSocket URL to match the new backend endpoint
    const wsUrl = `ws://${ipAddress}:8000/ws/storage`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log("WebSocket connection established");
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setStorageStatus(data); // Update state with new storage data
      } catch (err) {
        setError("Error parsing storage data");
        console.error("Error parsing data: ", err);
      }
    };

    socket.onerror = (err) => {
      setError("WebSocket connection failed");
      console.error("WebSocket error: ", err);
    };

    socket.onclose = (event) => {
      setError("WebSocket connection closed");
      console.log("WebSocket closed with code: ", event.code);
    };

    // Cleanup the WebSocket connection on component unmount
    return () => {
      console.log("Cleaning up WebSocket connection");
      socket.close();
    };
  }, [ipAddress]);

  if (!storageStatus) {
    return (
      <div className="flex items-center justify-center">
        <div className="text-gray-600 text-lg font-semibold">
          Loading storage information...
        </div>
      </div>
    );
  }

return (
  <div className="flex flex-col items-center justify-center mx-auto p-4">
    <h2 className="text-xl font-bold text-black mb-4">Storage Status</h2>
    <div className="bg-white shadow-sm rounded-lg w-full max-w-sm p-4">
      <div className="grid gap-4">
        <p className="text-lg font-medium">
          <strong className="text-gray-900">Total Storage:</strong> {storageStatus.total_storage}
        </p>
        <p className="text-lg font-medium">
          <strong className="text-gray-900">Used Storage:</strong> {storageStatus.used_storage}
        </p>
        <p className="text-lg font-medium">
          <strong className="text-gray-900">Free Storage:</strong> {storageStatus.free_storage}
        </p>
      </div>
    </div>
  </div>
);
};

export default StorageStatus;
