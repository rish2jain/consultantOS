import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'
import { ReactQueryProvider } from './providers'
import { Navigation, KeyboardShortcuts } from './components'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ConsultantOS - Business Intelligence Dashboard',
  description: 'Strategic analysis dashboard for independent consultants',
}

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning={true}>
      <body className={inter.className}>
        <ReactQueryProvider>
          <KeyboardShortcuts />
          <div className="min-h-screen bg-gray-50">
            <Navigation />
            <main className="pb-12">
              {children}
            </main>
            <footer className="bg-white border-t border-gray-200 py-6">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
                  <p className="text-sm text-gray-500">
                    &copy; {new Date().getFullYear()} ConsultantOS. All rights reserved.
                  </p>
                  <div className="flex space-x-6">
                    <Link href="/terms" className="text-sm text-gray-500 hover:text-gray-900">
                      Terms
                    </Link>
                    <Link href="/privacy" className="text-sm text-gray-500 hover:text-gray-900">
                      Privacy
                    </Link>
                    <Link href="/help" className="text-sm text-gray-500 hover:text-gray-900">
                      Help
                    </Link>
                  </div>
                </div>
              </div>
            </footer>
          </div>
        </ReactQueryProvider>
      </body>
    </html>
  )
}

