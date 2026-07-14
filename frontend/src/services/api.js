import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

function getStoredToken() {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('ppa_token')
}

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    if (typeof window !== 'undefined') localStorage.setItem('ppa_token', token)
  } else {
    delete api.defaults.headers.common['Authorization']
    if (typeof window !== 'undefined') localStorage.removeItem('ppa_token')
  }
}

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

setAuthToken(getStoredToken())

export async function updateCompanyProfile(profileData) {
    return await api.put('/company/profile', profileData);
}

export async function getStudentProfile(studentId) {
    return await api.get(`/student/${studentId}/profile`);
}

export function getStudentResumeUrl(studentId) {
    return `${api.defaults.baseURL}/student/${studentId}/resume`;
}

export default api
