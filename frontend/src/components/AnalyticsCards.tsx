import type { Analytics } from '../types';

interface Props {
  analytics: Analytics;
}

export default function AnalyticsCards({ analytics }: Props) {
  return (
    <div className="card">
      <h3>Portfolio Analytics</h3>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Sharpe Ratio</div>
          <div className="metric-value">
            {analytics.sharpe_ratio !== null ? analytics.sharpe_ratio.toFixed(2) : 'N/A'}
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Volatility</div>
          <div className="metric-value">{analytics.volatility.toFixed(2)}%</div>
        </div>
        <div className="metric">
          <div className="metric-label">Beta</div>
          <div className="metric-value">
            {analytics.beta !== null ? analytics.beta.toFixed(2) : 'N/A'}
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Max Drawdown</div>
          <div className="metric-value">{analytics.max_drawdown.toFixed(2)}%</div>
        </div>
        <div className="metric">
          <div className="metric-label">Avg Return</div>
          <div className="metric-value">{analytics.average_return.toFixed(4)}%</div>
        </div>
      </div>
    </div>
  );
}
