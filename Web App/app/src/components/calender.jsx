import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { useIp }from './IpContext';

const Calendar = () => {
    
    const {ipAddress} = useIp();
    const [fileStatus, setFileStatus] = useState({});
    const [selectedDate, setSelectedDate] = useState(null);
    const [socket, setSocket] = useState(null);

    useEffect(() => {

        // Establish WebSocket connection
        const initializeWebSocket = () => {
            const ws = new WebSocket(`ws://${ipAddress}:8000/ws/date_status`);
            
            setSocket(ws);

            // Handle incoming WebSocket messages
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('WebSocket message received:', data);
                setFileStatus(data);  
            };

            // Handle WebSocket connection errors
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            // Attempt to reconnect on close
            ws.onclose = () => {
                console.log("WebSocket closed, reconnecting...");
                setTimeout(initializeWebSocket, 5000); // Retry every 5 seconds
            };
        };

        initializeWebSocket();

        // Clean up WebSocket when component unmounts
        return () => {
            if (socket) {
                socket.close();
            }
        };
    }, []);

    // Function to set the date color based on status
    
const getDateColor = (date) => {

    const formattedDate = date.toISOString().split('T')[0];
    const status = fileStatus[formattedDate];
        
    if (status === undefined) {
        return "gray";  // Return default color if no status exists for the date
    }

    // Use status to set color
    switch (status) {
        case "no_files":
            return "red";
        case "files_exist":
            return "green";
        case "files_increasing":
            return "orange";
        default:
            return "gray";
    }
};

    return (
        <div className="p-3 rounded-lg shadow-lg max-w-sm w-auto">
            <h2 className="text-xl font-bold mb-4">Select Date</h2>
            <DatePicker
                selected={selectedDate}
                onChange={(date) => setSelectedDate(date)}
                inline
                dayClassName={(date) => `day-${getDateColor(date)}`}
            />

            <style jsx="true">{`
                .day-red { color: red; }
                .day-green { color: green; }
                .day-orange { color: orange; }
                .day-gray { color: gray; }
            `}</style>
        </div>
    );
};

export default Calendar;
