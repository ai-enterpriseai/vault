# 00-3: Frontend Foundation - React + TypeScript + Tailwind

## Objective
Set up a modern React frontend with TypeScript, Tailwind CSS, and essential development tools. Create the foundation for a professional UI with proper routing, state management, and component architecture.

## Prerequisites
- Backend core structure completed (00-2)
- Vite + React project initialized

## Implementation Steps

### 1. Development Environment Setup
- Configure Vite with proper TypeScript settings
- Set up Tailwind CSS with custom configuration
- Install and configure ESLint, Prettier, and Husky
- Set up path aliases for cleaner imports

### 2. Design System Foundation
- Create color palette and theme configuration
- Set up typography scale and spacing system
- Configure dark/light mode support
- Create base CSS variables and utilities

### 3. Core UI Components
- Build foundational UI components (Button, Input, Card, etc.)
- Implement layout components (Header, Sidebar, Footer)
- Create loading states and error boundaries
- Set up icon system with Lucide React

### 4. Routing and Navigation
- Set up React Router for SPA navigation
- Create route structure matching planned pages
- Implement protected route patterns
- Add navigation components and breadcrumbs

### 5. State Management Setup
- Configure Zustand for lightweight state management
- Create stores for UI state, auth, and app data
- Set up persistent storage for user preferences
- Implement state hydration and serialization

### 6. API Integration Foundation
- Set up Axios with interceptors
- Create base API service classes
- Implement error handling and retry logic
- Add request/response logging

## Files to Create

### Build Configuration
1. `frontend/vite.config.ts` - Enhanced Vite configuration
2. `frontend/tailwind.config.js` - Custom Tailwind setup
3. `frontend/tsconfig.json` - TypeScript configuration
4. `frontend/.eslintrc.json` - ESLint rules
5. `frontend/.prettierrc` - Prettier configuration
6. `frontend/postcss.config.js` - PostCSS setup

### Styling and Design System
7. `frontend/src/styles/globals.css` - Global styles and CSS variables
8. `frontend/src/styles/components.css` - Component-specific styles
9. `frontend/src/utils/cn.ts` - Class name utility function
10. `frontend/src/utils/constants.ts` - Design system constants

### Core UI Components
11. `frontend/src/components/ui/Button.tsx`
12. `frontend/src/components/ui/Input.tsx`
13. `frontend/src/components/ui/Card.tsx`
14. `frontend/src/components/ui/Modal.tsx`
15. `frontend/src/components/ui/Dropdown.tsx`
16. `frontend/src/components/ui/index.ts` - Component exports

### Layout Components
17. `frontend/src/components/layout/MainLayout.tsx`
18. `frontend/src/components/layout/Sidebar.tsx`
19. `frontend/src/components/layout/Header.tsx`
20. `frontend/src/components/layout/Footer.tsx`

### Common Components
21. `frontend/src/components/common/LoadingSpinner.tsx`
22. `frontend/src/components/common/ErrorBoundary.tsx`
23. `frontend/src/components/common/ThemeToggle.tsx`
24. `frontend/src/components/common/NotificationToast.tsx`

### Routing and Pages
25. `frontend/src/App.tsx` - Main application component
26. `frontend/src/pages/Dashboard.tsx` - Dashboard page placeholder
27. `frontend/src/pages/NotFound.tsx` - 404 page
28. `frontend/src/routes/index.tsx` - Route configuration

### State Management
29. `frontend/src/store/uiStore.ts` - UI state (theme, sidebar)
30. `frontend/src/store/authStore.ts` - Authentication state
31. `frontend/src/hooks/useLocalStorage.ts` - Local storage hook

### API Services
32. `frontend/src/services/api.ts` - Base API configuration
33. `frontend/src/services/types.ts` - API type definitions
34. `frontend/src/utils/api-client.ts` - API client utilities

### Type Definitions
35. `frontend/src/types/index.ts` - Common type definitions
36. `frontend/src/types/ui.ts` - UI component types

## Key Technologies and Libraries

### Core Dependencies
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.18.0",
  "typescript": "^5.2.0",
  "vite": "^4.5.0"
}
```

### UI and Styling
```json
{
  "tailwindcss": "^3.3.0",
  "clsx": "^2.0.0",
  "tailwind-merge": "^1.14.0",
  "lucide-react": "^0.290.0",
  "framer-motion": "^10.16.0"
}
```

### State Management and Data
```json
{
  "zustand": "^4.4.0",
  "axios": "^1.6.0",
  "react-query": "^3.39.0"
}
```

### Development Tools
```json
{
  "eslint": "^8.50.0",
  "@typescript-eslint/eslint-plugin": "^6.7.0",
  "prettier": "^3.0.0",
  "husky": "^8.0.0"
}
```

## Design System Configuration

### Color Palette
```css
:root {
  /* Light mode */
  --color-primary: 16 185 129; /* Emerald 500 */
  --color-secondary: 99 102 241; /* Indigo 500 */
  --color-background: 255 255 255;
  --color-foreground: 15 23 42; /* Slate 900 */
  --color-muted: 241 245 249; /* Slate 100 */
  --color-border: 226 232 240; /* Slate 200 */
}

[data-theme="dark"] {
  /* Dark mode */
  --color-background: 15 23 42; /* Slate 900 */
  --color-foreground: 248 250 252; /* Slate 50 */
  --color-muted: 30 41 59; /* Slate 800 */
  --color-border: 51 65 85; /* Slate 600 */
}
```

### Component Architecture Pattern
```tsx
// Base component pattern
interface ComponentProps {
  children?: React.ReactNode;
  className?: string;
  variant?: 'default' | 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
}

export const Component = ({ 
  children, 
  className, 
  variant = 'default',
  size = 'md',
  ...props 
}: ComponentProps) => {
  return (
    <div 
      className={cn(
        'base-styles',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
```

## Success Criteria
- [ ] Frontend starts with hot reload working
- [ ] Tailwind CSS properly configured and working
- [ ] Dark/light theme toggle functional
- [ ] Basic routing between pages works
- [ ] UI components render correctly
- [ ] State management stores function properly
- [ ] API client can make requests to backend
- [ ] TypeScript compilation has no errors
- [ ] ESLint and Prettier run without issues

## Testing Strategy
- Set up Vitest for unit testing
- Create basic component tests
- Test routing functionality
- Verify theme switching
- Test API client error handling

## Performance Considerations
- Configure Vite for optimal bundling
- Set up code splitting for routes
- Implement lazy loading for heavy components
- Optimize Tailwind CSS build size

## Estimated Time
5-6 hours

## Next Steps
After completion, proceed to `01-1-plan-chat-api-backend.md`