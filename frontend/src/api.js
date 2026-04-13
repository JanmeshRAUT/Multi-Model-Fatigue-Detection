
import axios from 'axios';

export const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
});

// --- HUGGING FACE INFERENCE API CONFIG ---
const HF_MODEL_URL = "https://api-inference.huggingface.co/models/JerryJR1705/fatiguemodel";
const HF_TOKEN = process.env.REACT_APP_HF_TOKEN; 

// --- API Service Methods ---

export const resetCalibration = async () => {
    try {
        const response = await api.post('/api/reset_calibration');
        return response.data.status === "success";
    } catch (error) {
        console.error("Error resetting calibration:", error);
        return false;
    }
};

export const getCombinedData = async () => {
    try {
        const response = await api.get('/api/combined_data');
        return response.data;
    } catch (error) {
        console.error("Error fetching combined data:", error);
        return null;
    }
};

// --- VEHICLE MODEL API ENDPOINTS ---

export const getVehicleCombinedData = async () => {
    try {
        const response = await api.get('/api/vehicle/combined_data');
        return response.data;
    } catch (error) {
        console.error("Error fetching vehicle data:", error);
        return null;
    }
};

export const resetVehicleCalibration = async () => {
    try {
        const response = await api.post('/api/vehicle/reset_calibration');
        return response.data.status === "OK";
    } catch (error) {
        console.error("Error resetting vehicle calibration:", error);
        return false;
    }
};

/**
 * Direct Prediction via Hugging Face Inference API
 * @param {Object} features - The 10 features (EAR, MAR, etc.)
 * @param {string} mode - "standard" or "vehicle"
 */
export const getFatiguePrediction = async (features, mode = "standard") => {
    if (!HF_TOKEN) {
        console.error("HF_TOKEN is missing in environment variables!");
        return null;
    }

    try {
        const response = await axios.post(
            HF_MODEL_URL,
            { 
                inputs: features,
                mode: mode 
            },
            {
                headers: { 
                    "Authorization": `Bearer ${HF_TOKEN}`,
                    "Content-Type": "application/json"
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error("Hugging Face Prediction Error:", error);
        return null;
    }
};

export default api;
