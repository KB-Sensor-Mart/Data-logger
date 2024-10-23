import React ,{ useState , useEffect } from "react";
import Popup from 'reactjs-popup';
import 'reactjs-popup/dist/index.css';
import axios from 'axios';
import Swal from 'sweetalert2';
import  Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import {useIp} from './IpContext'
import GpsDataComponents from '../components/Gps'
import LiveUPSData from '../components/ups'

function Home() {
    const [newIpAddress , setNewIpAddress] = useState('');
    const [currentIp , setCurrentIp] = useState('');
    const [routerIp, setRouterIp] = useState('');
    const [dnsservers, setdnsservers] = useState('');
    const [ipAssignment, setIpAssignment] = useState('dhcp');
    
    const [selectedDate, setSelectedDate] = useState('');
    const [startTime, setStartTime] = useState('');
    const [endTime, setEndTime] = useState('');

    const [host, setHost] = useState(' ');
    const [port, setPort] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [remotePath, setRemotePath] = useState('');
    const [ftpStatus, setFtpStatus] = useState('');
    const { ipAddress } = useIp();

  useEffect(() => {
    setCurrentIp(window.location.host.split(':')[0]);  
    

  }, []);

const updateFtpCredentials = async () => {
    try {
        const data = {
            host: host,
            port: Number(port),
            username: username,
            password: password,
            remotepath: remotePath,
        };

        await axios.post(`http://${ipAddress}:8000/ftp/upload_credentials`, data, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        Swal.fire({
            icon: 'success',
            title: 'Success',
            text: 'FTP credentials updated successfully.',
        });
    } catch (error) {
        console.error('Error updating FTP credentials:', error.response?.data || error.message || error);

        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.response?.data?.message || `Server error: ${error.response?.status || 'Unknown error'}`,
        });
    }
};

const startFtpUpload = async () => {
    try {
        // Replace this with your actual upload logic
        await axios.post(`http://${ipAddress}:8000/ftp/upload_folder`, {
            // Include necessary data for the upload here
        }, {
            headers: {
                'Content-Type': 'application/json',
            },
        });

        Swal.fire({
            icon: 'success',
            title: 'Success',
            text: 'FTP upload started successfully.',
        });
    } catch (error) {
        console.error('Error starting FTP upload:', error.response?.data || error.message || error);

        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.response?.data?.message || `Failed to start FTP upload: ${error.response?.status || 'Unknown error'}`,
        });
    }
};

  const checkFtpConnection = async () => {
   try {
        if (!ipAddress) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Please enter the IP Address before proceeding'
            });
            return; // Exit function if IP address is not provided
        }
      const response = await axios.get(`http://${ipAddress}:8000/ftp/check_connection`);
      setFtpStatus(response.data.message);
    } catch (error) {
      setFtpStatus('Failed to connect to the FTP server.');
    }
  };

  const handleStopUpload = async () => {
    try {
      const response = await axios.post(`http://${ipAddress}:8000/ftp/stop_upload`); // Adjust the URL if necessary
      if (response.status === 200) {
        Swal.fire({
          title: 'Success',
          text: 'FTP upload and folder monitoring stopped successfully!',
          icon: 'success',
          confirmButtonText: 'OK',
          customClass: {
            popup: 'responsive-popup'  // Custom class for responsive popup
          }
        });
      }
    } catch (error) {
      console.error('Error stopping upload:', error);
      Swal.fire({
        title: 'Error',
        text: 'Failed to stop the FTP upload and monitoring!',
        icon: 'error',
        confirmButtonText: 'OK',
        customClass: {
          popup: 'responsive-popup'
        }
      });
    }
  };

 const handleIpAddressChange = (e) => {
    const newIp = e.target.value.trim();
    if (validateIp(newIp)) {
      setNewIpAddress(newIp);
      localStorage.setItem('ipAddress', newIp); // Save new IP to localStorage

    }
  };

  // Utility function to validate the IP format
  const validateIp = (ip) => {
    const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
  };

   const handleSave = async () => {
    
    const payload = {
        dns_servers: ipAssignment === 'manual' ? dnsservers : '',
        ip_address: ipAssignment === 'manual' ? newIpAddress : '',
        routers: ipAssignment === 'manual' ? routerIp : '',
    };

    try {
        const url = `http://${ipAddress}:8000/ip`;  
        console.log('Sending request to URL:', url); 

        const response = await axios.post(url, payload, {
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.status === 200) {
            Swal.fire({
                icon: 'success',
                title: 'Success',
                text: 'IP settings saved successfully.',
            });
        }
    } catch (error) {
        console.error('Error saving IP settings:', error);

        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.response?.data?.message || 'Failed to save IP settings.',
        });
    }
};

