import React from 'react';

const Footer = () => {
  return (
  <footer className=" w-full bg-black text-white flex justify-between items-center">
  {/* Left section */}
  <div className="flex flex-col items-start">
    <span className="text-lg md:text-xl font-sans">An IIT Roorkee Startup</span>
    <span className="text-sm md:text-base">Seismic Hazard and Risk Investigation Pvt Ltd</span>
    <span className="text-sm md:text-base">BHU SENSE MODEL -SB2401</span>
  </div>
  
  {/* Right section: Image */}
  <img className="w-1/2 md:w-[10%] h-auto" src="./images/startup.png" alt="Startup Image" />
</footer>

  );
}

export default Footer;
