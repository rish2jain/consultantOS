'use client';

import { useEffect, useState } from 'react';
import ChatDemo from '@/app/components/ChatDemo';
import ForecastChart from '@/app/components/ForecastChart';
import { healthCheck } from '@/lib/mvp-api';
import { Sparkles, Activity, AlertCircle } from 'lucide-react';

export default function MVPDemoPage() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'error'>('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthCheck();
        setBackendStatus('healthy');
      } catch {
        setBackendStatus('error');
      }
    };

    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  ConsultantOS
                </h1>
                <p className="text-sm text-gray-600">
                  AI-Powered Competitive Intelligence Platform
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {backendStatus === 'checking' && (
                <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 rounded-full">
                  <Activity className="w-4 h-4 text-yellow-600 animate-pulse" />
                  <span className="text-xs font-medium text-yellow-700">Connecting...</span>
                </div>
              )}
              {backendStatus === 'healthy' && (
                <div className="flex items-center gap-2 px-3 py-1 bg-green-100 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-xs font-medium text-green-700">Backend Online</span>
                </div>
              )}
              {backendStatus === 'error' && (
                <div className="flex items-center gap-2 px-3 py-1 bg-red-100 rounded-full">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <span className="text-xs font-medium text-red-700">Backend Offline</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Banner */}
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-blue-900 mb-1">
                Hackathon MVP Demo - November 2025
              </h3>
              <p className="text-sm text-blue-700">
                Explore our AI-powered competitive intelligence platform with real-time chat assistance
                and market forecasting capabilities. Built for the Hackathon MVP showcase.
              </p>
            </div>
          </div>
        </div>

        {/* Backend Error Alert */}
        {backendStatus === 'error' && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-red-900 mb-1">
                  Backend Connection Error
                </h3>
                <p className="text-sm text-red-700 mb-2">
                  Unable to connect to the backend API. Please ensure the backend is running at{' '}
                  <code className="bg-red-100 px-1 py-0.5 rounded">http://localhost:8080</code>
                </p>
                <p className="text-xs text-red-600">
                  Start backend with: <code className="bg-red-100 px-1 py-0.5 rounded">python main.py</code>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Demo Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-300px)] min-h-[600px]">
          {/* Chat Section */}
          <div className="flex flex-col">
            <ChatDemo />
          </div>

          {/* Forecast Section */}
          <div className="flex flex-col">
            <ForecastChart />
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Chat Assistant</h3>
            <p className="text-sm text-gray-600">
              Get instant answers about competitive intelligence, market analysis, and business strategy
              powered by Google Gemini 2.5 Flash.
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Market Forecasting</h3>
            <p className="text-sm text-gray-600">
              AI-powered predictions with confidence intervals to help you make data-driven strategic
              decisions.
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-pink-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-time Insights</h3>
            <p className="text-sm text-gray-600">
              Continuous monitoring and analysis to keep you ahead of market trends and competitive
              dynamics.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-center sm:text-left">
              <p className="text-sm text-gray-600">
                Powered by{' '}
                <span className="font-semibold text-gray-900">Google Cloud Run</span> &{' '}
                <span className="font-semibold text-gray-900">Gemini 2.5 Flash</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Hackathon MVP Demo • November 2025
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full">
                <span className="text-xs font-semibold text-white">MVP DEMO</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
