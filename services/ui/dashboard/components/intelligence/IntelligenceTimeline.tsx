/**
 * IntelligenceTimeline Component
 * Chronological feed of threat detections and system events
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { 
  Shield, 
  AlertTriangle, 
  Camera, 
  Activity,
  Clock,
  ChevronDown,
  Filter,
  Download
} from 'lucide-react'
import { useState } from 'react'
import { format } from 'date-fns'
import { dashboardAPI } from '@/lib/api-client'
import type { TimelineEvent, ThreatLevel } from '@/types'

export function IntelligenceTimeline() {
  const [timeRange, setTimeRange] = useState(24) // hours
  const [filterType, setFilterType] = useState<'all' | 'threat' | 'alert' | 'system' | 'camera'>('all')
  const [showFilters, setShowFilters] = useState(false)

  // Fetch timeline events
  const { data: events, isLoading, error } = useQuery({
    queryKey: ['timeline-events', timeRange],
    queryFn: () => dashboardAPI.getTimelineEvents(timeRange),
    refetchInterval: 10000, // Refetch every 10 seconds
    staleTime: 5000,
  })

  const handleExport = () => {
    if (!events) return
    
    const dataStr = JSON.stringify(events, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `intelligence-timeline-${new Date().toISOString()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
          <AlertTriangle className="w-5 h-5" />
          <span className="text-sm font-medium">Failed to load timeline</span>
        </div>
      </div>
    )
  }

  // Filter events
  const filteredEvents = events?.filter(event => 
    filterType === 'all' || event.type === filterType
  ) || []

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {/* Time Range Selector */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={1}>Last hour</option>
            <option value={6}>Last 6 hours</option>
            <option value={24}>Last 24 hours</option>
            <option value={72}>Last 3 days</option>
            <option value={168}>Last week</option>
          </select>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1 ${
              showFilters
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>

        {/* Export Button */}
        <button
          onClick={handleExport}
          disabled={!events || events.length === 0}
          className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center space-x-1"
        >
          <Download className="w-4 h-4" />
          <span>Export</span>
        </button>
      </div>

      {/* Filter Options */}
      {showFilters && (
        <div className="flex flex-wrap gap-2 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
          {(['all', 'threat', 'alert', 'system', 'camera'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filterType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      )}

      {/* Timeline */}
      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

        {/* Events */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredEvents.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-gray-500 dark:text-gray-400">
              <Activity className="w-12 h-12 mb-2 opacity-50" />
              <p className="text-sm">No events in this time range</p>
            </div>
          ) : (
            filteredEvents.map((event, index) => (
              <TimelineEventItem key={event.id} event={event} isFirst={index === 0} />
            ))
          )}
        </div>

        {/* Load More */}
        {filteredEvents.length > 0 && (
          <div className="mt-6 flex justify-center">
            <button className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors flex items-center space-x-1">
              <ChevronDown className="w-4 h-4" />
              <span>Viewing {filteredEvents.length} events</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Timeline Event Item
 */
function TimelineEventItem({ event, isFirst }: { event: TimelineEvent; isFirst: boolean }) {
  const [isExpanded, setIsExpanded] = useState(isFirst)

  const typeConfig = getEventTypeConfig(event.type)
  const threatLevelColor = event.threat_level ? getThreatLevelColor(event.threat_level) : null

  return (
    <div className="relative pl-16">
      {/* Timeline Node */}
      <div className={`absolute left-6 -ml-2 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800 ${typeConfig.bgColor}`}></div>

      {/* Event Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              {/* Icon */}
              <div className={`p-2 rounded-lg ${typeConfig.bgColor}`}>
                {typeConfig.icon}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                    {event.title}
                  </h4>
                  {threatLevelColor && (
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${threatLevelColor}`}>
                      {event.threat_level?.toUpperCase()}
                    </span>
                  )}
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {event.description}
                </p>

                <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                  {event.camera_name && (
                    <div className="flex items-center space-x-1">
                      <Camera className="w-3 h-3" />
                      <span>{event.camera_name}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{format(new Date(event.timestamp), 'PPp')}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Expand Icon */}
            <ChevronDown 
              className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'transform rotate-180' : ''}`}
            />
          </div>
        </button>

        {/* Expanded Details */}
        {isExpanded && event.metadata && (
          <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900/50">
            <div className="space-y-2 text-xs">
              {Object.entries(event.metadata).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                  </span>
                  <span className="text-gray-900 dark:text-white font-mono">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Get event type configuration
 */
function getEventTypeConfig(type: string) {
  const configs = {
    threat: {
      icon: <Shield className="w-4 h-4 text-red-600 dark:text-red-400" />,
      bgColor: 'bg-red-100 dark:bg-red-900/30',
    },
    alert: {
      icon: <AlertTriangle className="w-4 h-4 text-orange-600 dark:text-orange-400" />,
      bgColor: 'bg-orange-100 dark:bg-orange-900/30',
    },
    system: {
      icon: <Activity className="w-4 h-4 text-blue-600 dark:text-blue-400" />,
      bgColor: 'bg-blue-100 dark:bg-blue-900/30',
    },
    camera: {
      icon: <Camera className="w-4 h-4 text-green-600 dark:text-green-400" />,
      bgColor: 'bg-green-100 dark:bg-green-900/30',
    },
  }

  return configs[type as keyof typeof configs] || configs.system
}

/**
 * Get threat level color
 */
function getThreatLevelColor(level: ThreatLevel): string {
  const colors: Record<ThreatLevel, string> = {
    none: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
    low: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
    medium: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300',
    high: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300',
    critical: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
  }
  return colors[level] || colors.none
}
