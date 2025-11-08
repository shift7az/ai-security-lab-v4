/**
 * CameraCard Component
 * Individual camera card with live feed and threat overlay
 */

'use client'

import { useState } from 'react'
import { Camera, MapPin, Clock, Shield, AlertTriangle, Signal } from 'lucide-react'
import { format } from 'date-fns'
import type { Camera as CameraType, ThreatAnalysis } from '@/types'
import { getThreatLevelColor } from './CameraGrid'

interface CameraCardProps {
  camera: CameraType
  threat?: ThreatAnalysis
  isSelected: boolean
  onSelect: () => void
  viewMode: 'grid' | 'list'
}

export function CameraCard({ camera, threat, isSelected, onSelect, viewMode }: CameraCardProps) {
  const [imageError, setImageError] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)

  const statusColor = camera.status === 'online' 
    ? 'bg-green-500' 
    : camera.status === 'offline' 
    ? 'bg-gray-500' 
    : 'bg-red-500'

  const statusText = camera.status === 'online' 
    ? 'Online' 
    : camera.status === 'offline' 
    ? 'Offline' 
    : 'Error'

  return (
    <div
      className={`
        relative bg-white dark:bg-gray-800 rounded-lg overflow-hidden
        border-2 transition-all duration-200 cursor-pointer
        ${isSelected 
          ? 'border-blue-500 shadow-lg shadow-blue-500/50' 
          : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
        }
        ${viewMode === 'list' ? 'flex' : ''}
      `}
      onClick={onSelect}
    >
      {/* Camera Feed */}
      <div className={`relative ${viewMode === 'list' ? 'w-64 flex-shrink-0' : 'aspect-video'} bg-gray-900`}>
        {/* Loading State */}
        {!imageLoaded && !imageError && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        )}

        {/* Camera Image/Stream */}
        {camera.snapshot_url && !imageError ? (
          <img
            src={camera.snapshot_url}
            alt={camera.name}
            className={`w-full h-full object-cover ${imageLoaded ? 'opacity-100' : 'opacity-0'} transition-opacity`}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <Camera className="w-12 h-12 text-gray-600" />
          </div>
        )}

        {/* Status Indicator */}
        <div className="absolute top-2 left-2 flex items-center space-x-1 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-full">
          <div className={`w-2 h-2 rounded-full ${statusColor} ${camera.status === 'online' ? 'animate-pulse' : ''}`}></div>
          <span className="text-xs text-white font-medium">{statusText}</span>
        </div>

        {/* Threat Badge */}
        {threat && threat.threat_score > 0.3 && (
          <div className={`absolute top-2 right-2 px-2 py-1 rounded-lg backdrop-blur-sm ${getThreatLevelColor(threat.threat_level)} font-semibold text-xs flex items-center space-x-1`}>
            <Shield className="w-3 h-3" />
            <span>{threat.threat_level.toUpperCase()}</span>
          </div>
        )}

        {/* Threat Count */}
        {camera.threat_count_24h > 0 && (
          <div className="absolute bottom-2 left-2 px-2 py-1 bg-red-600/90 backdrop-blur-sm rounded-lg flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3 text-white" />
            <span className="text-xs text-white font-semibold">
              {camera.threat_count_24h} threat{camera.threat_count_24h !== 1 ? 's' : ''}
            </span>
          </div>
        )}

        {/* Uptime Indicator */}
        {camera.status === 'online' && (
          <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-lg">
            <span className="text-xs text-white">
              {camera.uptime_percentage?.toFixed(1)}% uptime
            </span>
          </div>
        )}
      </div>

      {/* Camera Info */}
      <div className={`p-4 ${viewMode === 'list' ? 'flex-1' : ''}`}>
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
              {camera.name}
            </h3>
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 space-x-2">
              <MapPin className="w-3 h-3" />
              <span>{camera.location}</span>
            </div>
          </div>
        </div>

        {/* Camera Stats */}
        <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
          <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-400">
            <Signal className="w-3 h-3" />
            <span>{camera.metadata?.resolution || 'HD'}</span>
          </div>
          <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-400">
            <Clock className="w-3 h-3" />
            <span>
              {camera.last_detection 
                ? format(new Date(camera.last_detection.timestamp), 'HH:mm')
                : 'No activity'
              }
            </span>
          </div>
        </div>

        {/* Threat Details */}
        {threat && threat.threat_score > 0.3 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-start justify-between text-xs">
              <div>
                <div className="text-gray-600 dark:text-gray-400 mb-1">Threat Detected</div>
                <div className="font-medium text-gray-900 dark:text-white">
                  {threat.primary_threat}
                </div>
              </div>
              <div className="text-right">
                <div className="text-gray-600 dark:text-gray-400 mb-1">Score</div>
                <div className="font-semibold text-gray-900 dark:text-white">
                  {(threat.threat_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>
            
            {threat.factors && threat.factors.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {threat.factors.slice(0, 3).map((factor, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
                  >
                    {factor.name}
                  </span>
                ))}
                {threat.factors.length > 3 && (
                  <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs">
                    +{threat.factors.length - 3} more
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Last Detection */}
        {camera.last_detection && !threat && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-400">
            Last: {camera.last_detection.detection_type} at{' '}
            {format(new Date(camera.last_detection.timestamp), 'HH:mm:ss')}
          </div>
        )}
      </div>

      {/* Selection Indicator */}
      {isSelected && (
        <div className="absolute inset-0 border-4 border-blue-500 rounded-lg pointer-events-none"></div>
      )}
    </div>
  )
}
