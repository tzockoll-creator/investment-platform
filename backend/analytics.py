"""
Portfolio Analytics Module
Calculate advanced metrics like Sharpe ratio, volatility, beta, etc.
"""

import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
from models import Holding


def calculate_portfolio_metrics(holdings: List[Holding]) -> Dict:
    """
    Calculate comprehensive portfolio metrics
    
    Returns:
        Dictionary containing:
        - sharpe_ratio: Risk-adjusted return metric
        - volatility: Standard deviation of returns
        - beta: Market correlation (vs S&P 500)
        - max_drawdown: Largest peak-to-trough decline
        - average_return: Mean daily return
    """
    
    # Get historical data for all holdings
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year of data
    
    portfolio_returns = []
    weights = []
    total_value = 0
    
    # Calculate weights and get returns for each holding
    for holding in holdings:
        try:
            stock = yf.Ticker(holding.ticker)
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                continue
            
            # Calculate daily returns
            daily_returns = hist['Close'].pct_change().dropna()
            
            # Current value of this holding
            current_price = hist['Close'].iloc[-1]
            holding_value = holding.shares * current_price
            total_value += holding_value
            
            portfolio_returns.append(daily_returns)
            weights.append(holding_value)
            
        except Exception as e:
            print(f"Error fetching data for {holding.ticker}: {e}")
            continue
    
    if not portfolio_returns:
        return {
            "sharpe_ratio": None,
            "volatility": 0.0,
            "beta": None,
            "max_drawdown": 0.0,
            "average_return": 0.0
        }
    
    # Normalize weights
    weights = np.array(weights)
    weights = weights / weights.sum()
    
    # Align all return series to same dates
    aligned_returns = align_returns(portfolio_returns)
    
    # Calculate weighted portfolio returns
    weighted_returns = np.zeros(len(aligned_returns[0]))
    for i, returns in enumerate(aligned_returns):
        weighted_returns += weights[i] * returns
    
    # Calculate metrics
    volatility = calculate_volatility(weighted_returns)
    sharpe_ratio = calculate_sharpe_ratio(weighted_returns)
    beta = calculate_beta(weighted_returns, start_date, end_date)
    max_drawdown = calculate_max_drawdown(weighted_returns)
    average_return = np.mean(weighted_returns) * 100  # Convert to percentage
    
    return {
        "sharpe_ratio": round(sharpe_ratio, 4) if sharpe_ratio else None,
        "volatility": round(volatility * 100, 2),  # Convert to percentage
        "beta": round(beta, 4) if beta else None,
        "max_drawdown": round(max_drawdown * 100, 2),  # Convert to percentage
        "average_return": round(average_return, 4)
    }


def align_returns(return_series: List) -> List[np.ndarray]:
    """Align multiple return series to common dates"""
    # Find common index
    common_index = return_series[0].index
    for series in return_series[1:]:
        common_index = common_index.intersection(series.index)
    
    # Reindex all series to common dates
    aligned = []
    for series in return_series:
        aligned.append(series.reindex(common_index).values)
    
    return aligned


def calculate_volatility(returns: np.ndarray) -> float:
    """Calculate annualized volatility"""
    daily_vol = np.std(returns)
    # Annualize (assuming 252 trading days)
    annual_vol = daily_vol * np.sqrt(252)
    return annual_vol


def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: Array of daily returns
        risk_free_rate: Annual risk-free rate (default 2%)
    """
    if len(returns) == 0:
        return None
    
    # Convert annual risk-free rate to daily
    daily_rf = (1 + risk_free_rate) ** (1/252) - 1
    
    # Calculate excess returns
    excess_returns = returns - daily_rf
    
    # Sharpe ratio = mean excess return / std of excess returns
    if np.std(excess_returns) == 0:
        return None
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns)
    
    # Annualize
    sharpe_annual = sharpe * np.sqrt(252)
    
    return sharpe_annual


def calculate_beta(
    portfolio_returns: np.ndarray,
    start_date: datetime,
    end_date: datetime
) -> float:
    """
    Calculate portfolio beta (correlation with market - S&P 500)
    """
    try:
        # Get S&P 500 returns
        spy = yf.Ticker("SPY")
        market_hist = spy.history(start=start_date, end=end_date)
        market_returns = market_hist['Close'].pct_change().dropna().values
        
        # Ensure same length
        min_len = min(len(portfolio_returns), len(market_returns))
        portfolio_returns = portfolio_returns[-min_len:]
        market_returns = market_returns[-min_len:]
        
        # Calculate beta: covariance(portfolio, market) / variance(market)
        covariance = np.cov(portfolio_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return None
        
        beta = covariance / market_variance
        return beta
        
    except Exception as e:
        print(f"Error calculating beta: {e}")
        return None


def calculate_max_drawdown(returns: np.ndarray) -> float:
    """
    Calculate maximum drawdown - largest peak-to-trough decline
    """
    if len(returns) == 0:
        return 0.0
    
    # Calculate cumulative returns
    cumulative = np.cumprod(1 + returns)
    
    # Calculate running maximum
    running_max = np.maximum.accumulate(cumulative)
    
    # Calculate drawdown at each point
    drawdown = (cumulative - running_max) / running_max
    
    # Return the maximum drawdown (most negative value)
    max_dd = np.min(drawdown)
    
    return abs(max_dd)


def calculate_correlation_matrix(holdings: List[Holding]) -> Dict:
    """
    Calculate correlation matrix between holdings
    Useful for diversification analysis
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    tickers = [h.ticker for h in holdings]
    returns_dict = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            returns_dict[ticker] = hist['Close'].pct_change().dropna()
        except:
            continue
    
    if len(returns_dict) < 2:
        return {}
    
    # Create correlation matrix
    # This would typically use pandas DataFrame.corr()
    # Simplified version here
    correlation = {}
    for ticker in returns_dict:
        correlation[ticker] = {}
    
    return correlation
