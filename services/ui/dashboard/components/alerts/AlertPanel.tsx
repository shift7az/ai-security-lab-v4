/**
 * AlertPanel Component
 * Real-time alert feed with filtering and actions
 */

'use client'

import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, Filter, Bell, BellOff } from 'lucide-react'
import { alertsAPI } from '@/lib/api-client'
import { useWebSocketContext } from '@/hooks/useWebSocket'
import type { Alert, AlertStatus } from '@/types'
import { AlertItem } from './AlertItem'

export function AlertPanel() {
  const [filterStatus, setFilterStatus] = useState<AlertStatus | 'all'>('active')
  const [isPaused, setIsPaused] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const alertListRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // Fetch alerts with filtering
  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ['alerts', filterStatus],
    queryFn: () => alertsAPI.getAlerts(
      filterStatus === 'all' ? undefined : { status: [filterStatus] }
    ),
    refetchInterval: 5000, // Refetch every 5 seconds
    staleTime: 2000,
  })

  // Get real-time alerts from WebSocket
  const { alerts: wsAlerts, latestAlert } = useWebSocketContext()

  // Handle new alerts from WebSocket
  useEffect(() => {
    if (latestAlert) {
      // Invalidate query to refetch alerts
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      
      // Increment unread count if not viewing the list
      if (isPaused) {
        setUnreadCount(prev => prev + 1)
      } else {
        // Auto-scroll to top for new alerts
        if (alertListRef.current) {
          alertListRef.current.scrollTop = 0
        }
      }
    }
  }, [latestAlert, isPaused, queryClient])

  // Acknowledge alert mutation
  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: string) => alertsAPI.acknowledgeAlert(alertId, 'current_user'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  // Resolve alert mutation
  const resolveMutation = useMutation({
    mutationFn: ({ alertId, notes }: { alertId: string; notes: string }) =>
      alertsAPI.resolveAlert(alertId, 'current_user', notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const handleAcknowledge = (alertId: string) => {
    acknowledgeMutation.mutate(alertId)
  }

  const handleResolve = (alertId: string, notes: string = '') => {
    resolveMutation.mutate({ alertId, notes })
  }

  const handleScroll = () => {
    // Pause auto-scroll when user manually scrolls
    if (alertListRef.current) {
      const { scrollTop } = alertListRef.current
      if (scrollTop > 50) {
        setIsPaused(true)
      }
    }
  }

  const resumeAutoScroll = () => {
    setIsPaused(false)
    setUnreadCount(0)
    if (alertListRef.current) {
      alertListRef.current.scrollTop = 0
    }
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
          <AlertTriangle className="w-5 h-5" />
          <span className="text-sm font-medium">Failed to load alerts</span>
        </div>
      </div>
    )
  }

  const displayAlerts = alerts || []
  const activeCount = displayAlerts.filter(a => a.status === 'active').length
  const criticalCount = displayAlerts.filter(a => a.priority === 'critical').length

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Active Alerts
            </h3>
            {activeCount > 0 && (
              <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full text-xs font-semibold">
                {activeCount}
              </span>
            )}
          </div>
          
          {criticalCount > 0 && (
            <div className="flex items-center space-x-1 text-red-600 dark:text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-xs font-semibold">{criticalCount} Critical</span>
            </div>
          )}
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-2">
          <button
            onClick={() => setFilterStatus('active')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'active'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setFilterStatus('acknowledged')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'acknowledged'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Acknowledged
          </button>
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            All
          </button>
        </div>
      </div>

      {/* Unread Notification */}
      {isPaused && unreadCount > 0 && (
        <button
          onClick={resumeAutoScroll}
          className="mx-4 mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
        >
          <Bell className="w-4 h-4" />
          <span className="text-sm font-medium">
            {unreadCount} new alert{unreadCount !== 1 ? 's' : ''} - Click to view
          </span>
        </button>
      )}

      {/* Alert List */}
      <div
        ref={alertListRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 space-y-3"
      >
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : displayAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-gray-500 dark:text-gray-400">
            <BellOff className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm">No alerts</p>
          </div>
        ) : (
          displayAlerts.map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onAcknowledge={handleAcknowledge}
              onResolve={handleResolve}
              isAcknowledging={acknowledgeMutation.isPending}
              isResolving={resolveMutation.isPending}
            />
          ))
        )}
      </div>

      {/* Footer Stats */}
      {displayAlerts.length > 0 && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>{displayAlerts.length} total alerts</span>
            <span>Last updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      )}
    </div>
  )
}
