import React, { useState, useEffect, useRef } from "react";
import { TiThMenuOutline } from 'react-icons/ti';
import {
  LineChart,
  XAxis,
  YAxis,
  Tooltip,
  Line,
  CartesianGrid,
  ResponsiveContainer,
  Legend
} from "recharts";
import { useNavigate } from "react-router-dom";

// Static Legend Component
// const StaticLegend = () => (
//   <div className="static-legend">
//     <p><span className="legend-color" style={{ backgroundColor: "#2900ff" }}></span>X-axis</p>
//     <p><span className="legend-color" style={{ backgroundColor: "#fffa00" }}></span>Y-axis</p>
//     <p><span className="legend-color" style={{ backgroundColor: "#1cf007" }}></span>Z-axis</p>
//   </div>
// );

function App() {
  const [data, setData] = useState([]);
  const bufferRef = useRef([]);
  const requestRef = useRef();
  const navigate = useNavigate(); 

  const [showX, setShowX] = useState(true);
  const [showY, setShowY] = useState(true);
  const [showZ, setShowZ] = useState(true);
  const [yRange, setYRange] = useState(2000);

  const MaxPoints = 200;

  // Process buffer and update data state
  const processBuffer = () => {
    if (bufferRef.current.length > 0) {
      setData((prevData) => {
        const newData = [
          ...(Array.isArray(prevData) ? prevData : []),
          ...bufferRef.current.splice(0, bufferRef.current.length)
        ];
  
        if (newData.length > MaxPoints) {
          return newData.slice(newData.length - MaxPoints);
        }

        return newData;
      });
    }
  
    requestRef.current = requestAnimationFrame(processBuffer);
  };

  // Ensure the cleanup of the animation frame on component unmount
  useEffect(() => {
    requestRef.current = requestAnimationFrame(processBuffer);
  
    return () => {
      cancelAnimationFrame(requestRef.current);
    };
  });
  

  useEffect(() => {
    // WebSocket connection
    const socket = new WebSocket("ws://localhost:8000/ws"); // Update the port to match the backend

    socket.onopen = () => {
      console.log("Connected to WebSocket server");
    };

    socket.onmessage = (event) => {
      console.log("Received raw data:", event.data);
      try {
        const parsedData = JSON.parse(event.data);

        // Check if data is an array
        if (Array.isArray(parsedData)) {
          // Process each item in the array
          parsedData.forEach(item => {
            if (item.SNO !== undefined && item.Xdata !== undefined && item.Ydata !== undefined && item.Zdata !== undefined) {
              const formattedData = {
                SNO: item.SNO,
                Xdata: parseFloat(item.Xdata),
                Ydata: parseFloat(item.Ydata),
                Zdata: parseFloat(item.Zdata),
              };

              // Log formatted data
              console.log("Formatted data:", formattedData);

              // Push formatted data to the buffer
              bufferRef.current.push(formattedData);
            } else {
              console.error("Item does not match expected format:", item);
            }
          });
        } else {
          console.error("Received data is not an array:", parsedData);
        }
      } catch (error) {
        console.error("Error parsing WebSocket data:", error);
      }
    };

    requestRef.current = requestAnimationFrame(processBuffer);

    return () => {
      socket.close();
      cancelAnimationFrame(requestRef.current);
    };
  });

  useEffect(() => {
    console.log("Current data:", data);
  }, [data]);

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleMenuToggle = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <>
      <nav className="float-right p-4 mr-10">
        <div className="flex flex-col items-start">
          <div className="flex items-center justify-between w-auto">
            <TiThMenuOutline className="text-black text-2xl cursor-pointer" onClick={handleMenuToggle} />
            <span className="text-black ml-2 text-lg">MENU</span>
          </div>
          {isMenuOpen && (
            <div className="flex flex-col mt-2 space-y-2">
              <button className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700" onClick={() => navigate("/login")}>Login</button>
              <button className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700" onClick={() => navigate("/admin")}>Admin</button>
              <button className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700" onClick={() => navigate("/register")}>Register</button>
            </div>
          )}
        </div>
      </nav>

      <div className="container">
        <ResponsiveContainer width="50%" height={400}>
          <LineChart data={data} dataKey="value" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <XAxis dataKey="SNO" />
            <YAxis type="number"domain={[-yRange, yRange]} allowDataOverflow />
            <Tooltip />
            <Legend />
            <CartesianGrid stroke="#ccc" strokeOpacity={0.1}  fill="#232B2B" />
            {showX && <Line type="monotone" dataKey="Xdata" strokeWidth={3.5} stroke="#f6511d" dot={true} />}
            {showY && <Line type="monotone" dataKey="Ydata" strokeWidth={3.5} stroke="#ffb400" />}
            {showZ && <Line type="monotone" dataKey="Zdata" strokeWidth={3.5} stroke="#00a6ed" />}
          </LineChart>
        </ResponsiveContainer>
      </div>
      {/* <StaticLegend /> */}

      <div className="Box">
        <label htmlFor="name">PERSONALIZED DATA</label>
        <div className="check-box">
          <input
            name="Xdata"
            type="checkbox"
            checked={showX}
            onChange={(e) => setShowX(e.target.checked)}
          />
          <label htmlFor="Xdata">Xdata</label><br />
          <input
            name="Ydata"
            type="checkbox"
            checked={showY}
            onChange={(e) => setShowY(e.target.checked)}
          />
          <label htmlFor="Ydata">Ydata</label><br />
          <input
            name="Zdata"
            type="checkbox"
            checked={showZ}
            onChange={(e) => setShowZ(e.target.checked)}
          />
          <label htmlFor="Zdata">Zdata</label><br />
        </div>
      </div>


      <div className="input-box">
        <label htmlFor="yRange">Y-Axis Range Value:</label>
        <input
          type="number"
          id="yRange"
          value={yRange}
          onChange={(e) => setYRange(Number(e.target.value))}
        />
      </div>
    </>
  );
}

export default App;
