export const theme = {
  // Primary colors
  primary: '#ff7f00',
  primaryDark: '#a05305ff',
  primaryLight: '#ee9236ff',
  
  // Secondary colors
  secondary: '#3B82F6',
  secondaryDark: '#2563EB',
  secondaryLight: '#60A5FA',
  
  // Accent colors
  accent: '#8B5CF6',
  danger: '#EF4444',
  warning: '#F59E0B',
  success: '#10B981',
}

export type Theme = typeof theme

// Apply theme to CSS custom properties
export function applyTheme(customTheme: Partial<Theme> = {}) {
  const finalTheme = { ...theme, ...customTheme }
  const root = document.documentElement
  
  Object.entries(finalTheme).forEach(([key, value]) => {
    // Convert camelCase to kebab-case
    const cssVar = key.replace(/([A-Z])/g, '-$1').toLowerCase()
    root.style.setProperty(`--theme-${cssVar}`, value)
  })
}
