/**
 * CameraCardSkeleton Component
 * Loading placeholder for camera cards
 */

'use client'

export function CameraCardSkeleton() {
  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-lg overflow-hidden border-2 border-gray-200 dark:border-gray-700 animate-pulse">
      {/* Camera Feed Skeleton */}
      <div className="aspect-video bg-gray-300 dark:bg-gray-700 relative">
        {/* Status Indicator Skeleton */}
        <div className="absolute top-2 left-2 w-16 h-6 bg-gray-400 dark:bg-gray-600 rounded-full"></div>
        
        {/* Camera Icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 bg-gray-400 dark:bg-gray-600 rounded-full"></div>
        </div>
      </div>

      {/* Camera Info Skeleton */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <div className="h-5 bg-gray-300 dark:bg-gray-700 rounded w-3/4"></div>
        
        {/* Location */}
        <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-1/2"></div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-2">
          <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded"></div>
        </div>
      </div>
    </div>
  )
}
