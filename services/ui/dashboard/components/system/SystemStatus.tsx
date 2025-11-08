/**
 * SystemStatus Component
 * Displays system health and performance metrics
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { 
  Activity, 
  AlertCircle, 
  CheckCircle, 
  Server, 
  Database, 
  Cpu,
  HardDrive,
  Zap,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { useState } from 'react'
import { systemAPI } from '@/lib/api-client'
import type { SystemHealth, SystemHealthStatus } from '@/types'

export function SystemStatus() {
  const [isExpanded, setIsExpanded] = useState(false)

  // Fetch system health data
  const { data: health, isLoading, error } = useQuery({
    queryKey: ['system-health'],
    queryFn: systemAPI.getHealth,
    refetchInterval: 5000, // Refetch every 5 seconds
    staleTime: 2000,
  })

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm font-medium">System health unavailable</span>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
            <div className="h-4 w-24 bg-gray-300 dark:bg-gray-600 rounded"></div>
          </div>
          <div className="h-6 w-16 bg-gray-300 dark:bg-gray-600 rounded"></div>
        </div>
      </div>
    )
  }

  if (!health) {
    return null
  }

  const statusConfig = getStatusConfig(health.status)
  const allComponentsHealthy = Object.values(health.components).every(status => status === true)

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Main Status Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${statusConfig.bgColor}`}>
            {statusConfig.icon}
          </div>
          <div className="text-left">
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
                System Health
              </h3>
              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${statusConfig.badgeColor}`}>
                {health.status.toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {allComponentsHealthy ? 'All systems operational' : 'Some services degraded'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {getHealthPercentage(health)}%
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              uptime
            </div>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </div>
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 space-y-4">
          {/* Component Status */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Components
            </h4>
            <div className="space-y-2">
              <ComponentStatus
                name="AI Orchestrator"
                isHealthy={health.components.ai_orchestrator}
                icon={<Server className="w-4 h-4" />}
              />
              <ComponentStatus
                name="Threat Detector"
                isHealthy={health.components.threat_detector}
                icon={<Zap className="w-4 h-4" />}
              />
              <ComponentStatus
                name="Database"
                isHealthy={health.components.database}
                icon={<Database className="w-4 h-4" />}
              />
              <ComponentStatus
                name="Cache (Redis)"
                isHealthy={health.components.cache}
                icon={<HardDrive className="w-4 h-4" />}
              />
              <ComponentStatus
                name="Frigate"
                isHealthy={health.components.frigate}
                icon={<Activity className="w-4 h-4" />}
              />
            </div>
          </div>

          {/* Processing Statistics */}
          {health.statistics && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Performance
              </h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    Processed
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {health.statistics.total_processed?.toLocaleString() || 0}
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    Avg Time
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {health.statistics.avg_processing_time?.toFixed(1) || 0}ms
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    Threats
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {health.statistics.threats_detected?.toLocaleString() || 0}
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    Alerts
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {health.statistics.alerts_generated?.toLocaleString() || 0}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Configuration */}
          {health.configuration && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Configuration
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Threat Detector</span>
                  <span className={`font-medium ${health.configuration.threat_detector_enabled ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
                    {health.configuration.threat_detector_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Max Concurrent Analyses</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {health.configuration.max_concurrent_analyses || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Active Workers</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {health.configuration.workers_active || 0}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Last Updated */}
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400 text-center">
            Last updated: {new Date(health.timestamp).toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Component Status Display
 */
function ComponentStatus({ 
  name, 
  isHealthy, 
  icon 
}: { 
  name: string
  isHealthy: boolean
  icon: React.ReactNode 
}) {
  return (
    <div className="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-900/50">
      <div className="flex items-center space-x-2">
        <div className={`${isHealthy ? 'text-gray-600 dark:text-gray-400' : 'text-red-500'}`}>
          {icon}
        </div>
        <span className="text-sm text-gray-700 dark:text-gray-300">{name}</span>
      </div>
      {isHealthy ? (
        <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
      ) : (
        <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
      )}
    </div>
  )
}

/**
 * Get status configuration
 */
function getStatusConfig(status: SystemHealthStatus) {
  const configs = {
    healthy: {
      icon: <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />,
      bgColor: 'bg-green-100 dark:bg-green-900/30',
      badgeColor: 'bg-green-600 text-white',
    },
    degraded: {
      icon: <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />,
      bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
      badgeColor: 'bg-yellow-600 text-white',
    },
    unhealthy: {
      icon: <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />,
      bgColor: 'bg-red-100 dark:bg-red-900/30',
      badgeColor: 'bg-red-600 text-white',
    },
  }

  return configs[status] || configs.degraded
}

/**
 * Calculate overall health percentage
 */
function getHealthPercentage(health: SystemHealth): number {
  const components = Object.values(health.components)
  const healthyCount = components.filter(status => status === true).length
  return Math.round((healthyCount / components.length) * 100)
}
