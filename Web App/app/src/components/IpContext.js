import React ,{ createContext, useContext, useState}  from "react";

const IPContext = createContext();


export const useIp = () => {
    return useContext(IPContext);
};

export const IPProvider =  ({ children }) => {
    const [ipAddress, setIpAddress] = useState(window.location.host.split(':')[0]); // Default IP

    return (
        <IPContext.Provider value={{ ipAddress, setIpAddress }}>
            {children}
        </IPContext.Provider>
    );
};