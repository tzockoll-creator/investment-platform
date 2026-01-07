import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { SectorAllocation } from '../types';

interface Props {
  sectors: SectorAllocation;
}

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140'];

export default function SectorChart({ sectors }: Props) {
  const data = Object.entries(sectors).map(([sector, { value, percentage }]) => ({
    name: sector,
    value: percentage,
    amount: value
  }));

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number, name: string, props: any) => [
            `${value.toFixed(2)}% ($${props.payload.amount.toLocaleString()})`,
            name
          ]} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
