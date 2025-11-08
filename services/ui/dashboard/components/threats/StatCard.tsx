/**
 * StatCard Component
 * Reusable statistics card with icon, value, trend, and color theming
 */

'use client'

import { ReactNode } from 'react'
import type { TrendData } from '@/types'
import { getTrendIcon, getTrendColor } from './ThreatOverview'

interface StatCardProps {
  title: string
  value: number
  icon: ReactNode
  color: 'red' | 'orange' | 'yellow' | 'green' | 'blue' | 'purple'
  subtitle?: string
  trend?: TrendData
  total?: number
  percentage?: number
  isPercentage?: boolean
  onClick?: () => void
}

export function StatCard({
  title,
  value,
  icon,
  color,
  subtitle,
  trend,
  total,
  percentage,
  isPercentage = false,
  onClick,
}: StatCardProps) {
  const colorClasses = getColorClasses(color)
  
  return (
    <div
      className={`
        bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700
        transition-all duration-200
        ${onClick ? 'cursor-pointer hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600' : ''}
      `}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses.bg}`}>
          <div className={colorClasses.icon}>
            {icon}
          </div>
        </div>
        
        {trend && (
          <div className={`flex items-center space-x-1 ${getTrendColor(trend.direction, color === 'green')}`}>
            {getTrendIcon(trend.direction)}
            <span className="text-sm font-semibold">
              {Math.abs(trend.change_percentage).toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {/* Title */}
      <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
        {title}
      </h3>

      {/* Value */}
      <div className="flex items-baseline space-x-2">
        <span className="text-3xl font-bold text-gray-900 dark:text-white">
          {isPercentage ? `${value}%` : value.toLocaleString()}
        </span>
        {total !== undefined && (
          <span className="text-lg text-gray-500 dark:text-gray-400">
            / {total}
          </span>
        )}
      </div>

      {/* Subtitle */}
      {subtitle && (
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {subtitle}
        </p>
      )}

      {/* Progress Bar (if percentage provided) */}
      {percentage !== undefined && !isPercentage && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${colorClasses.progress}`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Trend Details */}
      {trend && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>vs previous period</span>
            <span className="font-medium">
              {trend.previous.toLocaleString()} → {trend.current.toLocaleString()}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Get color classes based on color prop
 */
function getColorClasses(color: string) {
  const classes = {
    red: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      icon: 'text-red-600 dark:text-red-400',
      progress: 'bg-red-500',
    },
    orange: {
      bg: 'bg-orange-100 dark:bg-orange-900/30',
      icon: 'text-orange-600 dark:text-orange-400',
      progress: 'bg-orange-500',
    },
    yellow: {
      bg: 'bg-yellow-100 dark:bg-yellow-900/30',
      icon: 'text-yellow-600 dark:text-yellow-400',
      progress: 'bg-yellow-500',
    },
    green: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      icon: 'text-green-600 dark:text-green-400',
      progress: 'bg-green-500',
    },
    blue: {
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      icon: 'text-blue-600 dark:text-blue-400',
      progress: 'bg-blue-500',
    },
    purple: {
      bg: 'bg-purple-100 dark:bg-purple-900/30',
      icon: 'text-purple-600 dark:text-purple-400',
      progress: 'bg-purple-500',
    },
  }

  return classes[color as keyof typeof classes] || classes.blue
}
