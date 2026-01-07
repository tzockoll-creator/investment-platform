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

### Phase 3: Frontend Dashboard ✅
- **React + TypeScript**: Modern, type-safe frontend
- **Interactive Charts**: Recharts for beautiful visualizations
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Portfolio Management**: Create, view, delete portfolios
- **Holdings Management**: Add/remove positions
- **Sector Visualization**: Pie chart showing allocation
- **Performance Comparison**: Bar charts vs benchmarks
- **Responsive Design**: Works on desktop and mobile

### Phase 4: Deployment ✅
- **Docker Containerization**: Multi-stage builds for production
- **Docker Compose**: Orchestration for local/production deployment
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **Cloud Ready**: Configurations for AWS ECS, GCP Cloud Run, Azure
- **Health Checks**: Built-in monitoring endpoints
- **Production Optimized**: Nginx serving, gzip compression, caching

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**Prerequisites**: Docker and Docker Compose

```bash
# Clone the repository
git clone https://github.com/tzockoll-creator/investment-platform.git
cd investment-platform

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Manual Setup

**Prerequisites**: Python 3.9+, Node.js 18+

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

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
│   ├── analytics.py         # Portfolio metrics & indicators
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container config
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API service layer
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx          # Main application
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Node dependencies
│   ├── vite.config.ts       # Vite configuration
│   ├── Dockerfile           # Frontend container config
│   └── nginx.conf           # Nginx configuration
├── deploy/
│   ├── docker-compose.prod.yml
│   ├── aws-ecs-task-definition.json
│   └── README.md            # Deployment guide
├── .github/workflows/
│   ├── ci-cd.yml            # Main CI/CD pipeline
│   └── docker-compose-test.yml
├── docker-compose.yml       # Local development
└── README.md
```

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy, yfinance, NumPy
- **Frontend**: React, TypeScript, Recharts, Axios
- **Build Tools**: Vite, ESLint
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Deployment**: Docker, Docker Compose, Nginx
- **CI/CD**: GitHub Actions
- **Cloud**: AWS ECS, GCP Cloud Run, Azure (ready)

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

### Backend Tests
```bash
cd backend
pip install pytest httpx
python test_api.py
```

### Frontend Tests
```bash
cd frontend
npm run lint
npm run build
```

### Docker Tests
```bash
# Test docker-compose setup
docker-compose up -d
curl http://localhost:8000/
curl http://localhost:3000/
docker-compose down
```

### CI/CD
GitHub Actions automatically runs:
- Backend syntax checks
- Frontend linting and build
- Docker Compose integration tests
- Image builds and pushes (on main branch)

---

## 🚀 Deployment

### Docker Compose (Simplest)
```bash
# Development
docker-compose up -d

# Production
docker-compose -f deploy/docker-compose.prod.yml up -d
```

### Cloud Deployment

#### AWS ECS/Fargate
```bash
# Build and push images
docker build -t <account>.dkr.ecr.us-east-1.amazonaws.com/backend backend/
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/backend

# Deploy using task definition
aws ecs register-task-definition --cli-input-json file://deploy/aws-ecs-task-definition.json
```

#### Google Cloud Run
```bash
gcloud run deploy backend --image gcr.io/<project>/backend --platform managed
gcloud run deploy frontend --image gcr.io/<project>/frontend --platform managed
```

#### Azure Container Instances
```bash
az container create --resource-group myRG --name investment-platform \
  --image myregistry.azurecr.io/investment-platform:latest
```

See [deploy/README.md](deploy/README.md) for detailed deployment guides.

---

## 🛣️ Roadmap

- [x] Phase 1: Backend API with portfolio management
- [x] Phase 1: Real-time market data integration
- [x] Phase 1: Advanced analytics (Sharpe, Beta, etc.)
- [x] Phase 2: Sector allocation analysis
- [x] Phase 2: Technical indicators (MA, RSI, MACD)
- [x] Phase 2: Performance benchmarking vs S&P 500
- [x] Phase 2: Correlation matrix for diversification
- [x] Phase 3: React + TypeScript frontend
- [x] Phase 3: Interactive charts with Recharts
- [x] Phase 3: Real-time updates (30s refresh)
- [x] Phase 3: Portfolio & holdings management UI
- [x] Phase 4: Docker containerization
- [x] Phase 4: Docker Compose orchestration
- [x] Phase 4: CI/CD pipeline with GitHub Actions
- [x] Phase 4: Multi-cloud deployment configurations
- [ ] Additional: User authentication & authorization
- [ ] Additional: Multi-currency support
- [ ] Additional: Cryptocurrency tracking
- [ ] Additional: Email alerts for portfolio changes
- [ ] Additional: Export reports (PDF/Excel)

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
