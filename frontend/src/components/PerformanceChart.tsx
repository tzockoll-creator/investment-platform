import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { BenchmarkData } from '../types';

interface Props {
  benchmarkData: BenchmarkData;
}

export default function PerformanceChart({ benchmarkData }: Props) {
  const data = [
    {
      name: 'Total Return',
      Portfolio: benchmarkData.portfolio.total_return,
      [benchmarkData.benchmark.ticker]: benchmarkData.benchmark.total_return
    },
    {
      name: 'Annualized Return',
      Portfolio: benchmarkData.portfolio.annualized_return,
      [benchmarkData.benchmark.ticker]: benchmarkData.benchmark.annualized_return
    },
    {
      name: 'Volatility',
      Portfolio: benchmarkData.portfolio.volatility,
      [benchmarkData.benchmark.ticker]: benchmarkData.benchmark.volatility
    }
  ];

  return (
    <>
      <div className="metrics-grid" style={{ marginBottom: '2rem' }}>
        <div className="metric">
          <div className="metric-label">Alpha</div>
          <div className={`metric-value ${benchmarkData.alpha >= 0 ? 'positive' : 'negative'}`}>
            {benchmarkData.alpha.toFixed(2)}%
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Outperformance</div>
          <div className={`metric-value ${benchmarkData.outperformance >= 0 ? 'positive' : 'negative'}`}>
            {benchmarkData.outperformance.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
            <Legend />
            <Bar dataKey="Portfolio" fill="#667eea" />
            <Bar dataKey={benchmarkData.benchmark.ticker} fill="#764ba2" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
