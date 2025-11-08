/**
 * CameraGrid Component
 * Displays a responsive grid of live camera feeds with threat overlays
 */

'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Camera as CameraIcon, AlertTriangle, Wifi, WifiOff } from 'lucide-react'
import { dashboardAPI } from '@/lib/api-client'
import { useWebSocketContext } from '@/hooks/useWebSocket'
import type { Camera, ThreatLevel } from '@/types'
import { CameraCard } from './CameraCard'
import { CameraCardSkeleton } from './CameraCardSkeleton'

interface CameraGridProps {
  selectedCamera: string | null
  onCameraSelect: (cameraId: string | null) => void
}

export function CameraGrid({ selectedCamera, onCameraSelect }: CameraGridProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  // Fetch cameras data
  const { data: cameras, isLoading, error, refetch } = useQuery({
    queryKey: ['cameras'],
    queryFn: dashboardAPI.getCameras,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  })

  // Get real-time threat updates from WebSocket
  const { threats, isConnected: wsConnected } = useWebSocketContext()

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 bg-red-50 dark:bg-red-900/10 rounded-lg border border-red-200 dark:border-red-800">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
            Failed to Load Cameras
          </h3>
          <p className="text-red-700 dark:text-red-300 mb-4">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className={`grid ${getGridClass(viewMode)} gap-4`}>
        {Array.from({ length: 6 }).map((_, i) => (
          <CameraCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (!cameras || cameras.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <CameraIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
            No Cameras Found
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Add cameras to start monitoring
          </p>
        </div>
      </div>
    )
  }

  // Filter to show only selected camera if one is selected
  const displayCameras = selectedCamera
    ? cameras.filter(cam => cam.id === selectedCamera)
    : cameras

  return (
    <div className="space-y-4">
      {/* View Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {cameras.length} camera{cameras.length !== 1 ? 's' : ''}
          </span>
          {wsConnected ? (
            <div className="flex items-center space-x-1 text-green-600 dark:text-green-400">
              <Wifi className="w-4 h-4" />
              <span className="text-xs">Live</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1 text-yellow-600 dark:text-yellow-400">
              <WifiOff className="w-4 h-4" />
              <span className="text-xs">Connecting...</span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`px-3 py-1 rounded-lg text-sm transition-colors ${
              viewMode === 'grid'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            Grid
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-3 py-1 rounded-lg text-sm transition-colors ${
              viewMode === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            List
          </button>
        </div>
      </div>

      {/* Camera Grid */}
      <div className={`grid ${getGridClass(viewMode)} gap-4`}>
        {displayCameras.map((camera) => {
          const threat = threats[camera.id]
          
          return (
            <CameraCard
              key={camera.id}
              camera={camera}
              threat={threat}
              isSelected={selectedCamera === camera.id}
              onSelect={() => onCameraSelect(camera.id === selectedCamera ? null : camera.id)}
              viewMode={viewMode}
            />
          )
        })}
      </div>

      {/* Selected Camera Info */}
      {selectedCamera && (
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-900 dark:text-blue-100">
              Viewing: {cameras.find(c => c.id === selectedCamera)?.name}
            </span>
            <button
              onClick={() => onCameraSelect(null)}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Show All Cameras
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Get Tailwind grid class based on view mode
 */
function getGridClass(viewMode: 'grid' | 'list'): string {
  if (viewMode === 'list') {
    return 'grid-cols-1'
  }
  return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
}

/**
 * Get threat level color
 */
export function getThreatLevelColor(level: ThreatLevel): string {
  const colors: Record<ThreatLevel, string> = {
    none: 'text-gray-500 bg-gray-100 dark:bg-gray-800',
    low: 'text-green-600 bg-green-100 dark:bg-green-900/30',
    medium: 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30',
    high: 'text-orange-600 bg-orange-100 dark:bg-orange-900/30',
    critical: 'text-red-600 bg-red-100 dark:bg-red-900/30',
  }
  return colors[level] || colors.none
}
