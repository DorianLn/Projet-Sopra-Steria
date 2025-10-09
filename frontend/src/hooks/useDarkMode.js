import { useState, useEffect } from 'react'
import { STORAGE_KEYS, THEMES } from '../utils/constants'

/**
 * Hook personnalisé pour gérer le mode sombre/clair
 * @returns {Object} { darkMode, toggleDarkMode }
 */
export const useDarkMode = () => {
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem(STORAGE_KEYS.DARK_MODE) === 'true'
  )

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add(THEMES.DARK)
    } else {
      document.documentElement.classList.remove(THEMES.DARK)
    }
    localStorage.setItem(STORAGE_KEYS.DARK_MODE, darkMode)
  }, [darkMode])

  const toggleDarkMode = () => setDarkMode(!darkMode)

  return { darkMode, toggleDarkMode }
}