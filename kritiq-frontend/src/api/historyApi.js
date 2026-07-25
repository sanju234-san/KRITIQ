import axiosInstance from './axiosInstance.js'

// Dev domain - History API helper
export const historyApi = {
  getHistory: async () => {
    const response = await axiosInstance.get('/history/')
    return response.data
  }
}
