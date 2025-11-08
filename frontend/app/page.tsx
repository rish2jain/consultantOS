'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { BarChart3, FileText, Key, TrendingUp, Clock, CheckCircle } from 'lucide-react'
import { format } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

interface Report {
  report_id: string
  company: string
  industry?: string
  frameworks: string[]
  status: string
  confidence_score?: number
  created_at: string
  execution_time_seconds?: number
  pdf_url?: string
}

interface Metrics {
  total_reports: number
  total_requests: number
  cache_hit_rate: number
  avg_execution_time: number
}

export default function Dashboard() {
  const [apiKey, setApiKey] = useState<string>('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check in-memory state and refresh token from server if needed
    // Note: In production, implement server-side auth with HttpOnly cookies
    // For now, check if we have an in-memory token, otherwise call silent-auth endpoint
    const checkAuth = async () => {
      // If no in-memory token, try to refresh from server
      try {
        // Call server endpoint to refresh/issue access token (server sets HttpOnly cookie)
        const response = await axios.post(`${API_URL}/auth/silent-auth`, {}, {
          withCredentials: true // Include HttpOnly cookies
        })
        if (response.data.access_token) {
          setApiKey(response.data.access_token) // Store only in memory
          setIsAuthenticated(true)
        }
      } catch (error) {
        // Not authenticated, user needs to login
        setIsAuthenticated(false)
      }
    }
    checkAuth()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Run once on mount

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const email = formData.get('email') as string
    const password = formData.get('password') as string

    try {
      const response = await axios.post(`${API_URL}/users/login`, {
        email,
        password,
      })
      
      const token = response.data.access_token
      // Store token only in memory (server sets HttpOnly refresh cookie)
      setApiKey(token)
      setIsAuthenticated(true)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Login failed')
    }
  }

  const handleLogout = async () => {
    // Clear in-memory token and call server logout endpoint
    try {
      await axios.post(`${API_URL}/auth/logout`, {}, {
        withCredentials: true // Include HttpOnly cookies for server to clear
      })
    } catch (error) {
      // Continue with logout even if server call fails
    }
    setApiKey('')
    setIsAuthenticated(false)
  }

  // Fetch reports
  const { data: reportsData, isLoading: reportsLoading } = useQuery({
    queryKey: ['reports', apiKey],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/reports`, {
        headers: { 'X-API-Key': apiKey },
      })
      return response.data
    },
    enabled: isAuthenticated && !!apiKey,
  })

  // Fetch metrics
  const { data: metricsData } = useQuery({
    queryKey: ['metrics', apiKey],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/metrics`, {
        headers: { 'X-API-Key': apiKey },
      })
      return response.data
    },
    enabled: isAuthenticated && !!apiKey,
  })

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
          <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">
            ConsultantOS Dashboard
          </h1>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                name="email"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition-colors font-medium"
            >
              Sign In
            </button>
          </form>
          <p className="mt-4 text-sm text-center text-gray-600">
            Don't have an account?{' '}
            <a href="/register" className="text-primary-600 hover:underline">
              Register
            </a>
          </p>
        </div>
      </div>
    )
  }

  const reports: Report[] = reportsData?.reports || []
  const metrics: Metrics = metricsData?.metrics || {
    total_reports: reports.length,
    total_requests: 0,
    cache_hit_rate: 0,
    avg_execution_time: 0,
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">ConsultantOS Dashboard</h1>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Reports"
            value={metrics.total_reports}
            icon={<FileText className="w-6 h-6" />}
            color="blue"
          />
          <MetricCard
            title="Total Requests"
            value={metrics.total_requests}
            icon={<TrendingUp className="w-6 h-6" />}
            color="green"
          />
          <MetricCard
            title="Cache Hit Rate"
            value={`${metrics.cache_hit_rate.toFixed(1)}%`}
            icon={<BarChart3 className="w-6 h-6" />}
            color="purple"
          />
          <MetricCard
            title="Avg Execution"
            value={`${metrics.avg_execution_time.toFixed(1)}s`}
            icon={<Clock className="w-6 h-6" />}
            color="orange"
          />
        </div>

        {/* Reports Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Reports</h2>
          </div>
          {reportsLoading ? (
            <div className="p-8 text-center text-gray-500">Loading reports...</div>
          ) : reports.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No reports yet. Generate your first analysis!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Frameworks
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Confidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {reports.map((report) => (
                    <tr key={report.report_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {report.company}
                        </div>
                        {report.industry && (
                          <div className="text-sm text-gray-500">{report.industry}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-wrap gap-1">
                          {report.frameworks.map((f) => (
                            <span
                              key={f}
                              className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary-100 text-primary-800"
                            >
                              {f}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            report.status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {report.status === 'completed' && (
                            <CheckCircle className="w-3 h-3 mr-1" />
                          )}
                          {report.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {report.confidence_score
                          ? `${(report.confidence_score * 100).toFixed(0)}%`
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {format(new Date(report.created_at), 'MMM d, yyyy')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {report.pdf_url && (
                          <a
                            href={report.pdf_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 hover:text-primary-900"
                          >
                            View PDF
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function MetricCard({
  title,
  value,
  icon,
  color,
}: {
  title: string
  value: string | number
  icon: React.ReactNode
  color: string
}) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`${colorClasses[color as keyof typeof colorClasses]} text-white p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

