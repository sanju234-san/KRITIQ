import axios from 'axios'

// Dev domain - Axios client setup with JWT authorization interceptor
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    if (status === 401) {
      const wasLoggedIn = !!localStorage.getItem('token')
      localStorage.removeItem('token')
      if (wasLoggedIn) {
        window.dispatchEvent(new CustomEvent('kritiq:session-expired', {
          detail: {
            message: 'Your session has expired. Please log in again to continue.',
            timestamp: Date.now()
          }
        }))
        if (!window.location.pathname.startsWith('/login')) {
          const currentPath = window.location.pathname + window.location.search
          const redirectTo = currentPath && currentPath !== '/' ? `?redirect=${encodeURIComponent(currentPath)}` : ''
          window.location.href = `/login${redirectTo}&expired=1`
        }
      }
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
