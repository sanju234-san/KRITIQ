import axiosInstance from './axiosInstance.js'

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
  },
  logout: async () => {
    try {
      const response = await axiosInstance.post('/auth/logout', {})
      return response.data
    } catch (_err) {
      return { detail: 'Logged out.' }
    }
  }
}
