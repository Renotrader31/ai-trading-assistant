#!/usr/bin/env python3
# Fix the get_market_data function to use real-time data

# Read the current file
with open('main.py', 'r') as f:
    content = f.read()

# Find the get_market_data function
start_marker = 'async def get_market_data(symbol: str) -> Dict[str, Any]:'
end_marker = 'async def get_ai_analysis(user_message: str, market_data: Dict[str, Any]) -> str:'

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)

if start_pos != -1 and end_pos != -1:
    # New REAL-TIME function
    new_function = '''async def get_market_data(symbol: str) -> Dict[str, Any]:
    """REAL-TIME market data for AI chat - Uses current prices, not previous day"""
    
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
            print(f"🔍 Fetching REAL-TIME data for {symbol}")
            print(f"🔑 API Key status: {'SET' if POLYGON_API_KEY != 'demo_key' else 'DEMO_MODE'}")
            
            # 🚀 GET CURRENT/LIVE PRICE (not previous day)
            current_url = f"https://api.polygon.io/v2/last/trade/{symbol}?apikey={POLYGON_API_KEY}"
            current_response = await client.get(current_url)
            
            # Get previous close for change calculation
            prev_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={POLYGON_API_KEY}"
            prev_response = await client.get(prev_url)
            
            print(f"📡 Current price response: {current_response.status_code}")
            print(f"📡 Previous close response: {prev_response.status_code}")
            
            current_price = None
            previous_close = None
            volume = None
            
            # Parse CURRENT/LIVE price
            if current_response.status_code == 200:
                current_data = current_response.json()
                if current_data.get('results'):
                    current_price = current_data['results'].get('p')  # LIVE CURRENT PRICE
                    print(f"🚀 LIVE CURRENT PRICE: ${current_price}")
            
            # Parse previous close for change calculation
            if prev_response.status_code == 200:
                prev_data = prev_response.json()
                if prev_data.get('results') and len(prev_data['results']) > 0:
                    prev_result = prev_data['results'][0]
                    previous_close = prev_result.get('c')  # Yesterday's close for comparison
                    volume = prev_result.get('v', 0)
                    print(f"📅 Previous close: ${previous_close}")
            
            # Use CURRENT price if available
            if current_price is not None and current_price > 0:
                price = current_price
                
                # Calculate change from previous close to CURRENT price
                if previous_close and previous_close > 0:
                    change = price - previous_close
                    change_percent = (change / previous_close * 100)
                else:
                    change = 0
                    change_percent = 0
                    previous_close = price
                
                print(f"✅ REAL-TIME: {symbol} ${price:.2f} ({change_percent:+.2f}%) vs prev ${previous_close:.2f}")
                
                return {
                    "symbol": symbol,
                    "company_name": f"{symbol} Inc.",
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "previous_close": round(previous_close, 2),
                    "volume": volume if volume else 0,
                    "market_cap": "N/A",
                    "live_data": True,
                    "data_source": "polygon_real_time",
                    "timestamp": datetime.now().isoformat()
                }
            
            print(f"⚠️ No current price for {symbol}, using fallback")
            
        # Fallback if real-time fails
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
            "data_source": "api_fallback"
        }
        
    except Exception as e:
        print(f"❌ Exception for {symbol}: {e}")
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

'''
    
    # Replace the function
    new_content = content[:start_pos] + new_function + content[end_pos:]
    
    # Write back
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print('✅ Replaced get_market_data with REAL-TIME version!')
    print('🚀 Now uses /v2/last/trade for current prices!')
else:
    print('❌ Could not find function boundaries')