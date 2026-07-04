import axiosInstance from './axiosInstance.js'

// Dev domain - Auth API connection stubs
export const authApi = {
  login: async (email, password) => {
    const response = await axiosInstance.post('/auth/login', { email, password })
    return response.data
  },
  register: async (name, email, password) => {
    const response = await axiosInstance.post('/auth/register', { name, email, password })
    return response.data
  },
  getProfile: async () => {
    const response = await axiosInstance.get('/auth/profile')
    return response.data
  }
}
