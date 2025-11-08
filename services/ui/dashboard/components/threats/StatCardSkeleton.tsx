/**
 * StatCardSkeleton Component
 * Loading placeholder for statistics cards
 */

'use client'

export function StatCardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 animate-pulse">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        {/* Icon placeholder */}
        <div className="p-3 rounded-lg bg-gray-200 dark:bg-gray-700">
          <div className="w-6 h-6 bg-gray-300 dark:bg-gray-600 rounded"></div>
        </div>
        
        {/* Trend placeholder */}
        <div className="flex items-center space-x-1">
          <div className="w-4 h-4 bg-gray-200 dark:bg-gray-600 rounded"></div>
          <div className="w-10 h-4 bg-gray-200 dark:bg-gray-600 rounded"></div>
        </div>
      </div>

      {/* Title placeholder */}
      <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-2/3 mb-2"></div>

      {/* Value placeholder */}
      <div className="h-8 bg-gray-300 dark:bg-gray-700 rounded w-1/2 mb-2"></div>

      {/* Subtitle placeholder */}
      <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-3/4 mb-4"></div>

      {/* Progress bar placeholder */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2"></div>
    </div>
  )
}
