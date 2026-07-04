import axiosInstance from './axiosInstance.js'

// Dev domain - Translation API stubs
export const translationApi = {
  submitTranslation: async (payload) => {
    const response = await axiosInstance.post('/translations', payload)
    return response.data
  },
  getTranslationResult: async (id) => {
    const response = await axiosInstance.get(`/translations/${id}`)
    return response.data
  }
}
