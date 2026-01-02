import { ref, computed } from 'vue'
import { fetchWithCsrf } from '../utils/csrf'

interface User {
  id: number
  username: string
  email: string
}

const user = ref<User | null>(null)
const isAuthenticated = computed(() => user.value !== null)
const isLoading = ref(false)

export const useAuth = () => {
  const login = async (username: string, password: string): Promise<boolean> => {
    isLoading.value = true
    try {
      const response = await fetchWithCsrf('/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      if (response.ok) {
        const data = await response.json()
        user.value = data.user
        return true
      } else {
        const error = await response.json()
        console.error('Login failed:', error)
        return false
      }
    } catch (error) {
      console.error('Login error:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (username: string, password: string, email: string = ''): Promise<boolean> => {
    isLoading.value = true
    try {
      const response = await fetchWithCsrf('/api/auth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password, email }),
      })

      if (response.ok) {
        const data = await response.json()
        user.value = data.user
        return true
      } else {
        const error = await response.json()
        console.error('Registration failed:', error)
        return false
      }
    } catch (error) {
      console.error('Registration error:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await fetchWithCsrf('/api/auth/logout/', {
        method: 'POST',
      })
      user.value = null
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const checkAuth = async (): Promise<void> => {
    try {
      const response = await fetch('/api/auth/check/', {
        credentials: 'include',
      })
      if (response.ok) {
        const data = await response.json()
        if (data.authenticated) {
          user.value = data.user
        }
      }
    } catch (error) {
      console.error('Auth check error:', error)
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
  }
}
