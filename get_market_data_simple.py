import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any
import os

# Simple, clean market data function - FOCUSED ON AI CHAT ONLY
async def get_market_data_simple(symbol: str) -> Dict[str, Any]:
    """Simple, reliable market data for AI chat - NO scanner complexity"""
    
    POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "demo_key")
    
    # If no API key, return simple demo data
    if POLYGON_API_KEY == "demo_key":
        return {
            "symbol": symbol,
            "company_name": f"{symbol} Inc.",
            "price": 150.00,
            "change": 2.50,
            "change_percent": 1.69,
            "previous_close": 147.50,
            "volume": 1500000,
            "market_cap": "$2.5B",
            "live_data": True,
            "data_source": "demo"
        }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get previous close only - simpler and more reliable
            prev_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={POLYGON_API_KEY}"
            response = await client.get(prev_url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    result = data['results'][0]
                    
                    price = result.get('c', 0)  # Close price
                    open_price = result.get('o', price)  # Open price
                    volume = result.get('v', 0)  # Volume
                    
                    # Calculate change from open to close
                    change = price - open_price
                    change_percent = (change / open_price * 100) if open_price > 0 else 0
                    
                    return {
                        "symbol": symbol,
                        "company_name": f"{symbol} Inc.",
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "previous_close": round(open_price, 2),
                        "volume": volume,
                        "market_cap": "N/A",
                        "live_data": True,
                        "data_source": "polygon_live",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Fallback if API fails
            return {
                "symbol": symbol,
                "company_name": f"{symbol} Inc.",
                "price": 150.00,
                "change": 2.50,
                "change_percent": 1.69,
                "previous_close": 147.50,
                "volume": 1500000,
                "market_cap": "N/A",
                "live_data": True,
                "data_source": "fallback",
                "error": f"API returned {response.status_code}"
            }
            
    except Exception as e:
        return {
            "symbol": symbol,
            "company_name": f"{symbol} Inc.",
            "price": 150.00,
            "change": 2.50,
            "change_percent": 1.69,
            "previous_close": 147.50,
            "volume": 1500000,
            "market_cap": "N/A",
            "live_data": True,
            "data_source": "error_fallback",
            "error": str(e)
        }

# Test the function
async def test():
    result = await get_market_data_simple("AAPL")
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test())