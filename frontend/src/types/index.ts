export interface Portfolio {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Holding {
  id: number;
  ticker: string;
  shares: number;
  avg_cost: number;
  current_price: number;
  current_value: number;
  cost_basis: number;
  gain_loss: number;
  gain_loss_pct: number;
}

export interface PortfolioDetail {
  id: number;
  name: string;
  description: string | null;
  total_value: number;
  total_cost: number;
  total_gain_loss: number;
  total_gain_loss_pct: number;
  holdings: Holding[];
}

export interface Analytics {
  sharpe_ratio: number | null;
  volatility: number;
  beta: number | null;
  max_drawdown: number;
  average_return: number;
}

export interface SectorAllocation {
  [sector: string]: {
    value: number;
    percentage: number;
  };
}

export interface BenchmarkData {
  portfolio: {
    total_return: number;
    annualized_return: number;
    volatility: number;
  };
  benchmark: {
    ticker: string;
    total_return: number;
    annualized_return: number;
    volatility: number;
  };
  alpha: number;
  outperformance: number;
}

export interface TechnicalIndicators {
  ticker: string;
  current_price: number;
  moving_averages: {
    ma_20: number | null;
    ma_50: number | null;
    ma_200: number | null;
  };
  rsi: {
    value: number | null;
    signal: string | null;
  };
  macd: {
    macd: number | null;
    signal: number | null;
    histogram: number | null;
    trend: string | null;
  };
}

export interface StockQuote {
  ticker: string;
  current_price: number;
  change: number;
  change_pct: number;
  volume: number;
  market_cap: number | null;
  pe_ratio: number | null;
}
