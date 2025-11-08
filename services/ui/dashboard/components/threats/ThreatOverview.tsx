/**
 * ThreatOverview Component
 * Displays summary statistics cards for threats, alerts, cameras, and system health
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { 
  Shield, 
  AlertTriangle, 
  Camera, 
  Activity,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'
import { dashboardAPI } from '@/lib/api-client'
import { StatCard } from './StatCard'
import { StatCardSkeleton } from './StatCardSkeleton'

export function ThreatOverview() {
  // Fetch dashboard overview data
  const { data: overview, isLoading, error } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: dashboardAPI.getOverview,
    refetchInterval: 10000, // Refetch every 10 seconds
    staleTime: 5000, // Consider data stale after 5 seconds
  })

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
          <AlertTriangle className="w-5 h-5" />
          <span className="text-sm font-medium">Failed to load overview data</span>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (!overview) {
    return null
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Total Threats Card */}
      <StatCard
        title="Total Threats (24h)"
        value={overview.total_threats}
        trend={overview.threat_trend}
        icon={<Shield className="w-6 h-6" />}
        color="red"
        subtitle="threats detected"
      />

      {/* Critical Alerts Card */}
      <StatCard
        title="Critical Alerts"
        value={overview.critical_alerts}
        trend={overview.alert_trend}
        icon={<AlertTriangle className="w-6 h-6" />}
        color="orange"
        subtitle="require attention"
      />

      {/* Active Cameras Card */}
      <StatCard
        title="Active Cameras"
        value={overview.active_cameras}
        total={overview.total_cameras}
        icon={<Camera className="w-6 h-6" />}
        color="blue"
        subtitle={`of ${overview.total_cameras} cameras`}
        percentage={(overview.active_cameras / overview.total_cameras) * 100}
      />

      {/* System Health Card */}
      <StatCard
        title="System Health"
        value={overview.system_health}
        icon={<Activity className="w-6 h-6" />}
        color={getHealthColor(overview.health_status)}
        subtitle={overview.health_status}
        isPercentage
      />
    </div>
  )
}

/**
 * Get color based on health status
 */
function getHealthColor(status: string): 'green' | 'yellow' | 'red' | 'blue' | 'orange' {
  switch (status) {
    case 'healthy':
      return 'green'
    case 'degraded':
      return 'yellow'
    case 'unhealthy':
      return 'red'
    default:
      return 'blue'
  }
}

/**
 * Get trend icon based on direction
 */
export function getTrendIcon(direction: 'up' | 'down' | 'stable') {
  switch (direction) {
    case 'up':
      return <TrendingUp className="w-4 h-4" />
    case 'down':
      return <TrendingDown className="w-4 h-4" />
    case 'stable':
      return <Minus className="w-4 h-4" />
  }
}

/**
 * Get trend color based on direction and context
 */
export function getTrendColor(direction: 'up' | 'down' | 'stable', isGood: boolean): string {
  if (direction === 'stable') {
    return 'text-gray-500 dark:text-gray-400'
  }
  
  const isPositive = (direction === 'up' && isGood) || (direction === 'down' && !isGood)
  
  return isPositive
    ? 'text-green-600 dark:text-green-400'
    : 'text-red-600 dark:text-red-400'
}
