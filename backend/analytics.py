"""
Portfolio Analytics Module
Calculate advanced metrics like Sharpe ratio, volatility, beta, etc.
"""

import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
from models import Holding
import time
from functools import lru_cache
from threading import Lock

# Cache for stock data to reduce API calls
_cache = {}
_cache_lock = Lock()
_last_request_time = {}
_request_lock = Lock()

# Rate limiting: minimum delay between requests (in seconds)
MIN_REQUEST_DELAY = 2.0  # Increased from 0.5 to 2 seconds


def _get_cached_or_fetch(cache_key: str, fetch_func, cache_duration: int = 300, max_retries: int = 3):
    """
    Get data from cache or fetch if expired/missing with retry logic

    Args:
        cache_key: Unique key for cache entry
        fetch_func: Function to call if cache miss
        cache_duration: Cache duration in seconds (default: 5 minutes)
        max_retries: Maximum number of retry attempts (default: 3)
    """
    with _cache_lock:
        now = time.time()

        # Check if cached and not expired
        if cache_key in _cache:
            cached_data, cached_time = _cache[cache_key]
            if now - cached_time < cache_duration:
                return cached_data

    # Rate limiting: wait if needed
    with _request_lock:
        if cache_key in _last_request_time:
            elapsed = time.time() - _last_request_time[cache_key]
            if elapsed < MIN_REQUEST_DELAY:
                time.sleep(MIN_REQUEST_DELAY - elapsed)

        _last_request_time[cache_key] = time.time()

    # Fetch new data with retry logic
    last_error = None
    for attempt in range(max_retries):
        try:
            data = fetch_func()

            # Cache the result
            with _cache_lock:
                _cache[cache_key] = (data, time.time())

            return data
        except Exception as e:
            last_error = e
            error_msg = str(e)

            # If rate limited (429), wait longer before retry
            if "429" in error_msg or "Too Many Requests" in error_msg:
                backoff_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                print(f"⏳ Rate limited - backing off for {backoff_time}s")
                time.sleep(backoff_time)
            elif attempt < max_retries - 1:
                # Exponential backoff for other errors
                backoff_time = 2 ** attempt
                time.sleep(backoff_time)

    # All retries failed - try stale cache
    with _cache_lock:
        if cache_key in _cache:
            print(f"Warning: Using stale cache for {cache_key} due to error: {last_error}")
            cached_data, _ = _cache[cache_key]
            return cached_data
    raise last_error


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

    # Get returns for all tickers
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                returns_dict[ticker] = hist['Close'].pct_change().dropna()
        except:
            continue

    if len(returns_dict) < 2:
        return {"error": "Need at least 2 holdings to calculate correlation"}

    # Align all return series to common dates
    common_index = None
    for series in returns_dict.values():
        if common_index is None:
            common_index = series.index
        else:
            common_index = common_index.intersection(series.index)

    # Build correlation matrix
    correlation = {}
    tickers_list = list(returns_dict.keys())

    for ticker1 in tickers_list:
        correlation[ticker1] = {}
        returns1 = returns_dict[ticker1].reindex(common_index).values

        for ticker2 in tickers_list:
            returns2 = returns_dict[ticker2].reindex(common_index).values

            # Calculate correlation coefficient
            if len(returns1) > 1 and len(returns2) > 1:
                corr_coef = np.corrcoef(returns1, returns2)[0, 1]
                correlation[ticker1][ticker2] = round(float(corr_coef), 4)
            else:
                correlation[ticker1][ticker2] = 0.0

    return correlation


def calculate_sector_allocation(holdings: List[Holding]) -> Dict:
    """
    Calculate sector allocation of portfolio
    Returns percentage breakdown by sector
    """
    sector_values = {}
    total_value = 0

    for holding in holdings:
        try:
            cache_key = f"stock_info_{holding.ticker}"

            def fetch_info():
                stock = yf.Ticker(holding.ticker)
                return stock.info

            # Use cache with 5 minute expiration
            info = _get_cached_or_fetch(cache_key, fetch_info, cache_duration=300)

            # Get current price and sector
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            sector = info.get('sector', 'Unknown')

            holding_value = holding.shares * current_price
            total_value += holding_value

            if sector in sector_values:
                sector_values[sector] += holding_value
            else:
                sector_values[sector] = holding_value

        except Exception as e:
            print(f"Error fetching sector for {holding.ticker}: {e}")
            continue

    if total_value == 0:
        return {}

    # Convert to percentages
    sector_allocation = {}
    for sector, value in sector_values.items():
        sector_allocation[sector] = {
            "value": round(value, 2),
            "percentage": round((value / total_value) * 100, 2)
        }

    return sector_allocation


