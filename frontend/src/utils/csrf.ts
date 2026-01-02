// Get CSRF token from cookie
export const getCsrfToken = (): string | null => {
  const name = 'csrftoken'
  const cookies = document.cookie.split(';')
  
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=')
    if (key === name && value) {
      return decodeURIComponent(value)
    }
  }
  return null
}

// Fetch wrapper that includes CSRF token
export const fetchWithCsrf = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const csrfToken = getCsrfToken()
  
  const headers: HeadersInit = {
    ...options.headers,
  }
  
  // Add CSRF token for non-GET requests
  if (csrfToken && options.method && options.method !== 'GET') {
    headers['X-CSRFToken'] = csrfToken
  }
  
  // Ensure credentials are included
  const fetchOptions: RequestInit = {
    ...options,
    headers,
    credentials: 'include',
  }
  
  return fetch(url, fetchOptions)
}

// Initialize CSRF token by calling the endpoint
export const initializeCsrf = async (): Promise<void> => {
  try {
    await fetch('/api/auth/csrf/', {
      credentials: 'include',
    })
  } catch (error) {
    console.error('Failed to initialize CSRF token:', error)
  }
}
