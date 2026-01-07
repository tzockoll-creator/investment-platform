import { useState, useEffect } from 'react';
import { portfolioApi } from '../services/api';
import type { Portfolio, PortfolioDetail, Analytics, SectorAllocation, BenchmarkData } from '../types';

export const usePortfolios = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      const data = await portfolioApi.getAll();
      setPortfolios(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch portfolios');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolios();
  }, []);

  return { portfolios, loading, error, refetch: fetchPortfolios };
};

export const usePortfolioDetail = (portfolioId: number | null) => {
  const [portfolio, setPortfolio] = useState<PortfolioDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolio = async () => {
    if (!portfolioId) return;

    try {
      setLoading(true);
      const data = await portfolioApi.getById(portfolioId);
      setPortfolio(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch portfolio details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, [portfolioId]);

  return { portfolio, loading, error, refetch: fetchPortfolio };
};

export const useAnalytics = (portfolioId: number | null) => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId) return;

    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const data = await portfolioApi.getAnalytics(portfolioId);
        setAnalytics(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch analytics');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [portfolioId]);

  return { analytics, loading, error };
};

export const useSectorAllocation = (portfolioId: number | null) => {
  const [sectors, setSectors] = useState<SectorAllocation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId) return;

    const fetchSectors = async () => {
      try {
        setLoading(true);
        const data = await portfolioApi.getSectorAllocation(portfolioId);
        setSectors(data.sectors);
        setError(null);
      } catch (err) {
        setError('Failed to fetch sector allocation');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSectors();
  }, [portfolioId]);

  return { sectors, loading, error };
};

export const useBenchmark = (portfolioId: number | null, benchmark: string = 'SPY') => {
  const [benchmarkData, setBenchmarkData] = useState<BenchmarkData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId) return;

    const fetchBenchmark = async () => {
      try {
        setLoading(true);
        const data = await portfolioApi.getBenchmark(portfolioId, benchmark);
        setBenchmarkData(data.benchmark_data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch benchmark data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBenchmark();
  }, [portfolioId, benchmark]);

  return { benchmarkData, loading, error };
};