def calculate_performance_benchmark(holdings: List[Holding], benchmark: str = "SPY") -> Dict:
    """
    Compare portfolio performance against a benchmark (default: S&P 500)

    Args:
        holdings: List of portfolio holdings
        benchmark: Ticker symbol for benchmark (default: SPY for S&P 500)

    Returns:
        Dictionary with portfolio vs benchmark performance metrics
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Calculate portfolio returns
    portfolio_returns = []
    weights = []
    total_value = 0

    for holding in holdings:
        try:
            stock = yf.Ticker(holding.ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                continue

            daily_returns = hist['Close'].pct_change().dropna()
            current_price = hist['Close'].iloc[-1]
            holding_value = holding.shares * current_price
            total_value += holding_value

            portfolio_returns.append(daily_returns)
            weights.append(holding_value)

        except Exception as e:
            print(f"Error fetching data for {holding.ticker}: {e}")
            continue

    if not portfolio_returns:
        return {"error": "Could not calculate portfolio returns"}

    # Normalize weights and calculate weighted returns
    weights = np.array(weights) / sum(weights)
    aligned_returns = align_returns(portfolio_returns)
    weighted_returns = np.zeros(len(aligned_returns[0]))
    for i, returns in enumerate(aligned_returns):
        weighted_returns += weights[i] * returns

    # Get benchmark returns
    try:
        benchmark_ticker = yf.Ticker(benchmark)
        benchmark_hist = benchmark_ticker.history(start=start_date, end=end_date)
        benchmark_returns = benchmark_hist['Close'].pct_change().dropna().values
    except Exception as e:
        return {"error": f"Could not fetch benchmark data: {str(e)}"}

    # Calculate cumulative returns
    portfolio_cumulative = (1 + weighted_returns).cumprod()[-1] - 1
    benchmark_cumulative = (1 + benchmark_returns).cumprod()[-1] - 1

    # Calculate annualized returns
    days = len(weighted_returns)
    portfolio_annual = ((1 + portfolio_cumulative) ** (252 / days)) - 1
    benchmark_annual = ((1 + benchmark_cumulative) ** (252 / days)) - 1

    # Calculate volatilities
    portfolio_vol = np.std(weighted_returns) * np.sqrt(252)
    benchmark_vol = np.std(benchmark_returns) * np.sqrt(252)

    # Calculate alpha (excess return over benchmark)
    alpha = portfolio_annual - benchmark_annual

    return {
        "portfolio": {
            "total_return": round(portfolio_cumulative * 100, 2),
            "annualized_return": round(portfolio_annual * 100, 2),
            "volatility": round(portfolio_vol * 100, 2)
        },
        "benchmark": {
            "ticker": benchmark,
            "total_return": round(benchmark_cumulative * 100, 2),
            "annualized_return": round(benchmark_annual * 100, 2),
            "volatility": round(benchmark_vol * 100, 2)
        },
        "alpha": round(alpha * 100, 2),
        "outperformance": round((portfolio_cumulative - benchmark_cumulative) * 100, 2)
    }


def calculate_technical_indicators(ticker: str, period: str = "6mo") -> Dict:
    """
    Calculate technical indicators for a stock

    Indicators:
        - Moving Averages (20, 50, 200 day)
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)

    Args:
        ticker: Stock ticker symbol
        period: Historical period (default: 6mo)

    Returns:
        Dictionary with technical indicator values
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"error": f"No data available for {ticker}"}

        close_prices = hist['Close'].values

        # Calculate Moving Averages
        ma_20 = calculate_sma(close_prices, 20)
        ma_50 = calculate_sma(close_prices, 50)
        ma_200 = calculate_sma(close_prices, 200)

        # Calculate RSI
        rsi = calculate_rsi(close_prices, period=14)

        # Calculate MACD
        macd_data = calculate_macd(close_prices)

        # Get current price
        current_price = close_prices[-1]

        return {
            "ticker": ticker.upper(),
            "current_price": round(float(current_price), 2),
            "moving_averages": {
                "ma_20": round(float(ma_20), 2) if ma_20 is not None else None,
                "ma_50": round(float(ma_50), 2) if ma_50 is not None else None,
                "ma_200": round(float(ma_200), 2) if ma_200 is not None else None
            },
            "rsi": {
                "value": round(float(rsi), 2) if rsi is not None else None,
                "signal": get_rsi_signal(rsi) if rsi is not None else None
            },
            "macd": macd_data
        }

    except Exception as e:
        return {"error": f"Error calculating indicators for {ticker}: {str(e)}"}


def calculate_sma(prices: np.ndarray, period: int) -> float:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])


def calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI)
    RSI measures momentum - values 0-100
    """
    if len(prices) < period + 1:
        return None

    # Calculate price changes
    deltas = np.diff(prices)

    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    # Calculate average gains and losses
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_rsi_signal(rsi: float) -> str:
    """Interpret RSI value"""
    if rsi >= 70:
        return "Overbought"
    elif rsi <= 30:
        return "Oversold"
    else:
        return "Neutral"


def calculate_macd(prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """
    Calculate MACD (Moving Average Convergence Divergence)

    MACD = 12-day EMA - 26-day EMA
    Signal = 9-day EMA of MACD
    Histogram = MACD - Signal
    """
    if len(prices) < slow:
        return {
            "macd": None,
            "signal": None,
            "histogram": None,
            "trend": None
        }

    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate signal line (EMA of MACD)
    # For simplicity, using SMA here; proper implementation would use EMA
    if len(prices) >= slow + signal:
        # Create array of MACD values
        macd_values = []
        for i in range(slow, len(prices)):
            ema_f = calculate_ema(prices[:i+1], fast)
            ema_s = calculate_ema(prices[:i+1], slow)
            macd_values.append(ema_f - ema_s)

        signal_line = np.mean(macd_values[-signal:]) if len(macd_values) >= signal else macd_line
    else:
        signal_line = macd_line

    histogram = macd_line - signal_line

    # Determine trend
    trend = "Bullish" if histogram > 0 else "Bearish"

    return {
        "macd": round(float(macd_line), 4),
        "signal": round(float(signal_line), 4),
        "histogram": round(float(histogram), 4),
        "trend": trend
    }


def calculate_ema(prices: np.ndarray, period: int) -> float:
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return np.mean(prices)

    multiplier = 2 / (period + 1)
    ema = np.mean(prices[:period])  # Start with SMA

    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema

    return ema
