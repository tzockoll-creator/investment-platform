import { useState } from 'react';
import { usePortfolioDetail, useAnalytics, useSectorAllocation, useBenchmark } from '../hooks/usePortfolio';
import { portfolioApi } from '../services/api';
import SectorChart from './SectorChart';
import PerformanceChart from './PerformanceChart';
import AnalyticsCards from './AnalyticsCards';

interface Props {
  portfolioId: number;
  onUpdate: () => void;
}

export default function PortfolioDashboard({ portfolioId, onUpdate }: Props) {
  const { portfolio, loading, error, refetch } = usePortfolioDetail(portfolioId);
  const { analytics } = useAnalytics(portfolioId);
  const { sectors } = useSectorAllocation(portfolioId);
  const { benchmarkData } = useBenchmark(portfolioId);

  const [showAddHolding, setShowAddHolding] = useState(false);
  const [newHolding, setNewHolding] = useState({
    ticker: '',
    shares: '',
    avg_cost: ''
  });

  const handleAddHolding = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await portfolioApi.addHolding(portfolioId, {
        ticker: newHolding.ticker.toUpperCase(),
        shares: parseFloat(newHolding.shares),
        avg_cost: parseFloat(newHolding.avg_cost)
      });
      setNewHolding({ ticker: '', shares: '', avg_cost: '' });
      setShowAddHolding(false);
      refetch();
      onUpdate();
    } catch (err) {
      console.error('Failed to add holding:', err);
    }
  };

  const handleDeleteHolding = async (holdingId: number) => {
    if (!confirm('Are you sure you want to delete this holding?')) return;
    try {
      await portfolioApi.deleteHolding(holdingId);
      refetch();
      onUpdate();
    } catch (err) {
      console.error('Failed to delete holding:', err);
    }
  };

  // Auto-refresh every 30 seconds
  useState(() => {
    const interval = setInterval(() => {
      refetch();
    }, 30000);
    return () => clearInterval(interval);
  });

  if (loading && !portfolio) {
    return <div className="loading">Loading portfolio...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!portfolio) {
    return null;
  }

  return (
    <div className="dashboard">
      {/* Summary Cards */}
      <div className="summary-grid">
        <div className="summary-card">
          <h4>Total Value</h4>
          <p>${portfolio.total_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
        <div className="summary-card">
          <h4>Total Cost</h4>
          <p>${portfolio.total_cost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
        <div className={`summary-card ${portfolio.total_gain_loss >= 0 ? 'positive' : 'negative'}`}>
          <h4>Total Gain/Loss</h4>
          <p>${portfolio.total_gain_loss.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({portfolio.total_gain_loss_pct.toFixed(2)}%)</p>
        </div>
      </div>

      {/* Analytics Cards */}
      {analytics && <AnalyticsCards analytics={analytics} />}

      {/* Holdings Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Holdings</h3>
          <button className="btn btn-primary" onClick={() => setShowAddHolding(!showAddHolding)}>
            {showAddHolding ? 'Cancel' : 'Add Holding'}
          </button>
        </div>

        {showAddHolding && (
          <form className="add-holding-form" onSubmit={handleAddHolding}>
            <div className="form-row">
              <div className="form-group">
                <label>Ticker</label>
                <input
                  type="text"
                  value={newHolding.ticker}
                  onChange={(e) => setNewHolding({ ...newHolding, ticker: e.target.value })}
                  placeholder="AAPL"
                  required
                />
              </div>
              <div className="form-group">
                <label>Shares</label>
                <input
                  type="number"
                  step="0.01"
                  value={newHolding.shares}
                  onChange={(e) => setNewHolding({ ...newHolding, shares: e.target.value })}
                  placeholder="100"
                  required
                />
              </div>
              <div className="form-group">
                <label>Avg Cost</label>
                <input
                  type="number"
                  step="0.01"
                  value={newHolding.avg_cost}
                  onChange={(e) => setNewHolding({ ...newHolding, avg_cost: e.target.value })}
                  placeholder="150.00"
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary">Add</button>
          </form>
        )}

        <table className="holdings-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Shares</th>
              <th>Avg Cost</th>
              <th>Current Price</th>
              <th>Current Value</th>
              <th>Gain/Loss</th>
              <th>Gain/Loss %</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {portfolio.holdings.map((holding) => (
              <tr key={holding.id}>
                <td><strong>{holding.ticker}</strong></td>
                <td>{holding.shares.toFixed(2)}</td>
                <td>${holding.avg_cost.toFixed(2)}</td>
                <td>${holding.current_price.toFixed(2)}</td>
                <td>${holding.current_value.toFixed(2)}</td>
                <td className={holding.gain_loss >= 0 ? 'positive' : 'negative'}>
                  ${holding.gain_loss.toFixed(2)}
                </td>
                <td className={holding.gain_loss_pct >= 0 ? 'positive' : 'negative'}>
                  {holding.gain_loss_pct.toFixed(2)}%
                </td>
                <td>
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleDeleteHolding(holding.id)}
                    style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Sector Allocation */}
      {sectors && Object.keys(sectors).length > 0 && (
        <div className="card">
          <h3>Sector Allocation</h3>
          <SectorChart sectors={sectors} />
        </div>
      )}

      {/* Performance vs Benchmark */}
      {benchmarkData && (
        <div className="card">
          <h3>Performance vs {benchmarkData.benchmark.ticker}</h3>
          <PerformanceChart benchmarkData={benchmarkData} />
        </div>
      )}
    </div>
  );
}
