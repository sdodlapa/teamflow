import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'

// Import pages (will be created as we build them)
// import HomePage from './pages/HomePage'
// import LoginPage from './pages/LoginPage'
// import DashboardPage from './pages/DashboardPage'

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<HomePage />} />
            {/* <Route path="/login" element={<LoginPage />} /> */}
            {/* <Route path="/dashboard" element={<DashboardPage />} /> */}
          </Routes>
          
          {/* Toast notifications */}
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
      
      {/* React Query DevTools (only in development) */}
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  )
}

// Temporary HomePage component until we create the proper one
function HomePage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to TeamFlow
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Enterprise task management and collaboration platform
        </p>
        <div className="space-y-4">
          <div className="card p-6 max-w-md mx-auto">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Development Setup Complete
            </h2>
            <p className="text-gray-600 text-sm">
              Frontend is running with React, TypeScript, and Tailwind CSS.
              Backend API is available at http://localhost:8000
            </p>
          </div>
          <div className="flex space-x-4 justify-center">
            <button className="btn-primary px-6 py-2">
              Get Started
            </button>
            <button className="btn-outline px-6 py-2">
              View Docs
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App