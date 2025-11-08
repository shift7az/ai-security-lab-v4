'use client';

import { useMemo } from 'react';

interface CameraActivity {
  camera_id: string;
  camera_name: string;
  detections: number;
  threats: number;
  avg_threat_score: number;
}

interface CameraHeatmapProps {
  data: CameraActivity[];
  className?: string;
}

export function CameraHeatmap({ data, className = '' }: CameraHeatmapProps) {
  // Calculate max values for normalization
  const maxDetections = useMemo(() => 
    Math.max(...data.map(c => c.detections), 1),
    [data]
  );

  const maxThreats = useMemo(() => 
    Math.max(...data.map(c => c.threats), 1),
    [data]
  );

  // Get heat intensity (0-1 scale)
  const getHeatIntensity = (value: number, max: number): number => {
    return Math.min(value / max, 1);
  };

  // Get color based on intensity
  const getHeatColor = (intensity: number): string => {
    if (intensity >= 0.8) return 'bg-red-600';
    if (intensity >= 0.6) return 'bg-orange-500';
    if (intensity >= 0.4) return 'bg-yellow-500';
    if (intensity >= 0.2) return 'bg-blue-500';
    return 'bg-green-500';
  };

  // Get threat level color
  const getThreatLevelColor = (score: number): string => {
    if (score >= 0.8) return 'text-red-500';
    if (score >= 0.6) return 'text-orange-500';
    if (score >= 0.4) return 'text-yellow-500';
    return 'text-green-500';
  };

  // Sort cameras by threat count
  const sortedData = useMemo(() => 
    [...data].sort((a, b) => b.threats - a.threats),
    [data]
  );

  return (
    <div className={`bg-gray-800 rounded-lg p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">Camera Activity Heatmap</h3>
        <p className="text-sm text-gray-400">
          Detection and threat distribution by camera
        </p>
      </div>

      {/* Legend */}
      <div className="mb-4 flex items-center gap-4 text-xs">
        <span className="text-gray-400">Intensity:</span>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-gray-400">Low</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-yellow-500 rounded"></div>
          <span className="text-gray-400">Medium</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-orange-500 rounded"></div>
          <span className="text-gray-400">High</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-red-600 rounded"></div>
          <span className="text-gray-400">Critical</span>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="space-y-2">
        {sortedData.map((camera) => {
          const detectionIntensity = getHeatIntensity(camera.detections, maxDetections);
          const threatIntensity = getHeatIntensity(camera.threats, maxThreats);
          
          return (
            <div 
              key={camera.camera_id}
              className="bg-gray-900 rounded-lg p-3 hover:bg-gray-750 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium text-white">
                    {camera.camera_name}
                  </span>
                </div>
                <span className={`text-xs font-semibold ${getThreatLevelColor(camera.avg_threat_score)}`}>
                  Score: {(camera.avg_threat_score * 100).toFixed(0)}%
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {/* Detections Bar */}
                <div>
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Detections</span>
                    <span className="font-semibold">{camera.detections}</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${getHeatColor(detectionIntensity)} transition-all duration-300`}
                      style={{ width: `${detectionIntensity * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Threats Bar */}
                <div>
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Threats</span>
                    <span className="font-semibold">{camera.threats}</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${getHeatColor(threatIntensity)} transition-all duration-300`}
                      style={{ width: `${threatIntensity * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xs text-gray-400">Total Cameras</div>
            <div className="text-lg font-bold text-white">{data.length}</div>
          </div>
          <div>
            <div className="text-xs text-gray-400">Total Detections</div>
            <div className="text-lg font-bold text-blue-500">
              {data.reduce((sum, c) => sum + c.detections, 0)}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-400">Total Threats</div>
            <div className="text-lg font-bold text-red-500">
              {data.reduce((sum, c) => sum + c.threats, 0)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
