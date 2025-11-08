/**
 * AlertItem Component
 * Individual alert card with details and actions
 */

'use client'

import { useState } from 'react'
import { 
  AlertTriangle, 
  Shield, 
  Camera, 
  Clock, 
  Check, 
  X,
  ChevronDown,
  ChevronUp,
  MapPin
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import type { Alert } from '@/types'

interface AlertItemProps {
  alert: Alert
  onAcknowledge: (alertId: string) => void
  onResolve: (alertId: string, notes: string) => void
  isAcknowledging: boolean
  isResolving: boolean
}

export function AlertItem({ 
  alert, 
  onAcknowledge, 
  onResolve, 
  isAcknowledging, 
  isResolving 
}: AlertItemProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [resolveNotes, setResolveNotes] = useState('')
  const [showResolveInput, setShowResolveInput] = useState(false)

  const priorityColors = {
    critical: 'border-l-4 border-l-red-500 bg-red-50 dark:bg-red-900/10',
    high: 'border-l-4 border-l-orange-500 bg-orange-50 dark:bg-orange-900/10',
    medium: 'border-l-4 border-l-yellow-500 bg-yellow-50 dark:bg-yellow-900/10',
    low: 'border-l-4 border-l-green-500 bg-green-50 dark:bg-green-900/10',
  }

  const priorityBadgeColors = {
    critical: 'bg-red-600 text-white',
    high: 'bg-orange-600 text-white',
    medium: 'bg-yellow-600 text-white',
    low: 'bg-green-600 text-white',
  }

  const statusBadgeColors = {
    active: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
    acknowledged: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300',
    resolved: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
  }

  const handleResolveSubmit = () => {
    onResolve(alert.id, resolveNotes)
    setShowResolveInput(false)
    setResolveNotes('')
  }

  const timeAgo = formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })

  return (
    <div className={`rounded-lg border border-gray-200 dark:border-gray-700 ${priorityColors[alert.priority]} transition-all duration-200`}>
      {/* Main Alert Content */}
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-start space-x-3 flex-1">
            {/* Priority Icon */}
            <div className={`p-2 rounded-lg ${priorityBadgeColors[alert.priority]}`}>
              {alert.priority === 'critical' || alert.priority === 'high' ? (
                <AlertTriangle className="w-4 h-4" />
              ) : (
                <Shield className="w-4 h-4" />
              )}
            </div>

            {/* Alert Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                  {alert.message}
                </h4>
                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${statusBadgeColors[alert.status]}`}>
                  {alert.status}
                </span>
              </div>

              {alert.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {alert.description}
                </p>
              )}

              {/* Meta Information */}
              <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                {alert.camera_name && (
                  <div className="flex items-center space-x-1">
                    <Camera className="w-3 h-3" />
                    <span>{alert.camera_name}</span>
                  </div>
                )}
                <div className="flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{timeAgo}</span>
                </div>
                {alert.threat_score && (
                  <div className="flex items-center space-x-1">
                    <Shield className="w-3 h-3" />
                    <span>Score: {(alert.threat_score * 100).toFixed(0)}%</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Expand Button */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          >
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </button>
        </div>

        {/* Action Buttons */}
        {alert.status === 'active' && !showResolveInput && (
          <div className="flex space-x-2 mt-3">
            <button
              onClick={() => onAcknowledge(alert.id)}
              disabled={isAcknowledging}
              className="flex-1 px-3 py-1.5 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center justify-center space-x-1"
            >
              <Check className="w-4 h-4" />
              <span>{isAcknowledging ? 'Acknowledging...' : 'Acknowledge'}</span>
            </button>
            <button
              onClick={() => setShowResolveInput(true)}
              className="flex-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium flex items-center justify-center space-x-1"
            >
              <X className="w-4 h-4" />
              <span>Resolve</span>
            </button>
          </div>
        )}

        {/* Resolve Input */}
        {showResolveInput && (
          <div className="mt-3 space-y-2">
            <textarea
              value={resolveNotes}
              onChange={(e) => setResolveNotes(e.target.value)}
              placeholder="Add resolution notes (optional)..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
            />
            <div className="flex space-x-2">
              <button
                onClick={handleResolveSubmit}
                disabled={isResolving}
                className="flex-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
              >
                {isResolving ? 'Resolving...' : 'Confirm Resolve'}
              </button>
              <button
                onClick={() => {
                  setShowResolveInput(false)
                  setResolveNotes('')
                }}
                className="px-3 py-1.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Expanded Details */}
        {isExpanded && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
            {/* Timestamp */}
            <div className="text-xs">
              <span className="text-gray-500 dark:text-gray-400">Detected:</span>
              <span className="ml-2 text-gray-700 dark:text-gray-300">
                {format(new Date(alert.timestamp), 'PPpp')}
              </span>
            </div>

            {/* Detection ID */}
            {alert.detection_id && (
              <div className="text-xs">
                <span className="text-gray-500 dark:text-gray-400">Detection ID:</span>
                <span className="ml-2 text-gray-700 dark:text-gray-300 font-mono">
                  {alert.detection_id}
                </span>
              </div>
            )}

            {/* Acknowledged Info */}
            {alert.acknowledged_by && (
              <div className="text-xs">
                <span className="text-gray-500 dark:text-gray-400">Acknowledged by:</span>
                <span className="ml-2 text-gray-700 dark:text-gray-300">
                  {alert.acknowledged_by} at {format(new Date(alert.acknowledged_at!), 'PPpp')}
                </span>
              </div>
            )}

            {/* Resolved Info */}
            {alert.resolved_by && (
              <div className="text-xs">
                <span className="text-gray-500 dark:text-gray-400">Resolved by:</span>
                <span className="ml-2 text-gray-700 dark:text-gray-300">
                  {alert.resolved_by} at {format(new Date(alert.resolved_at!), 'PPpp')}
                </span>
                {alert.resolution_notes && (
                  <div className="mt-1 p-2 bg-gray-100 dark:bg-gray-800 rounded text-gray-700 dark:text-gray-300">
                    {alert.resolution_notes}
                  </div>
                )}
              </div>
            )}

            {/* Actions Taken */}
            {alert.actions_taken && alert.actions_taken.length > 0 && (
              <div className="text-xs">
                <span className="text-gray-500 dark:text-gray-400">Actions taken:</span>
                <ul className="mt-1 space-y-1">
                  {alert.actions_taken.map((action, idx) => (
                    <li key={idx} className="ml-4 text-gray-700 dark:text-gray-300">
                      • {action}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
