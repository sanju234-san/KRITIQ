import axiosInstance from './axiosInstance.js'

// Dev domain - Review API stubs
export const reviewApi = {
  submitReview: async (payload) => {
    const response = await axiosInstance.post('/reviews', payload)
    return response.data
  },
  getReviewResult: async (id) => {
    const response = await axiosInstance.get(`/reviews/${id}`)
    return response.data
  }
}
