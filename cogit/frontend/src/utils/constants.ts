/**
 * Design System Constants
 * Central definition of design tokens, component variants, and application constants
 */

// Design Tokens
export const DESIGN_TOKENS = {
  // Spacing scale (based on 4px grid)
  spacing: {
    xs: '0.25rem',  // 4px
    sm: '0.5rem',   // 8px
    md: '1rem',     // 16px
    lg: '1.5rem',   // 24px
    xl: '2rem',     // 32px
    '2xl': '3rem',  // 48px
    '3xl': '4rem',  // 64px
    '4xl': '6rem',  // 96px
  },

  // Border radius scale
  radius: {
    none: '0',
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },

  // Typography scale
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],      // 12px
    sm: ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
    base: ['1rem', { lineHeight: '1.5rem' }],     // 16px
    lg: ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
    xl: ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
    '2xl': ['1.5rem', { lineHeight: '2rem' }],    // 24px
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }],   // 36px
    '5xl': ['3rem', { lineHeight: '1' }],           // 48px
  },

  // Z-index scale
  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800,
  },

  // Animation durations
  duration: {
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
    slower: '500ms',
  },

  // Breakpoints (mobile-first)
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const

// Component Size Variants
export const COMPONENT_SIZES = {
  button: {
    sm: 'h-9 px-3 text-xs',
    md: 'h-10 px-4 py-2',
    lg: 'h-11 px-8',
    icon: 'h-10 w-10',
  },
  input: {
    sm: 'h-9 px-3 text-sm',
    md: 'h-10 px-3 py-2',
    lg: 'h-11 px-4 text-base',
  },
  avatar: {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  },
  badge: {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-sm',
    lg: 'px-3 py-1 text-sm',
  },
  spinner: {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  },
} as const

// Component Color Variants
export const COMPONENT_VARIANTS = {
  button: {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    outline: 'border border-input bg-background hover:bg-muted hover:text-muted-foreground',
    ghost: 'hover:bg-muted hover:text-muted-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
  },
  badge: {
    default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
    secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
    destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
    outline: 'text-foreground',
    success: 'border-transparent bg-success text-white hover:bg-success/80',
    warning: 'border-transparent bg-warning text-white hover:bg-warning/80',
    info: 'border-transparent bg-info text-white hover:bg-info/80',
  },
  alert: {
    default: 'bg-background text-foreground',
    destructive: 'border-destructive/50 text-destructive dark:border-destructive',
    success: 'border-success/50 text-success dark:border-success',
    warning: 'border-warning/50 text-warning dark:border-warning',
    info: 'border-info/50 text-info dark:border-info',
  },
} as const

// Application Constants
export const APP_CONFIG = {
  name: 'VAULT_APP',
  version: '2.0.0',
  description: 'AI-powered document analysis and workflow automation platform',
  
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 30000,
    retries: 3,
  },

  // WebSocket Configuration
  websocket: {
    baseUrl: import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000',
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
  },

  // File Upload Limits
  fileUpload: {
    maxSize: 100 * 1024 * 1024, // 100MB
    maxFiles: 10,
    allowedTypes: [
      'text/plain',
      'text/markdown',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/csv',
      'application/json',
    ],
  },

  // Theme Configuration
  theme: {
    defaultTheme: 'light',
    storageKey: 'vault-theme',
  },

  // Navigation
  navigation: {
    items: [
      { name: 'Dashboard', href: '/', icon: 'Home' },
      { name: 'Chat', href: '/chat', icon: 'MessageSquare' },
      { name: 'Documents', href: '/documents', icon: 'FileText' },
      { name: 'Sequences', href: '/sequences', icon: 'Workflow' },
      { name: 'Analytics', href: '/analytics', icon: 'BarChart3' },
      { name: 'Settings', href: '/settings', icon: 'Settings' },
    ],
  },

  // Animation Preferences
  animations: {
    respectReducedMotion: true,
    defaultDuration: DESIGN_TOKENS.duration.normal,
    defaultEasing: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Accessibility
  accessibility: {
    skipToContentId: 'main-content',
    ariaLiveRegionId: 'live-region',
  },
} as const

// Icon Size Mapping
export const ICON_SIZES = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 28,
  '2xl': 32,
} as const

// Common Color Mappings
export const STATUS_COLORS = {
  success: 'text-success',
  warning: 'text-warning',
  error: 'text-destructive',
  info: 'text-info',
  neutral: 'text-muted-foreground',
} as const

// Keyboard Shortcuts
export const KEYBOARD_SHORTCUTS = {
  openSearch: ['cmd+k', 'ctrl+k'],
  openCommands: ['cmd+j', 'ctrl+j'],
  toggleTheme: ['cmd+shift+l', 'ctrl+shift+l'],
  newChat: ['cmd+n', 'ctrl+n'],
  toggleSidebar: ['cmd+b', 'ctrl+b'],
} as const

// Export types for TypeScript
export type ComponentSize = keyof typeof COMPONENT_SIZES.button
export type ComponentVariant = keyof typeof COMPONENT_VARIANTS.button
export type IconSize = keyof typeof ICON_SIZES
export type StatusColor = keyof typeof STATUS_COLORS