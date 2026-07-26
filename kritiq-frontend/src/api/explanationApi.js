import axiosInstance from './axiosInstance.js'

// Dev domain - Explanation API helper
export const explanationApi = {
  submitExplanation: async (payload) => {
    const response = await axiosInstance.post('/explanations/', payload)
    return response.data
  },
  getExplanationResult: async (id) => {
    const response = await axiosInstance.get(`/explanations/${id}`)
    return response.data
  }
}
