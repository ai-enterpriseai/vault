import { BrowserRouter as Router } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import AppRoutes from './routes'
import ErrorBoundary from './components/common/ErrorBoundary'

// Create a query client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="min-h-screen bg-background text-foreground">
            <AppRoutes />
          </div>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App