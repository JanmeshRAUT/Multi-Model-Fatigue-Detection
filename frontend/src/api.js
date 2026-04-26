
import axios from 'axios';

const rawApiUrl = process.env.REACT_APP_API_URL || "http://localhost:5000";
export const API_BASE = rawApiUrl.endsWith('/') ? rawApiUrl.slice(0, -1) : rawApiUrl;

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
 * Prediction via Hugging Face Space (FastAPI) or Inference API
 * @param {Object} features - The features (EAR, MAR, etc.)
 * @param {string} mode - "standard" or "vehicle"
 */
export const getFatiguePrediction = async (features, mode = "standard") => {
    // 1. Try the Space API first (if it's our primary backend)
    try {
        const response = await api.post('/predict', {
            mode: mode,
            ...features
        });
        return response.data;
    } catch (error) {
        console.warn("Space API Prediction failed, trying Inference API...", error);
    }

    // 2. Fallback to Inference API if token is available
    if (!HF_TOKEN) {
        console.error("HF_TOKEN is missing, cannot use Inference API fallback.");
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
        console.error("All Prediction Methods Failed:", error);
        return null;
    }
};

export default api;
