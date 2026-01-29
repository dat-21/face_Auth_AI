import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const registerUser = async (userId: string, imageBase64: string) => {
    try {
        const response = await axios.post(`${API_URL}/register`, {
            user_id: userId,
            image: imageBase64
        });
        return response.data;
    } catch (error: any) {
        throw error.response ? error.response.data : error;
    }
};

export const verifyUser = async (imageBase64: string) => {
    try {
        const response = await axios.post(`${API_URL}/verify`, {
            image: imageBase64
        });
        return response.data;
    } catch (error: any) {
        throw error.response ? error.response.data : error;
    }
};
