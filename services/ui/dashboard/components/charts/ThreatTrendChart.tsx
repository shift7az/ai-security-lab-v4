'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts';
import { format } from 'date-fns';

interface ThreatDataPoint {
  timestamp: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
}

interface ThreatTrendChartProps {
  data: ThreatDataPoint[];
  timeRange?: '1h' | '6h' | '24h' | '7d' | '30d';
  className?: string;
}

export function ThreatTrendChart({ 
  data, 
  timeRange = '24h',
  className = '' 
}: ThreatTrendChartProps) {
  
  // Format data for display
  const formattedData = useMemo(() => {
    return data.map(point => ({
      ...point,
      time: format(new Date(point.timestamp), 
        timeRange === '1h' || timeRange === '6h' ? 'HH:mm' : 
        timeRange === '24h' ? 'HH:mm' :
        'MMM dd'
      ),
    }));
  }, [data, timeRange]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
        <p className="text-sm font-semibold text-gray-200 mb-2">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center justify-between gap-4 text-xs">
            <span style={{ color: entry.color }} className="font-medium">
              {entry.name}:
            </span>
            <span className="text-gray-300 font-semibold">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">Threat Trends</h3>
        <p className="text-sm text-gray-400">
          Detection patterns over time
        </p>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
          <Line 
            type="monotone" 
            dataKey="critical" 
            stroke="#EF4444" 
            strokeWidth={2}
            name="Critical"
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line 
            type="monotone" 
            dataKey="high" 
            stroke="#F59E0B" 
            strokeWidth={2}
            name="High"
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line 
            type="monotone" 
            dataKey="medium" 
            stroke="#3B82F6" 
            strokeWidth={2}
            name="Medium"
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line 
            type="monotone" 
            dataKey="low" 
            stroke="#10B981" 
            strokeWidth={2}
            name="Low"
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Stats Summary */}
      <div className="mt-4 grid grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-xs text-gray-400">Critical</div>
          <div className="text-lg font-bold text-red-500">
            {formattedData.reduce((sum, d) => sum + d.critical, 0)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400">High</div>
          <div className="text-lg font-bold text-orange-500">
            {formattedData.reduce((sum, d) => sum + d.high, 0)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400">Medium</div>
          <div className="text-lg font-bold text-blue-500">
            {formattedData.reduce((sum, d) => sum + d.medium, 0)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400">Low</div>
          <div className="text-lg font-bold text-green-500">
            {formattedData.reduce((sum, d) => sum + d.low, 0)}
          </div>
        </div>
      </div>
    </div>
  );
}
