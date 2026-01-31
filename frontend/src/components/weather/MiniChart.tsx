import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
} from "recharts";

interface SparklineProps {
  data: { value: number }[];
  color?: string;
}

export function Sparkline({ data, color = "#f0a020" }: SparklineProps) {
  if (!data || data.length === 0) return null;
  return (
    <div className="mini-chart">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`grad-${color}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={1.5}
            fill={`url(#grad-${color})`}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

function kpColor(value: number): string {
  if (value < 4) return "var(--kp-low)";
  if (value < 6) return "var(--kp-moderate)";
  if (value < 8) return "var(--kp-high)";
  return "var(--kp-severe)";
}

interface KpBarChartProps {
  data: { value: number }[];
}

export function KpBarChart({ data }: KpBarChartProps) {
  if (!data || data.length === 0) return null;
  return (
    <div className="mini-chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <Bar dataKey="value" isAnimationActive={false}>
            {data.map((entry, i) => (
              <Cell key={i} fill={kpColor(entry.value)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
