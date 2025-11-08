'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts';
import { format } from 'date-fns';

interface SystemMetric {
  timestamp: string;
  cpu: number;
  memory: number;
  gpu: number;
  disk: number;
}

interface SystemMetricsChartProps {
  data: SystemMetric[];
  className?: string;
}

export function SystemMetricsChart({ data, className = '' }: SystemMetricsChartProps) {
  // Format data for display
  const formattedData = data.map(point => ({
    ...point,
    time: format(new Date(point.timestamp), 'HH:mm'),
  }));

  // Get metric status color
  const getStatusColor = (value: number): string => {
    if (value >= 90) return 'text-red-500';
    if (value >= 75) return 'text-orange-500';
    if (value >= 50) return 'text-yellow-500';
    return 'text-green-500';
  };

  // Get metric status text
  const getStatusText = (value: number): string => {
    if (value >= 90) return 'Critical';
    if (value >= 75) return 'High';
    if (value >= 50) return 'Moderate';
    return 'Normal';
  };

  // Calculate averages
  const avgCpu = (data.reduce((sum, d) => sum + d.cpu, 0) / data.length).toFixed(1);
  const avgMemory = (data.reduce((sum, d) => sum + d.memory, 0) / data.length).toFixed(1);
  const avgGpu = (data.reduce((sum, d) => sum + d.gpu, 0) / data.length).toFixed(1);
  const avgDisk = (data.reduce((sum, d) => sum + d.disk, 0) / data.length).toFixed(1);

  // Get current values (last data point)
  const current = data[data.length - 1] || { cpu: 0, memory: 0, gpu: 0, disk: 0 };

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
            <span className="text-gray-300 font-semibold">{entry.value}%</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">System Metrics</h3>
        <p className="text-sm text-gray-400">
          Resource utilization over time
        </p>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={formattedData}>
          <defs>
            <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorGpu" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorDisk" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="cpu"
            stroke="#3B82F6"
            fillOpacity={1}
            fill="url(#colorCpu)"
            name="CPU"
          />
          <Area
            type="monotone"
            dataKey="memory"
            stroke="#10B981"
            fillOpacity={1}
            fill="url(#colorMemory)"
            name="Memory"
          />
          <Area
            type="monotone"
            dataKey="gpu"
            stroke="#F59E0B"
            fillOpacity={1}
            fill="url(#colorGpu)"
            name="GPU"
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Current Metrics Grid */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* CPU */}
        <div className="bg-gray-900 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">CPU</span>
            <span className={`text-xs font-semibold ${getStatusColor(current.cpu)}`}>
              {getStatusText(current.cpu)}
            </span>
          </div>
          <div className="text-2xl font-bold text-blue-500">{current.cpu.toFixed(1)}%</div>
          <div className="text-xs text-gray-400 mt-1">Avg: {avgCpu}%</div>
        </div>

        {/* Memory */}
        <div className="bg-gray-900 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Memory</span>
            <span className={`text-xs font-semibold ${getStatusColor(current.memory)}`}>
              {getStatusText(current.memory)}
            </span>
          </div>
          <div className="text-2xl font-bold text-green-500">{current.memory.toFixed(1)}%</div>
          <div className="text-xs text-gray-400 mt-1">Avg: {avgMemory}%</div>
        </div>

        {/* GPU */}
        <div className="bg-gray-900 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">GPU</span>
            <span className={`text-xs font-semibold ${getStatusColor(current.gpu)}`}>
              {getStatusText(current.gpu)}
            </span>
          </div>
          <div className="text-2xl font-bold text-orange-500">{current.gpu.toFixed(1)}%</div>
          <div className="text-xs text-gray-400 mt-1">Avg: {avgGpu}%</div>
        </div>

        {/* Disk */}
        <div className="bg-gray-900 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Disk</span>
            <span className={`text-xs font-semibold ${getStatusColor(current.disk)}`}>
              {getStatusText(current.disk)}
            </span>
          </div>
          <div className="text-2xl font-bold text-purple-500">{current.disk.toFixed(1)}%</div>
          <div className="text-xs text-gray-400 mt-1">Avg: {avgDisk}%</div>
        </div>
      </div>

      {/* Health Status */}
      <div className="mt-4 p-3 bg-gray-900 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Overall System Health</span>
          <div className="flex items-center gap-2">
            {Math.max(current.cpu, current.memory, current.gpu, current.disk) < 75 ? (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-semibold text-green-500">Healthy</span>
              </>
            ) : Math.max(current.cpu, current.memory, current.gpu, current.disk) < 90 ? (
              <>
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-semibold text-yellow-500">Warning</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-semibold text-red-500">Critical</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
