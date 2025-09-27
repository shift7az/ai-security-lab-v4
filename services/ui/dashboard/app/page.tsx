'use client'

import { useState } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { CameraGrid } from '@/components/cameras/CameraGrid'
import { ThreatOverview } from '@/components/threats/ThreatOverview'
import { AlertPanel } from '@/components/alerts/AlertPanel'
import { SystemStatus } from '@/components/system/SystemStatus'
import { IntelligenceTimeline } from '@/components/intelligence/IntelligenceTimeline'

export default function SecurityDashboard() {
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null)

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              AI Security Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Real-time intelligent surveillance monitoring
            </p>
          </div>
          <SystemStatus />
        </div>

        {/* Threat Overview */}
        <ThreatOverview />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Camera Grid - Takes up 3 columns */}
          <div className="xl:col-span-3">
            <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700">
              <div className="p-6 border-b border-gray-200 dark:border-dark-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Live Camera Feeds
                  </h2>
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Live
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="p-6">
                <CameraGrid
                  selectedCamera={selectedCamera}
                  onCameraSelect={setSelectedCamera}
                />
              </div>
            </div>
          </div>

          {/* Alert Panel - Takes up 1 column */}
          <div className="xl:col-span-1">
            <AlertPanel />
          </div>
        </div>

        {/* Intelligence Timeline */}
        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700">
          <div className="p-6 border-b border-gray-200 dark:border-dark-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Intelligence Timeline
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Recent threat detections and system events
            </p>
          </div>
          <div className="p-6">
            <IntelligenceTimeline />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
