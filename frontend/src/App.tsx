import { useState } from 'react';
import { usePortfolios } from './hooks/usePortfolio';
import { portfolioApi } from './services/api';
import PortfolioDashboard from './components/PortfolioDashboard';
import './App.css';

export default function App() {
  const { portfolios, loading, error, refetch } = usePortfolios();
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPortfolio, setNewPortfolio] = useState({ name: '', description: '' });

  const handleCreatePortfolio = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await portfolioApi.create(newPortfolio);
      setNewPortfolio({ name: '', description: '' });
      setShowCreateForm(false);
      refetch();
    } catch (err) {
      console.error('Failed to create portfolio:', err);
    }
  };

  const handleDeletePortfolio = async (portfolioId: number) => {
    if (!confirm('Are you sure you want to delete this portfolio?')) return;
    try {
      await portfolioApi.delete(portfolioId);
      if (selectedPortfolioId === portfolioId) {
        setSelectedPortfolioId(null);
      }
      refetch();
    } catch (err) {
      console.error('Failed to delete portfolio:', err);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Investment Platform</h1>
        <p>Professional Portfolio Management & Analytics</p>
      </header>

      <div className="container">
        <div className="portfolio-selector">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2>Portfolios</h2>
            <button className="btn btn-primary" onClick={() => setShowCreateForm(!showCreateForm)}>
              {showCreateForm ? 'Cancel' : 'Create Portfolio'}
            </button>
          </div>

          {showCreateForm && (
            <form className="create-form" onSubmit={handleCreatePortfolio}>
              <input
                type="text"
                placeholder="Portfolio Name"
                value={newPortfolio.name}
                onChange={(e) => setNewPortfolio({ ...newPortfolio, name: e.target.value })}
                required
              />
              <input
                type="text"
                placeholder="Description (optional)"
                value={newPortfolio.description}
                onChange={(e) => setNewPortfolio({ ...newPortfolio, description: e.target.value })}
              />
              <button type="submit" className="btn btn-primary">Create</button>
            </form>
          )}

          {loading && <div className="loading">Loading portfolios...</div>}
          {error && <div className="error">{error}</div>}

          {!loading && portfolios.length === 0 && (
            <p style={{ color: '#718096', marginTop: '1rem' }}>
              No portfolios yet. Create your first portfolio to get started!
            </p>
          )}

          {portfolios.length > 0 && (
            <div className="portfolio-buttons">
              {portfolios.map((portfolio) => (
                <div key={portfolio.id} style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className={`btn btn-secondary ${selectedPortfolioId === portfolio.id ? 'active' : ''}`}
                    onClick={() => setSelectedPortfolioId(portfolio.id)}
                  >
                    {portfolio.name}
                  </button>
                  <button
                    className="btn"
                    onClick={() => handleDeletePortfolio(portfolio.id)}
                    style={{
                      background: '#ef4444',
                      color: 'white',
                      padding: '0.75rem 1rem'
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedPortfolioId && (
          <PortfolioDashboard
            portfolioId={selectedPortfolioId}
            onUpdate={refetch}
          />
        )}

        {!selectedPortfolioId && portfolios.length > 0 && (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <h3 style={{ color: '#718096' }}>Select a portfolio to view details</h3>
          </div>
        )}
      </div>
    </div>
  );
}
