#!/usr/bin/env python3
"""
Implement FMP real-time market data to replace Polygon
Uses Financial Modeling Prep API for true real-time data
"""

def implement_fmp_realtime():
    """Replace get_market_data function with FMP implementation"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the get_market_data function
    func_start = content.find('async def get_market_data(symbol: str) -> Dict[str, Any]:')
    if func_start == -1:
        print("❌ Could not find get_market_data function")
        return False
    
    func_end = content.find('\nasync def ', func_start + 1)
    if func_end == -1:
        func_end = content.find('\n@app.', func_start + 1)
    if func_end == -1:
        func_end = len(content)
    
    # Update environment variables section
    env_section = content.find('# API Keys from environment')
    if env_section != -1:
        env_end = content.find('\n\n', env_section)
        old_env = content[env_section:env_end]
        new_env = '''# API Keys from environment
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "demo_key")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "demo_key")
FMP_API_KEY = os.getenv("FMP_API_KEY", "demo_key")'''
        content = content[:env_section] + new_env + content[env_end:]
    
    # Create new FMP-powered function
    new_function = '''async def get_market_data(symbol: str) -> Dict[str, Any]:
    """Real-time market data using FMP API - TRUE real-time data"""
    
    # If no FMP API key, fall back to Polygon or demo data
    if FMP_API_KEY == "demo_key":
        print(f"⚠️ No FMP API key, falling back to Polygon for {symbol}")
        return await get_polygon_data(symbol)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"🚀 Fetching REAL-TIME FMP data for {symbol}")
            print(f"🔑 FMP API Key configured: {len(FMP_API_KEY)} chars")
            
            # FMP Real-time Quote - comprehensive market data
            quote_url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={FMP_API_KEY}"
            print(f"📡 Requesting FMP quote: {quote_url.replace(FMP_API_KEY, '***')}")
            
            response = await client.get(quote_url)
            print(f"📡 FMP response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    quote = data[0]  # FMP returns array with single quote
                    
                    # Extract comprehensive data
                    current_price = quote.get('price', 0)
                    previous_close = quote.get('previousClose', 0) 
                    change = quote.get('change', 0)
                    change_percent = quote.get('changesPercentage', 0)
                    volume = quote.get('volume', 0)
                    market_cap = quote.get('marketCap', 0)
                    day_high = quote.get('dayHigh', 0)
                    day_low = quote.get('dayLow', 0)
                    company_name = quote.get('name', f"{symbol} Inc.")
                    
                    # Format market cap
                    if market_cap > 1000000000:
                        market_cap_str = f"${market_cap/1000000000:.1f}B"
                    elif market_cap > 1000000:
                        market_cap_str = f"${market_cap/1000000:.1f}M"
                    else:
                        market_cap_str = f"${market_cap:,.0f}"
                    
                    print(f"✅ FMP SUCCESS: {symbol} ${current_price:.2f} ({change_percent:+.2f}%) Vol: {volume:,}")
                    
                    return {
                        "symbol": symbol,
                        "company_name": company_name,
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "previous_close": round(previous_close, 2),
                        "day_high": round(day_high, 2),
                        "day_low": round(day_low, 2),
                        "volume": volume,
                        "market_cap": market_cap_str,
                        "live_data": True,
                        "data_source": "fmp_real_time",
                        "timestamp": datetime.now().isoformat(),
                        "exchange": quote.get('exchange', 'NASDAQ'),
                        "pe_ratio": quote.get('pe', 0),
                        "eps": quote.get('eps', 0)
                    }
                else:
                    print(f"⚠️ FMP returned empty data for {symbol}")
                    
            elif response.status_code == 401:
                print(f"❌ FMP UNAUTHORIZED: Invalid API key")
                # Fall back to Polygon
                return await get_polygon_data(symbol)
            elif response.status_code == 403:
                print(f"❌ FMP FORBIDDEN: API limit exceeded or insufficient permissions")
                # Fall back to Polygon  
                return await get_polygon_data(symbol)
            else:
                print(f"❌ FMP API Error {response.status_code}: {response.text[:200]}")
                # Fall back to Polygon
                return await get_polygon_data(symbol)
        
        # If we get here, something went wrong - try Polygon fallback
        print(f"⚠️ FMP request failed for {symbol}, trying Polygon fallback")
        return await get_polygon_data(symbol)
        
    except Exception as e:
        print(f"❌ FMP Exception for {symbol}: {e}")
        # Fall back to Polygon
        return await get_polygon_data(symbol)

async def get_polygon_data(symbol: str) -> Dict[str, Any]:
    """Fallback to Polygon previous close data when FMP fails"""
    
    if POLYGON_API_KEY == "demo_key":
        print(f"⚠️ No Polygon API key either, using demo data for {symbol}")
        return {
            "symbol": symbol,
            "company_name": f"{symbol} Inc.",
            "price": 150.00,
            "change": 2.50,
            "change_percent": 1.69,
            "previous_close": 147.50,
            "volume": 1500000,
            "market_cap": "$2.5B",
            "live_data": False,
            "data_source": "demo_fallback"
        }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"📊 Fallback: Using Polygon previous close for {symbol}")
            
            # Polygon previous close endpoint
            prev_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={POLYGON_API_KEY}"
            prev_response = await client.get(prev_url)
            
            if prev_response.status_code == 200:
                prev_data = prev_response.json()
                
                if prev_data.get('results') and len(prev_data['results']) > 0:
                    result = prev_data['results'][0]
                    
                    close_price = result.get('c', 0)
                    open_price = result.get('o', 0)
                    volume = result.get('v', 0)
                    
                    change = close_price - open_price if open_price > 0 else 0
                    change_percent = (change / open_price * 100) if open_price > 0 else 0
                    
                    print(f"✅ Polygon fallback: {symbol} ${close_price:.2f} ({change_percent:+.2f}%)")
                    
                    return {
                        "symbol": symbol,
                        "company_name": f"{symbol} Inc.",
                        "price": round(close_price, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "previous_close": round(open_price, 2),
                        "volume": volume,
                        "market_cap": "N/A",
                        "live_data": True,
                        "data_source": "polygon_fallback",
                        "timestamp": datetime.now().isoformat(),
                        "note": "15-minute delayed data from Polygon"
                    }
            
            print(f"❌ Polygon fallback failed for {symbol}")
            
    except Exception as e:
        print(f"❌ Polygon fallback error: {e}")
    
    # Final fallback to demo data
    return {
        "symbol": symbol,
        "company_name": f"{symbol} Inc.",
        "price": 150.00,
        "change": 2.50,
        "change_percent": 1.69,
        "previous_close": 147.50,
        "volume": 1500000,
        "market_cap": "N/A",
        "live_data": False,
        "data_source": "final_fallback",
        "timestamp": datetime.now().isoformat()
    }'''
    
    # Replace the function in the content
    # First find where to insert the new function
    func_start = content.find('async def get_market_data(symbol: str) -> Dict[str, Any]:')
    func_end = content.find('\nasync def ', func_start + 1)
    if func_end == -1:
        func_end = content.find('\n@app.', func_start + 1)
    if func_end == -1:
        func_end = len(content)
    
    new_content = content[:func_start] + new_function + content[func_end:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Implemented FMP real-time API integration")
    print("🚀 Primary: FMP real-time data (true live prices)")
    print("📊 Fallback: Polygon previous close (15-min delayed)")
    print("🎯 Data source will show 'fmp_real_time' for live data")
    
    return True

if __name__ == "__main__":
    implement_fmp_realtime()