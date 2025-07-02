import { Routes, Route } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'
import NotFound from '../pages/NotFound'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}