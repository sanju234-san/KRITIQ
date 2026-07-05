import axiosInstance from './axiosInstance.js'

// Dev domain - History API stubs
export const historyApi = {
  getHistory: async () => {
    const response = await axiosInstance.get('/history')
    return response.data
  }
}
