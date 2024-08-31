import React, { useState } from "react";
import Popup from 'reactjs-popup';
import 'reactjs-popup/dist/index.css';
import axios from 'axios';
import qs from 'qs';

function Home() {
    const [ipAddress, setIpAddress] = useState('');
    const [routerIp, setRouterIp] = useState('');
    const [dns_servers, setdns_servers] = useState('');
    const [ipAssignment, setIpAssignment] = useState('dhcp');

    const [selectedDate, setSelectedDate] = useState('');
    const [startTime, setStartTime] = useState('');
    const [endTime, setEndTime] = useState('');

    const handleSave = async () => {
        const payload = {
            ip_address: ipAssignment === 'manual' ? ipAddress : '',
            routers: ipAssignment === 'manual' ? routerIp : '',
            dns_server: ipAssignment === 'manual' ? dns_servers : ''
        };
        
        try {
            const response = await axios.post('http://localhost:8000/change-ip/', qs.stringify(payload), {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            alert(response.data.message);
        } catch (error) {
            console.error('Error response:', error.response);
            alert('Failed to change IP: ' + (error.response ? error.response.data.detail : error.message));
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

        try {
            const response = await axios.get('http://localhost:8000/downloaddata', {
                params: {
                    formatted_date: selectedDate,
                    start_t: startTime,
                    end_t: endTime
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
            alert('Failed to download files: ' + (error.response ? error.response.data.detail : error.message));
        }
    };

    return (
        <div className="px-4 pt-10 max-xl:pb-6">
            <div className="mx-auto w-full max-sm:max-w-full">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 justify-center">
                    
                    {/* IP Config Popup */}
                    <Popup
                        trigger={
                            <div className="flex flex-col w-full sm:w-[80%] lg:w-[80%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                                <div className="grow px-5 pt-9 cursor-pointer pb-20 sm:pb-28 w-full text-base font-bold whitespace-nowrap text-stone-950">
                                    IP Config
                                </div>
                                <div className="flex items-center px-5 pb-5">
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
                                <h2 className="text-xl font-bold mb-4">Configure IP Address</h2>

                                <select
                                    value={ipAssignment}
                                    onChange={(e) => setIpAssignment(e.target.value)}
                                    className="w-full p-2 border border-gray-300 rounded mb-4"
                                >
                                    <option value="dhcp">Automatic (DHCP)</option>
                                    <option value="manual">Manual</option>
                                </select>

                                {ipAssignment === 'manual' && (
                                    <>
                                        <input
                                            type="text"
                                            value={ipAddress}
                                            onChange={(e) => setIpAddress(e.target.value)}
                                            placeholder="Enter New IP Address"
                                            className="w-full p-2 border border-gray-300 rounded mb-4"
                                        />
                                        <input
                                            type="text"
                                            value={routerIp}
                                            onChange={(e) => setRouterIp(e.target.value)}
                                            placeholder="Enter Router IP"
                                            className="w-full p-2 border border-gray-300 rounded mb-4"
                                        />
                                        <input
                                            type="text"
                                            value={dns_servers}
                                            onChange={(e) => setdns_servers(e.target.value)}
                                            placeholder="Enter Subnet Mask"
                                            className="w-full p-2 border border-gray-300 rounded mb-4"
                                        />
                                    </>
                                )}

                                <div className="flex justify-end space-x-4">
                                    <button
                                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                        onClick={async () => {
                                            await handleSave();
                                            close();
                                        }}
                                    >
                                        Save
                                    </button>
                                    <button
                                        className="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400"
                                        onClick={close}
                                    >
                                        Close
                                    </button>
                                </div>
                            </div>
                        )}
                    </Popup>
    
                    <div className="flex flex-col w-full sm:w-[80%] lg:w-[80%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                        <a href="Live graph">
                            <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full text-base font-bold whitespace-nowrap text-stone-950">
                                Live Graph
                                <img className="w-[30%]" src="./images/graph.png" alt="" />
                            </div>
                            <div className="flex items-center px-5 pb-5">
                                <a className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400" href="/Live graph">
                                    Learn more
                                </a>
                                <svg width="34px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="ml-2">
                                    <path d="M4 12H20M20 12L16 8M20 12L16 16" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                                </svg>
                            </div>
                        </a>
                    </div>
    
                    <Popup
                        trigger={
                            <div className="flex flex-col w-full sm:w-[80%] lg:w-[80%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                                <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                                    Download Files
                                    <img className="w-[20%]" src="./images/download.png" alt="" />
                                </div>
                                <div className="flex items-center px-5 pb-5">
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

    
                    <div className="flex flex-col w-full sm:w-[80%] lg:w-[80%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                        <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                            About Us
                            <img className="w-[20%]" src="./images/about.png" alt="" />
                        </div>
                        <div className="flex items-center px-5 pb-5">
                            <a className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400" href="/pages/webdevservices">
                                Learn more
                            </a>
                            <svg width="34px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="ml-2">
                                <path d="M4 12H20M20 12L16 8M20 12L16 16" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                            </svg>
                        </div>
                    </div>
                    
                    <div className="flex flex-col w-full sm:w-[80%] lg:w-[80%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                        <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                            Log files
                            <img className="w-[20%]" src="./images/png.png"
                            alt="" />
                    </div>
                    <div className="flex items-center px-5 pb-5">
                        <a className="text-transparent bg-clip-text bg-gradient-to-r from-[#5E58E7] to-pink-400" href="/pages/webdevservices">
                            Learn more
                        </a>
                        <svg width="34px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="ml-2">
                            <path d="M4 12H20M20 12L16 8M20 12L16 16" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                        </svg>
                    </div>
                </div>
                    
                <div className="flex flex-col w-full sm:w-[80%] lg:w-[80%] mx-auto transform rounded-md border-2 transition-transform duration-300 hover:scale-105 text-base border border-black border-solid">
                        <div className="grow px-5 pt-9 pb-20 sm:pb-28 w-full cursor-pointer text-base font-bold text-stone-950">
                            Admin
                            <img className="w-[20%]" src="./images/admin.png"
                            alt="" />
                    </div>
                    <div className="flex items-center px-5 pb-5">
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
    
    
    
    );
}

export default Home;
