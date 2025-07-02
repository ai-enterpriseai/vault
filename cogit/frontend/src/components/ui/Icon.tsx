import { forwardRef } from 'react'
import { LucideIcon, LucideProps } from 'lucide-react'
import { cn } from '@/utils/cn'
import { ICON_SIZES, type IconSize } from '@/utils/constants'

// Common icon imports from Lucide React
import {
  Home,
  MessageSquare,
  FileText,
  Settings,
  BarChart3,
  Search,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  ChevronUp,
  Plus,
  Minus,
  Check,
  AlertTriangle,
  Info,
  XCircle,
  CheckCircle,
  Upload,
  Download,
  Edit,
  Trash2,
  Copy,
  Share,
  Eye,
  EyeOff,
  Sun,
  Moon,
  User,
  Mail,
  Phone,
  Calendar,
  Clock,
  MapPin,
  Link,
  ExternalLink,
  Heart,
  Star,
  Bookmark,
  Filter,
  SortAsc,
  SortDesc,
  Refresh,
  Loader2,
  Zap,
  Shield,
  Lock,
  Unlock,
  Key,
  Database,
  Server,
  Cloud,
  Wifi,
  WifiOff,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Stop,
  SkipForward,
  SkipBack,
  Maximize,
  Minimize,
  MoreHorizontal,
  MoreVertical,
} from 'lucide-react'

// Icon name to component mapping
export const iconMap = {
  // Navigation
  home: Home,
  'message-square': MessageSquare,
  'file-text': FileText,
  settings: Settings,
  'bar-chart-3': BarChart3,
  search: Search,
  menu: Menu,
  x: X,

  // Arrows & Chevrons
  'chevron-down': ChevronDown,
  'chevron-right': ChevronRight,
  'chevron-left': ChevronLeft,
  'chevron-up': ChevronUp,

  // Actions
  plus: Plus,
  minus: Minus,
  check: Check,
  edit: Edit,
  'trash-2': Trash2,
  copy: Copy,
  share: Share,
  upload: Upload,
  download: Download,

  // Status & Alerts
  'alert-triangle': AlertTriangle,
  info: Info,
  'x-circle': XCircle,
  'check-circle': CheckCircle,

  // Visibility
  eye: Eye,
  'eye-off': EyeOff,

  // Theme
  sun: Sun,
  moon: Moon,

  // User & Contact
  user: User,
  mail: Mail,
  phone: Phone,
  calendar: Calendar,
  clock: Clock,
  'map-pin': MapPin,

  // Links
  link: Link,
  'external-link': ExternalLink,

  // Favorites
  heart: Heart,
  star: Star,
  bookmark: Bookmark,

  // Data & Sorting
  filter: Filter,
  'sort-asc': SortAsc,
  'sort-desc': SortDesc,
  refresh: Refresh,
  'loader-2': Loader2,

  // Security & System
  zap: Zap,
  shield: Shield,
  lock: Lock,
  unlock: Unlock,
  key: Key,
  database: Database,
  server: Server,
  cloud: Cloud,

  // Connectivity
  wifi: Wifi,
  'wifi-off': WifiOff,

  // Media
  'volume-2': Volume2,
  'volume-x': VolumeX,
  play: Play,
  pause: Pause,
  stop: Stop,
  'skip-forward': SkipForward,
  'skip-back': SkipBack,

  // Layout
  maximize: Maximize,
  minimize: Minimize,
  'more-horizontal': MoreHorizontal,
  'more-vertical': MoreVertical,
} as const

export type IconName = keyof typeof iconMap

interface IconProps extends Omit<LucideProps, 'size'> {
  name: IconName
  size?: IconSize | number
  className?: string
}

/**
 * Icon component wrapper for Lucide React icons
 * Provides consistent sizing and easy icon management
 */
export const Icon = forwardRef<SVGSVGElement, IconProps>(
  ({ name, size = 'md', className, ...props }, ref) => {
    const IconComponent = iconMap[name] as LucideIcon

    if (!IconComponent) {
      console.warn(`Icon "${name}" not found in iconMap`)
      return null
    }

    const iconSize = typeof size === 'number' ? size : ICON_SIZES[size]

    return (
      <IconComponent
        ref={ref}
        size={iconSize}
        className={cn('shrink-0', className)}
        {...props}
      />
    )
  }
)

Icon.displayName = 'Icon'

// Convenience component for loading spinners
interface SpinnerProps extends Omit<IconProps, 'name'> {
  className?: string
}

export const Spinner = forwardRef<SVGSVGElement, SpinnerProps>(
  ({ size = 'md', className, ...props }, ref) => (
    <Icon
      ref={ref}
      name="loader-2"
      size={size}
      className={cn('animate-spin', className)}
      {...props}
    />
  )
)

Spinner.displayName = 'Spinner'

// Export individual icons for direct use if needed
export {
  Home,
  MessageSquare,
  FileText,
  Settings,
  BarChart3,
  Search,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  ChevronUp,
  Plus,
  Minus,
  Check,
  AlertTriangle,
  Info,
  XCircle,
  CheckCircle,
  Upload,
  Download,
  Edit,
  Trash2,
  Copy,
  Share,
  Eye,
  EyeOff,
  Sun,
  Moon,
  User,
  Mail,
  Phone,
  Calendar,
  Clock,
  MapPin,
  Link,
  ExternalLink,
  Heart,
  Star,
  Bookmark,
  Filter,
  SortAsc,
  SortDesc,
  Refresh,
  Loader2,
  Zap,
  Shield,
  Lock,
  Unlock,
  Key,
  Database,
  Server,
  Cloud,
  Wifi,
  WifiOff,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Stop,
  SkipForward,
  SkipBack,
  Maximize,
  Minimize,
  MoreHorizontal,
  MoreVertical,
}