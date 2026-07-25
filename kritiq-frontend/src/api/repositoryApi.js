import axiosInstance from './axiosInstance.js'

// Dev domain - Repository API helper
export const repositoryApi = {
  connectRepo: async (repo_url) => {
    const response = await axiosInstance.post('/repositories/connect', { repo_url })
    return response.data
  },
  getRepos: async () => {
    const response = await axiosInstance.get('/repositories/')
    return response.data
  },
  getRepoFiles: async (owner, name, path = '') => {
    const response = await axiosInstance.get(`/repositories/${owner}/${name}/files?path=${path}`)
    return response.data
  },
  getFileContent: async (owner, name, path) => {
    const response = await axiosInstance.get(`/repositories/${owner}/${name}/file-content?path=${path}`)
    return response.data
  }
}
