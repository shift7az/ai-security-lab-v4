'use client';

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
  TooltipProps,
} from 'recharts';

interface AlertDistribution {
  type: string;
  count: number;
  percentage: number;
}

interface AlertDistributionChartProps {
  data: AlertDistribution[];
  className?: string;
}

const COLORS = {
  'weapon_detected': '#EF4444',
  'suspicious_behavior': '#F59E0B',
  'unauthorized_access': '#3B82F6',
  'loitering': '#8B5CF6',
  'crowd_detection': '#10B981',
  'vehicle_alert': '#6366F1',
  'other': '#6B7280',
};

const LABELS = {
  'weapon_detected': 'Weapon Detected',
  'suspicious_behavior': 'Suspicious Behavior',
  'unauthorized_access': 'Unauthorized Access',
  'loitering': 'Loitering',
  'crowd_detection': 'Crowd Detection',
  'vehicle_alert': 'Vehicle Alert',
  'other': 'Other',
};

export function AlertDistributionChart({ data, className = '' }: AlertDistributionChartProps) {
  // Format data for pie chart
  const chartData = data.map(item => ({
    name: LABELS[item.type as keyof typeof LABELS] || item.type,
    value: item.count,
    percentage: item.percentage,
    type: item.type,
  }));

  // Custom label for pie slices
  const renderCustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }: any) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * (Math.PI / 180));
    const y = cy + radius * Math.sin(-midAngle * (Math.PI / 180));

    if (percent < 0.05) return null; // Don't show label for small slices

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-xs font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;

    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
        <p className="text-sm font-semibold text-white mb-1">{data.name}</p>
        <div className="text-xs text-gray-300">
          <div>Count: <span className="font-semibold">{data.value}</span></div>
          <div>Percentage: <span className="font-semibold">{data.percentage.toFixed(1)}%</span></div>
        </div>
      </div>
    );
  };

  // Custom legend
  const renderLegend = (props: any) => {
    const { payload } = props;

    return (
      <div className="flex flex-wrap gap-3 justify-center mt-4">
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            ></div>
            <span className="text-xs text-gray-300">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  };

  const totalAlerts = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className={`bg-gray-800 rounded-lg p-6 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">Alert Distribution</h3>
        <p className="text-sm text-gray-400">
          Breakdown of alert types
        </p>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={COLORS[entry.type as keyof typeof COLORS] || COLORS.other}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={renderLegend} />
        </PieChart>
      </ResponsiveContainer>

      {/* Stats */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-400">Total Alerts</div>
            <div className="text-2xl font-bold text-white">{totalAlerts}</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-400">Alert Types</div>
            <div className="text-2xl font-bold text-blue-500">{chartData.length}</div>
          </div>
        </div>
      </div>

      {/* Top Alert Type */}
      {chartData.length > 0 && (
        <div className="mt-4 p-3 bg-gray-900 rounded-lg">
          <div className="text-xs text-gray-400 mb-1">Most Common Alert</div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-white">
              {chartData[0].name}
            </span>
            <span className="text-sm font-bold" style={{ 
              color: COLORS[chartData[0].type as keyof typeof COLORS] || COLORS.other 
            }}>
              {chartData[0].value} ({chartData[0].percentage.toFixed(1)}%)
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
