"""
Demo script to test the Investment Platform API
Run this to verify everything is working
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def pretty_print(data):
    print(json.dumps(data, indent=2))

def test_api():
    print("🚀 Investment Platform API Test")
    
    # 1. Health check
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/")
    pretty_print(response.json())
    
    # 2. Create portfolio
    print_section("2. Create Portfolio")
    portfolio_data = {
        "name": "Tech Growth Portfolio",
        "description": "Long-term tech investments"
    }
    response = requests.post(f"{BASE_URL}/api/portfolios", json=portfolio_data)
    portfolio = response.json()
    pretty_print(portfolio)
    portfolio_id = portfolio['id']
    
    # 3. Add holdings
    print_section("3. Add Holdings")
    holdings = [
        {"ticker": "AAPL", "shares": 50, "avg_cost": 150.00},
        {"ticker": "MSFT", "shares": 30, "avg_cost": 280.00},
        {"ticker": "GOOGL", "shares": 20, "avg_cost": 125.00},
    ]
    
    for holding in holdings:
        response = requests.post(
            f"{BASE_URL}/api/portfolios/{portfolio_id}/holdings",
            json=holding
        )
        print(f"Added {holding['ticker']}: {response.json()}")
    
    # 4. Get portfolio details
    print_section("4. Portfolio Details with Live Prices")
    response = requests.get(f"{BASE_URL}/api/portfolios/{portfolio_id}")
    pretty_print(response.json())
    
    # 5. Get stock quote
    print_section("5. Stock Quote - AAPL")
    response = requests.get(f"{BASE_URL}/api/stocks/AAPL/quote")
    pretty_print(response.json())
    
    # 6. Get historical data
    print_section("6. Historical Data - AAPL (1 week)")
    response = requests.get(f"{BASE_URL}/api/stocks/AAPL/history?period=5d&interval=1d")
    data = response.json()
    print(f"Ticker: {data['ticker']}")
    print(f"Data points: {len(data['data'])}")
    if data['data']:
        print("Sample data point:")
        pretty_print(data['data'][0])
    
    # 7. Get analytics
    print_section("7. Portfolio Analytics")
    print("Calculating Sharpe ratio, Beta, Volatility...")
    response = requests.get(f"{BASE_URL}/api/portfolios/{portfolio_id}/analytics")
    pretty_print(response.json())
    
    # 8. List all portfolios
    print_section("8. All Portfolios")
    response = requests.get(f"{BASE_URL}/api/portfolios")
    pretty_print(response.json())
    
    print("\n" + "="*60)
    print("✅ All tests completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("- Visit http://localhost:8000/docs for interactive API docs")
    print("- Try creating your own portfolios with real holdings")
    print("- Check out the analytics for risk metrics")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n⚠️  Make sure the API server is running:")
    print("   python main.py\n")
    input("Press Enter when server is ready...")
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
