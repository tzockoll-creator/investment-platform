# 📊 Investment Platform

A professional full-stack investment analysis platform combining portfolio management, real-time market data, and advanced analytics.

## 🌟 Features

### Phase 1: Backend API (Current) ✅
- **RESTful API** built with FastAPI
- **Portfolio Management**: Create, read, update, delete portfolios
- **Holdings Tracking**: Add/remove positions with cost basis tracking
- **Real-time Market Data**: Live stock quotes via Yahoo Finance
- **Historical Data**: Access price history with customizable periods
- **Advanced Analytics**:
  - Sharpe Ratio (risk-adjusted returns)
  - Portfolio Volatility
  - Beta (market correlation)
  - Maximum Drawdown
  - Average Returns
- **Database**: SQLAlchemy ORM with SQLite (production-ready for PostgreSQL)
- **API Documentation**: Auto-generated with Swagger UI

### Phase 2: Data Analysis ✅
- **Sector Allocation**: Portfolio breakdown by industry sectors
- **Performance Benchmarking**: Compare against S&P 500 or custom benchmarks
- **Technical Indicators**: Moving averages (MA), RSI, MACD for stocks
- **Correlation Matrix**: Diversification analysis across holdings

### Phase 3: Frontend Dashboard (Coming Soon) 🚧
- React + TypeScript
- Interactive charts with Recharts
- Real-time updates
- Portfolio visualization

### Phase 4: Deployment (Coming Soon) 🚧
- Docker containerization
- CI/CD pipeline
- Cloud deployment (AWS/GCP/Azure)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/investment-platform.git
cd investment-platform/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation
Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📖 API Endpoints

### Portfolio Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/portfolios` | Create new portfolio |
| GET | `/api/portfolios` | List all portfolios |
| GET | `/api/portfolios/{id}` | Get portfolio details with valuations |
| DELETE | `/api/portfolios/{id}` | Delete portfolio |

### Holdings

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/portfolios/{id}/holdings` | Add holding to portfolio |
| DELETE | `/api/holdings/{id}` | Remove holding |

### Market Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stocks/{ticker}/quote` | Get current stock quote |
| GET | `/api/stocks/{ticker}/history` | Get historical prices |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolios/{id}/analytics` | Get portfolio analytics (Sharpe, Beta, etc.) |
| GET | `/api/portfolios/{id}/sectors` | Get sector allocation breakdown |
| GET | `/api/portfolios/{id}/benchmark` | Compare performance vs benchmark |
| GET | `/api/portfolios/{id}/correlation` | Get correlation matrix for holdings |
| GET | `/api/stocks/{ticker}/indicators` | Get technical indicators (MA, RSI, MACD) |

---

## 💡 Usage Examples

### Create a Portfolio
```bash
curl -X POST "http://localhost:8000/api/portfolios" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Tech Portfolio",
    "description": "Long-term tech investments"
  }'
```

### Add Holdings
```bash
curl -X POST "http://localhost:8000/api/portfolios/1/holdings" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "shares": 50,
    "avg_cost": 150.00
  }'
```

### Get Portfolio Analysis
```bash
curl "http://localhost:8000/api/portfolios/1"
```

### Get Stock Quote
```bash
curl "http://localhost:8000/api/stocks/AAPL/quote"
```

### Get Analytics
```bash
curl "http://localhost:8000/api/portfolios/1/analytics"
```

### Get Sector Allocation (Phase 2)
```bash
curl "http://localhost:8000/api/portfolios/1/sectors"
```

### Compare Performance vs S&P 500 (Phase 2)
```bash
curl "http://localhost:8000/api/portfolios/1/benchmark"
```

### Get Correlation Matrix (Phase 2)
```bash
curl "http://localhost:8000/api/portfolios/1/correlation"
```

### Get Technical Indicators (Phase 2)
```bash
curl "http://localhost:8000/api/stocks/AAPL/indicators?period=6mo"
```

---

## 🏗️ Architecture

```
investment-platform/
├── backend/
│   ├── main.py              # FastAPI application & routes
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database configuration
│   ├── analytics.py         # Portfolio metrics calculations
│   └── requirements.txt     # Python dependencies
├── frontend/                # React app (Phase 3)
└── README.md
```

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy, yfinance
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **API**: RESTful with OpenAPI/Swagger docs
- **Analytics**: NumPy for calculations

---

## 📊 Analytics Explained

### Sharpe Ratio
Measures risk-adjusted returns. Higher is better.
- **> 1.0**: Good
- **> 2.0**: Very good
- **> 3.0**: Excellent

### Beta
Measures correlation with market (S&P 500).
- **β < 1**: Less volatile than market
- **β = 1**: Moves with market
- **β > 1**: More volatile than market

### Volatility
Annualized standard deviation of returns.
- Lower = more stable
- Higher = more risky

### Max Drawdown
Largest peak-to-trough decline.
- Shows worst-case scenario
- Important for risk management

---

## 🔧 Configuration

### Environment Variables
```bash
# Database URL (optional, defaults to SQLite)
export DATABASE_URL="postgresql://user:pass@localhost/dbname"

# API Port (optional, defaults to 8000)
export PORT=8000
```

### Switching to PostgreSQL
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Set database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/investment_db"
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (coming soon)
pytest
```

---

## 🚀 Deployment

### Docker (Coming Soon)
```bash
docker build -t investment-platform .
docker run -p 8000:8000 investment-platform
```

### Cloud Deployment
- AWS: Elastic Beanstalk / ECS
- GCP: Cloud Run / App Engine
- Azure: App Service

---

## 🛣️ Roadmap

- [x] Phase 1: Backend API with portfolio management
- [x] Phase 1: Real-time market data integration
- [x] Phase 1: Advanced analytics (Sharpe, Beta, etc.)
- [x] Phase 2: Sector allocation analysis
- [x] Phase 2: Technical indicators (MA, RSI, MACD)
- [x] Phase 2: Performance benchmarking vs S&P 500
- [x] Phase 2: Correlation matrix for diversification
- [ ] Phase 3: React frontend
- [ ] Phase 3: Interactive charts
- [ ] Phase 3: Real-time updates
- [ ] Phase 4: Docker deployment
- [ ] Phase 4: CI/CD pipeline
- [ ] Additional: User authentication
- [ ] Additional: Multi-currency support
- [ ] Additional: Cryptocurrency tracking

---

## 📝 License

MIT License - feel free to use for your portfolio!

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📧 Contact

Built by Tom Zockoll
- GitHub: [@tzockoll-creator](https://github.com/tzockoll-creator)

---

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- Yahoo Finance for market data
- The open-source community

---

**⚠️ Disclaimer**: This is a portfolio/educational project. Not financial advice. Always do your own research before making investment decisions.
