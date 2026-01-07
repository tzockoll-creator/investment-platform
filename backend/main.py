"""
Investment Platform API
A comprehensive RESTful API for portfolio management and stock analysis
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import yfinance as yf
from pydantic import BaseModel
from database import get_db, init_db
from models import Portfolio, Holding, StockData
import uvicorn
import time
from threading import Lock

# Cache for stock data to reduce API calls
_api_cache = {}
_cache_lock = Lock()
_last_request_time = {}
_request_lock = Lock()

# Rate limiting: minimum delay between requests (in seconds)
MIN_REQUEST_DELAY = 0.5


def _get_cached_or_fetch_api(cache_key: str, fetch_func, cache_duration: int = 300):
    """
    Get data from cache or fetch if expired/missing

    Args:
        cache_key: Unique key for cache entry
        fetch_func: Function to call if cache miss
        cache_duration: Cache duration in seconds (default: 5 minutes)
    """
    with _cache_lock:
        now = time.time()

        # Check if cached and not expired
        if cache_key in _api_cache:
            cached_data, cached_time = _api_cache[cache_key]
            if now - cached_time < cache_duration:
                print(f"Cache hit for {cache_key}")
                return cached_data

    # Rate limiting: wait if needed
    with _request_lock:
        if cache_key in _last_request_time:
            elapsed = time.time() - _last_request_time[cache_key]
            if elapsed < MIN_REQUEST_DELAY:
                time.sleep(MIN_REQUEST_DELAY - elapsed)

        _last_request_time[cache_key] = time.time()

    # Fetch new data
    try:
        print(f"Cache miss for {cache_key} - fetching from API")
        data = fetch_func()

        # Cache the result
        with _cache_lock:
            _api_cache[cache_key] = (data, time.time())

        return data
    except Exception as e:
        # If fetch fails, return stale cache if available
        with _cache_lock:
            if cache_key in _api_cache:
                print(f"Warning: Using stale cache for {cache_key} due to error: {e}")
                cached_data, _ = _api_cache[cache_key]
                return cached_data
        raise

app = FastAPI(
    title="Investment Platform API",
    description="Professional-grade API for portfolio management and stock analysis",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class HoldingCreate(BaseModel):
    ticker: str
    shares: float
    avg_cost: float

class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_pct: float
    holdings: List[dict]

class StockQuote(BaseModel):
    ticker: str
    current_price: float
    change: float
    change_pct: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]

class AnalyticsResponse(BaseModel):
    sharpe_ratio: Optional[float]
    volatility: float
    beta: Optional[float]
    max_drawdown: float
    average_return: float


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Investment Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# PORTFOLIO ENDPOINTS
# ============================================================================

@app.post("/api/portfolios", response_model=dict, status_code=201)
async def create_portfolio(portfolio: PortfolioCreate, db=Depends(get_db)):
    """Create a new portfolio"""
    db_portfolio = Portfolio(
        name=portfolio.name,
        description=portfolio.description,
        created_at=datetime.now()
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    
    return {
        "id": db_portfolio.id,
        "name": db_portfolio.name,
        "description": db_portfolio.description,
        "created_at": db_portfolio.created_at.isoformat()
    }

@app.get("/api/portfolios", response_model=List[dict])
async def get_portfolios(db=Depends(get_db)):
    """Get all portfolios"""
    portfolios = db.query(Portfolio).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "created_at": p.created_at.isoformat()
        }
        for p in portfolios
    ]

@app.get("/api/portfolios/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int, db=Depends(get_db)):
    """Get detailed portfolio information with current valuations"""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    
    # Calculate current values
    holdings_data = []
    total_value = 0
    total_cost = 0
    
    for holding in holdings:
        # Fetch current price
        current_price = get_current_price(holding.ticker)
        current_value = holding.shares * current_price
        cost_basis = holding.shares * holding.avg_cost
        gain_loss = current_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        holdings_data.append({
            "id": holding.id,
            "ticker": holding.ticker,
            "shares": holding.shares,
            "avg_cost": holding.avg_cost,
            "current_price": current_price,
            "current_value": current_value,
            "cost_basis": cost_basis,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct
        })
        
        total_value += current_value
        total_cost += cost_basis
    
    total_gain_loss = total_value - total_cost
    total_gain_loss_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    return PortfolioResponse(
        id=portfolio.id,
        name=portfolio.name,
        description=portfolio.description,
        total_value=total_value,
        total_cost=total_cost,
        total_gain_loss=total_gain_loss,
        total_gain_loss_pct=total_gain_loss_pct,
        holdings=holdings_data
    )

@app.delete("/api/portfolios/{portfolio_id}", status_code=204)
async def delete_portfolio(portfolio_id: int, db=Depends(get_db)):
    """Delete a portfolio and all its holdings"""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Delete all holdings first
    db.query(Holding).filter(Holding.portfolio_id == portfolio_id).delete()
    db.delete(portfolio)
    db.commit()
    
    return None


# ============================================================================
# HOLDINGS ENDPOINTS
# ============================================================================

@app.post("/api/portfolios/{portfolio_id}/holdings", status_code=201)
async def add_holding(
    portfolio_id: int,
    holding: HoldingCreate,
    db=Depends(get_db)
):
    """Add a holding to a portfolio"""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Validate ticker (lenient - allows adding even if validation fails)
    try:
        ticker_data = yf.Ticker(holding.ticker)
        info = ticker_data.info
        if not info or len(info) == 0:
            print(f"Warning: Could not validate ticker {holding.ticker}, but allowing it anyway")
    except Exception as e:
        print(f"Warning: Ticker validation failed for {holding.ticker}: {str(e)}, but allowing it anyway")
    
    db_holding = Holding(
        portfolio_id=portfolio_id,
        ticker=holding.ticker.upper(),
        shares=holding.shares,
        avg_cost=holding.avg_cost,
        added_at=datetime.now()
    )
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    
    return {
        "id": db_holding.id,
        "ticker": db_holding.ticker,
        "shares": db_holding.shares,
        "avg_cost": db_holding.avg_cost
    }

@app.delete("/api/holdings/{holding_id}", status_code=204)
async def delete_holding(holding_id: int, db=Depends(get_db)):
    """Delete a specific holding"""
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    db.delete(holding)
    db.commit()
    return None


# ============================================================================
# STOCK DATA ENDPOINTS
# ============================================================================

@app.get("/api/stocks/{ticker}/quote", response_model=StockQuote)
async def get_stock_quote(ticker: str):
    """Get current quote for a stock"""
    try:
        cache_key = f"stock_quote_{ticker.upper()}"

        def fetch_quote():
            stock = yf.Ticker(ticker.upper())
            return stock.info

        # Use cache with 2 minute expiration for quotes
        info = _get_cached_or_fetch_api(cache_key, fetch_quote, cache_duration=120)

        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', current_price)
        change = current_price - previous_close
        change_pct = (change / previous_close * 100) if previous_close > 0 else 0

        return StockQuote(
            ticker=ticker.upper(),
            current_price=current_price,
            change=change,
            change_pct=change_pct,
            volume=info.get('volume', 0),
            market_cap=info.get('marketCap'),
            pe_ratio=info.get('trailingPE')
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch data for {ticker}: {str(e)}")

@app.get("/api/stocks/{ticker}/history")
async def get_stock_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d"
):
    """Get historical price data for a stock"""
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "ticker": ticker.upper(),
            "period": period,
            "interval": interval,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/portfolios/{portfolio_id}/analytics", response_model=AnalyticsResponse)
async def get_portfolio_analytics(portfolio_id: int, db=Depends(get_db)):
    """Calculate advanced analytics for a portfolio"""
    from analytics import calculate_portfolio_metrics

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    if not holdings:
        raise HTTPException(status_code=400, detail="Portfolio has no holdings")

    metrics = calculate_portfolio_metrics(holdings)
    return AnalyticsResponse(**metrics)


# ============================================================================
# PHASE 2: DATA ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/api/portfolios/{portfolio_id}/sectors")
async def get_sector_allocation(portfolio_id: int, db=Depends(get_db)):
    """Get sector allocation analysis for a portfolio"""
    from analytics import calculate_sector_allocation

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    if not holdings:
        raise HTTPException(status_code=400, detail="Portfolio has no holdings")

    sector_data = calculate_sector_allocation(holdings)
    return {
        "portfolio_id": portfolio_id,
        "sectors": sector_data
    }

@app.get("/api/portfolios/{portfolio_id}/benchmark")
async def get_performance_benchmark(
    portfolio_id: int,
    benchmark: str = "SPY",
    db=Depends(get_db)
):
    """Compare portfolio performance against a benchmark (default: S&P 500)"""
    from analytics import calculate_performance_benchmark

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    if not holdings:
        raise HTTPException(status_code=400, detail="Portfolio has no holdings")

    benchmark_data = calculate_performance_benchmark(holdings, benchmark)

    if "error" in benchmark_data:
        raise HTTPException(status_code=500, detail=benchmark_data["error"])

    return {
        "portfolio_id": portfolio_id,
        "benchmark_data": benchmark_data
    }

@app.get("/api/portfolios/{portfolio_id}/correlation")
async def get_correlation_matrix(portfolio_id: int, db=Depends(get_db)):
    """Get correlation matrix for portfolio holdings (diversification analysis)"""
    from analytics import calculate_correlation_matrix

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    if not holdings:
        raise HTTPException(status_code=400, detail="Portfolio has no holdings")

    correlation_data = calculate_correlation_matrix(holdings)

    if "error" in correlation_data:
        raise HTTPException(status_code=400, detail=correlation_data["error"])

    return {
        "portfolio_id": portfolio_id,
        "correlation_matrix": correlation_data
    }

@app.get("/api/stocks/{ticker}/indicators")
async def get_technical_indicators(ticker: str, period: str = "6mo"):
    """Get technical indicators for a stock (MA, RSI, MACD)"""
    from analytics import calculate_technical_indicators

    indicators = calculate_technical_indicators(ticker, period)

    if "error" in indicators:
        raise HTTPException(status_code=404, detail=indicators["error"])

    return indicators


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_price(ticker: str) -> float:
    """Fetch current price for a ticker"""
    try:
        cache_key = f"stock_price_{ticker.upper()}"

        def fetch_price():
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('currentPrice') or info.get('regularMarketPrice', 0)

        # Use cache with 2 minute expiration
        return _get_cached_or_fetch_api(cache_key, fetch_price, cache_duration=120)
    except:
        return 0.0


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
