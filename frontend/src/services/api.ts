import axios from 'axios';
import type {
  Portfolio,
  PortfolioDetail,
  Analytics,
  SectorAllocation,
  BenchmarkData,
  TechnicalIndicators,
  StockQuote
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const portfolioApi = {
  // Portfolio CRUD
  getAll: async (): Promise<Portfolio[]> => {
    const response = await api.get('/portfolios');
    return response.data;
  },

  getById: async (id: number): Promise<PortfolioDetail> => {
    const response = await api.get(`/portfolios/${id}`);
    return response.data;
  },

  create: async (data: { name: string; description?: string }): Promise<Portfolio> => {
    const response = await api.post('/portfolios', data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/portfolios/${id}`);
  },

  // Holdings
  addHolding: async (portfolioId: number, data: { ticker: string; shares: number; avg_cost: number }) => {
    const response = await api.post(`/portfolios/${portfolioId}/holdings`, data);
    return response.data;
  },

  deleteHolding: async (holdingId: number): Promise<void> => {
    await api.delete(`/holdings/${holdingId}`);
  },

  // Analytics - Phase 1
  getAnalytics: async (portfolioId: number): Promise<Analytics> => {
    const response = await api.get(`/portfolios/${portfolioId}/analytics`);
    return response.data;
  },

  // Phase 2 - Data Analysis
  getSectorAllocation: async (portfolioId: number): Promise<{ portfolio_id: number; sectors: SectorAllocation }> => {
    const response = await api.get(`/portfolios/${portfolioId}/sectors`);
    return response.data;
  },

  getBenchmark: async (portfolioId: number, benchmark: string = 'SPY'): Promise<{ portfolio_id: number; benchmark_data: BenchmarkData }> => {
    const response = await api.get(`/portfolios/${portfolioId}/benchmark`, {
      params: { benchmark }
    });
    return response.data;
  },

  getCorrelation: async (portfolioId: number): Promise<{ portfolio_id: number; correlation_matrix: any }> => {
    const response = await api.get(`/portfolios/${portfolioId}/correlation`);
    return response.data;
  },
};

export const stockApi = {
  getQuote: async (ticker: string): Promise<StockQuote> => {
    const response = await api.get(`/stocks/${ticker}/quote`);
    return response.data;
  },

  getHistory: async (ticker: string, period: string = '1mo', interval: string = '1d') => {
    const response = await api.get(`/stocks/${ticker}/history`, {
      params: { period, interval }
    });
    return response.data;
  },

  getIndicators: async (ticker: string, period: string = '6mo'): Promise<TechnicalIndicators> => {
    const response = await api.get(`/stocks/${ticker}/indicators`, {
      params: { period }
    });
    return response.data;
  },
};

export default api;
