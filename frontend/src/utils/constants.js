// ===================== NAVIGATION CONSTANTS =====================
export const ROUTES = {
  HOME: '/',
  START: '/start',
  EXAMPLE: '/example',
  HOW_IT_WORKS: '/howitworks'
}

export const NAV_LINKS = [
  { path: ROUTES.HOME, label: 'Home' },
  { path: ROUTES.EXAMPLE, label: 'Voir un exemple' },
  { path: ROUTES.HOW_IT_WORKS, label: 'Comment ça marche' }
]

// ===================== APP CONSTANTS =====================
export const APP_NAME = 'CV Generator'
export const COMPANY_NAME = 'Sopra Steria'

// ===================== FILE UPLOAD CONSTANTS =====================
export const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export const FILE_TYPE_EXTENSIONS = {
  'application/pdf': '.pdf',
  'application/msword': '.doc',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
}

// ===================== THEME CONSTANTS =====================  
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark'
}

export const STORAGE_KEYS = {
  DARK_MODE: 'darkMode'
}