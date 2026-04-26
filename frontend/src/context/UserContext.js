import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

export const useUserContext = () => {
    return useContext(UserContext);
};

export const UserProvider = ({ children }) => {
    const [userProfile, setUserProfile] = useState(() => {
        const saved = localStorage.getItem('user_profile');
        return saved ? JSON.parse(saved) : {
            name: "John Doe",
            vehicleType: "Truck", // "Car" or "Truck"
            vehicleId: "TRUCK-01",
            role: "Owner",
            company: "Logistics Pro",
            avatar: null
        };
    });

    useEffect(() => {
        localStorage.setItem('user_profile', JSON.stringify(userProfile));
    }, [userProfile]);

    const updateProfile = (newData) => {
        setUserProfile(prev => ({ ...prev, ...newData }));
    };

    return (
        <UserContext.Provider value={{ userProfile, updateProfile }}>
            {children}
        </UserContext.Provider>
    );
};