const handleDownload = async () => {
    if (!selectedDate || !startTime || !endTime) {
        alert('Please select all required fields');
        return;
    }

    if (startTime >= endTime) {
        alert('End time must be after start time');
        return;
    }

    // Validate IP address format
    const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    if (!ipRegex.test(ipAddress)) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Invalid IP address format.',
        });
        return;
    }

    const downloadUrl = `http://${ipAddress}:8000/download_data`
    console.log("Constructed download URL:", downloadUrl);

    try {
        const response = await axios.get(downloadUrl, {
            params: {
                date: selectedDate,
                start_time: startTime,
                end_time: endTime
            },
            responseType: 'blob'
        });

        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/zip' }));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `files_${selectedDate}_${startTime}_${endTime}.zip`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch (error) {
        console.error('Error downloading the file:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Failed to download files: ' + (error.response ? error.response.data.detail : error.message),
        });
    }
};

 
   return (
    <>
       <div className=" mb-20 overflow-hidden flex flex-col">
  <div>
    <Navbar />
  </div>
  
  <div className="flex-1 flex items-center justify-center overflow-y-auto">
    <div className="grid grid-cols-1 m-4 sm:grid-cols-2 lg:grid-cols-3 gap-6 justify-center w-full max-w-full">
      
      {/* IP Config Popup */}
      <Popup
        trigger={
          <div className="flex flex-col w-full sm:w-[80%] lg:h-[80%] lg:w-[60%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
            <div className="grow px-5 pt-9 cursor-pointer pb-20 sm:pb-28 w-full text-base font-bold whitespace-nowrap text-stone-950">
              IP Config
            </div>
            <div className="flex items-center  px-5 pb-5">
              <a className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400">Learn more</a>
              <svg width="34px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="ml-2">
                <path d="M4 12H20M20 12L16 8M20 12L16 16" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </div>
          </div>
        }
        modal
        nested
      >
        {close => (
          <div className="p-5 rounded-lg shadow-lg max-w-lg w-full">
            <h2 className="text-xl font-bold mb-4">Configure IP Address</h2>
            <select value={ipAssignment} onChange={(e) => setIpAssignment(e.target.value)} className="w-full p-2 border border-gray-300 rounded mb-4">
              <option value="dhcp">Automatic (DHCP)</option>
              <option value="manual">Manual</option>
            </select>

            {ipAssignment === 'manual' && (
              <>
                <input type="text" value={newIpAddress} onChange={(e) => setNewIpAddress(e.target.value)} placeholder="Enter New IP Address" className="w-full p-2 border border-gray-300 rounded mb-4" />
                <input type="text" value={routerIp} onChange={(e) => setRouterIp(e.target.value)} placeholder="Enter Router IP" className="w-full p-2 border border-gray-300 rounded mb-4" />
                <input type="text" value={dnsservers} onChange={(e) => setdnsservers(e.target.value)} placeholder="Enter DNS" className="w-full p-2 border border-gray-300 rounded mb-4" />
              </>
            )}

            <div className="flex justify-end space-x-4">
              <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" onClick={handleSave}>Save</button>
              <button className="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400" onClick={close}>Close</button>
            </div>
          </div>
        )}
      </Popup>
    
         <div className="flex flex-col w-full sm:w-[80%] lg:h-[80%]  lg:w-[60%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
        <a href="Live graph">
        <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                          Live Graph
        <img className="w-[50%]" src="./images/graph.png" alt="" />
                                </div>
          <div className="flex items-center px-5 pb-5">
            <a className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400" href="/Live graph"></a>
           
          </div>
        </a>
      </div>
                   
                  <div>
                    <Popup
                        trigger={
                            <div className="flex flex-col w-full sm:w-[80%] lg:h-[80%] lg:w-[60%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                                <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                                    Download Files
                                    <img className="w-[20%]" src="./images/download.png" alt="" />
                                </div>
                                <div className="flex items-center -mt-12 px-5 pb-5 ">
                                    <a
                                        className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400"
                                        style={{ cursor: 'pointer'}} >
                                        Download Now
                                    </a>
                                    <svg width="34px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="ml-2">
                                        <path d="M4 12H20M20 12L16 8M20 12L16 16" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                                    </svg>
                                </div>
                            </div>
                        }
                        modal
                        nested
                    >
                        {close => (
                            <div className="p-3 rounded-lg shadow-lg max-w-sm w-auto">
                                <h2 className="text-xl font-bold mb-4">Download Files</h2>

                                <input
                                    
                                    value={selectedDate}
                                    onChange={(e) => setSelectedDate(e.target.value)}
                                    placeholder="YYYY-MM-DD"
                                    className="w-full p-2 border border-gray-300 rounded mb-4"
                                />
                                <input
                                    type="time"
                                    value={startTime}
                                    onChange={(e) => setStartTime(e.target.value)}
                                    placeholder="Select Start Time"
                                    className="w-full p-2 border border-gray-300 rounded mb-4"
                                />
                                <input
                                    type="time"
                                    value={endTime}
                                    onChange={(e) => setEndTime(e.target.value)}
                                    placeholder="Select End Time"
                                    className="w-full p-2 border border-gray-300 rounded mb-4"
                                />

                                <div className="flex justify-end space-x-4">
                                    <button
                                        onClick={async () => {
                                            await handleDownload();
                                            close();
                                        }}
                                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                    >
                                        Download
                                    </button>
                                    <button
                                        onClick={close}
                                        className="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400"
                                    >
                                        Close
                                    </button>
                                </div>
                            </div>
                        )}
                    </Popup>
                     </div>
                     
                  <Popup
      trigger={
        <div className="flex flex-col w-full sm:w-[80%] lg:h-[80%] lg:w-[60%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
          <div className="grow px-5 pt-9 cursor-pointer pb-20 sm:pb-28 w-full text-base font-bold whitespace-nowrap text-stone-950">
            FTP Server
          </div>
          <div className="flex items-center -mt-12 px-5 pb-5">
            <a className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400">
              Learn more
            </a>
            <svg width="34px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="ml-2">
              <path d="M4 12H20M20 12L16 8M20 12L16 16" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
            </svg>
          </div>
        </div>
      }
      modal
      nested
    >
      {close => (
        <div className="p-5 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-xl font-bold mb-4">Configure FTP Credentials</h2>
          <form onSubmit={(e) => {
            e.preventDefault();
            updateFtpCredentials();
          }}>
            <input
              type="text"
              value={host}
              required
              onChange={(e) => setHost(e.target.value)}
              placeholder="Host"
              className="w-full p-2 border border-gray-300 rounded mb-4"
            />
            <input
              type="number"
              value={port}
              required
              onChange={(e) => setPort(e.target.value)}
              placeholder="FTP Port"
              className="w-full p-2 border border-gray-300 rounded mb-4"
            />
            <input
              type="text"
              value={username}
              required
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              className="w-full p-2 border border-gray-300 rounded mb-4"
            />
            <input
              
              value={password}
              required
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full p-2 border border-gray-300 rounded mb-4"
            />
            <input
              type="text"
              value={remotePath}
              required
              onChange={(e) => setRemotePath(e.target.value)}
              placeholder="Remote Path"
              className="w-full p-2 border border-gray-300 rounded mb-4"
            />
            <div className="flex justify-end space-x-4">
              <button
                type="submit"
                className="mt-4 p-2 bg-blue-500 text-white rounded"
              >
                Update FTP Credentials
              </button>
              <button
                type="button"

                onClick={startFtpUpload}
                className="mt-4 p-2 bg-green-500 text-white rounded"
              >
                Start FTP Upload
              </button>
              <button
                type="button"
                onClick={checkFtpConnection}
                className="mt-4 p-2 bg-yellow-500 text-white rounded"
              >
                Check FTP Connection
              </button>
              <button
                type="button"
                onClick={handleStopUpload}
                className="mt-4 p-2 bg-red-500 text-white rounded"
              >
                Stop FTP Upload
              </button>
            </div>
            {ftpStatus && (
              <div className="mt-4 p-2 border border-gray-300 rounded">
                <h2 className="text-lg font-semibold">FTP Connection Status:</h2>
                <p>{ftpStatus}</p>
              </div>
            )}
          </form>
        </div>
      )}
    </Popup>
    
                 <div className="flex flex-col w-full sm:w-[80%] lg:h-[80%] lg:w-[60%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                        <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                            Log files
                            <img className="w-[20%]" src="./images/png.png"
                            alt="" />
                    </div>
                    <div className="flex items-center px-5 pb-5">
                        <a className="text-transparent" href="/pages/webdevservices">
                            Learn more
                        </a>
                      
                    </div>
                </div>
                    
                <div className="flex flex-col w-full sm:w-[80%] lg:h-[80%] lg:w-[60%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                        <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                            Admin
                            <img className="w-[20%]" src="./images/admin.png"
                            alt="" />
                    </div>
                    <div className="flex items-center -mt-12 px-5 pb-5">
                        <a className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400" href="/pages/webdevservices">
                            Learn more
                        </a>
                        <svg width="34px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="ml-2">
                            <path d="M4 12H20M20 12L16 8M20 12L16 16" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                        </svg>
                    </div>
                </div>
                
            </div>
        </div>
    </div>
    
    <div className="flex justify-center gap-20">
    
    <LiveUPSData />
    <GpsDataComponents / >
    
    </div>
    
  <div>
     <Footer/>
  </div>

   </>
    
    );
}

export default Home;
