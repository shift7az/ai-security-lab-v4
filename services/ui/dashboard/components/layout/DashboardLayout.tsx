/**
 * DashboardLayout Component
 * Main layout wrapper for the security dashboard with navigation and header
 */

'use client'

import { ReactNode } from 'react'
import { Shield, Menu, Bell, Settings, User } from 'lucide-react'

interface DashboardLayoutProps {
  children: ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Top Navigation Bar */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                  AI Security Lab
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  v4.0 Intelligence Dashboard
                </p>
              </div>
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <button className="relative p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>

              {/* Settings */}
              <a
                href="/settings"
                className="p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="System Settings"
              >
                <Settings className="w-5 h-5" />
              </a>

              {/* User Menu */}
              <button className="flex items-center space-x-2 p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                <User className="w-5 h-5" />
                <span className="text-sm font-medium hidden md:block">Admin</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <p>© 2024 AI Security Lab v4.0. All rights reserved.</p>
            <div className="flex items-center space-x-4">
              <a href="#" className="hover:text-gray-900 dark:hover:text-white transition-colors">
                Documentation
              </a>
              <a href="#" className="hover:text-gray-900 dark:hover:text-white transition-colors">
                Support
              </a>
              <a href="#" className="hover:text-gray-900 dark:hover:text-white transition-colors">
                API
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
