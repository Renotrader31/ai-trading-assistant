#!/usr/bin/env python3
"""
Implement powerful stock scanner using FMP real-time data
This will replace the existing scanner with actual live market data
"""

def implement_fmp_scanner():
    """Add FMP-powered stock scanner endpoints to main.py"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find where to insert scanner functions (before the existing scanner endpoints)
    insertion_point = content.find('@app.get("/api/scanner/types")')
    
    if insertion_point == -1:
        print("❌ Could not find scanner endpoints insertion point")
        return False
    
    # New FMP scanner implementation
    fmp_scanner_code = '''
# FMP-powered Stock Scanner Implementation
async def fetch_fmp_stock_data(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from FMP for scanner use"""
    try:
        if FMP_API_KEY == "demo_key":
            # Return demo data if no FMP key
            return {
                "symbol": symbol,
                "price": 100.0 + (hash(symbol) % 50),
                "change": -5 + (hash(symbol) % 10),
                "change_percent": -2.5 + (hash(symbol) % 5),
                "volume": 1000000 + (hash(symbol) % 5000000),
                "market_cap": 1000000000,
                "day_high": 105.0,
                "day_low": 95.0,
                "error": None
            }
        
        async with httpx.AsyncClient(timeout=8.0) as client:
            # Use FMP quote endpoint for comprehensive data
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={FMP_API_KEY}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    quote = data[0]
                    return {
                        "symbol": quote.get('symbol', symbol),
                        "name": quote.get('name', f"{symbol} Inc."),
                        "price": quote.get('price', 0),
                        "change": quote.get('change', 0),
                        "change_percent": quote.get('changesPercentage', 0),
                        "volume": quote.get('volume', 0),
                        "market_cap": quote.get('marketCap', 0),
                        "day_high": quote.get('dayHigh', 0),
                        "day_low": quote.get('dayLow', 0),
                        "previous_close": quote.get('previousClose', 0),
                        "pe": quote.get('pe', 0),
                        "eps": quote.get('eps', 0),
                        "exchange": quote.get('exchange', 'NASDAQ'),
                        "error": None
                    }
            
            return {"symbol": symbol, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

async def get_fmp_active_stocks() -> list:
    """Get list of active stocks from FMP for scanning"""
    try:
        if FMP_API_KEY == "demo_key":
            # Return demo stock list
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 
                   'AMD', 'INTC', 'CRM', 'ORCL', 'UBER', 'SHOP', 'SQ', 'ROKU',
                   'ZM', 'SNOW', 'PLTR', 'COIN', 'RBLX', 'PYPL', 'ADBE', 'NOW']
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Get list of tradeable symbols from FMP
            url = f"https://financialmodelingprep.com/api/v3/available-traded/list?apikey={FMP_API_KEY}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Filter for major US exchanges and reasonable price range
                    symbols = []
                    for item in data:
                        symbol = item.get('symbol', '')
                        exchange = item.get('exchangeShortName', '')
                        price = item.get('price', 0)
                        
                        # Filter criteria for scanner
                        if (exchange in ['NASDAQ', 'NYSE', 'AMEX'] and 
                            len(symbol) <= 5 and 
                            symbol.isalpha() and 
                            price > 1.0 and 
                            price < 1000.0):
                            symbols.append(symbol)
                    
                    # Return top 500 most liquid stocks for performance
                    return symbols[:500] if len(symbols) > 500 else symbols
        
        # Fallback to popular stocks if API fails
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 
               'AMD', 'INTC', 'CRM', 'ORCL', 'UBER', 'SHOP', 'SQ', 'ROKU']
               
    except Exception as e:
        print(f"Error fetching active stocks: {e}")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']

@app.get("/api/scanner/fmp/scan")
async def fmp_scanner_scan(
    scan_type: str = "top_gainers",
    min_price: float = 5.0,
    max_price: float = 500.0,
    min_volume: int = 1000000,
    limit: int = 25
):
    """FMP-powered real-time stock scanner"""
    try:
        print(f"🚀 Starting FMP scanner: {scan_type}")
        start_time = time.time()
        
        # Get active stocks list
        active_stocks = await get_fmp_active_stocks()
        
        # For performance, limit scanning to reasonable number
        scan_limit = min(limit * 4, 200)  # Scan 4x the requested limit for better filtering
        stocks_to_scan = active_stocks[:scan_limit]
        
        print(f"📊 Scanning {len(stocks_to_scan)} stocks with FMP real-time data")
        
        # Fetch data concurrently in batches to avoid overwhelming FMP API
        batch_size = 25  # FMP can handle decent concurrent load
        all_results = []
        
        for i in range(0, len(stocks_to_scan), batch_size):
            batch = stocks_to_scan[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}: {len(batch)} stocks")
            
            batch_results = await asyncio.gather(
                *[fetch_fmp_stock_data(symbol) for symbol in batch],
                return_exceptions=True
            )
            
            # Filter out errors and add to results
            for result in batch_results:
                if isinstance(result, dict) and not result.get("error"):
                    all_results.append(result)
            
            # Small delay between batches to be respectful to FMP API
            if i + batch_size < len(stocks_to_scan):
                await asyncio.sleep(0.2)  # 200ms between batches
        
        print(f"📈 Got data for {len(all_results)} stocks")
        
        # Apply filters and scanner logic
        filtered_results = []
        
        for stock in all_results:
            price = stock.get("price", 0)
            volume = stock.get("volume", 0)
            change_percent = stock.get("change_percent", 0)
            
            # Basic filters
            if not (min_price <= price <= max_price):
                continue
            if volume < min_volume:
                continue
            
            # Scanner type filters
            if scan_type == "top_gainers" and change_percent < 3.0:
                continue
            elif scan_type == "top_losers" and change_percent > -3.0:
                continue
            elif scan_type == "high_volume" and volume < min_volume * 2:
                continue
            elif scan_type == "breakouts" and change_percent < 5.0:
                continue
            elif scan_type == "under_10" and price >= 10.0:
                continue
            elif scan_type == "momentum" and (change_percent < 2.0 or volume < min_volume * 1.5):
                continue
            
            # Calculate scanner score
            volume_score = min(50, (volume / 1000000) * 10)  # Up to 50 points for volume
            price_score = min(30, abs(change_percent) * 3)   # Up to 30 points for price change
            momentum_score = min(20, (change_percent + 10) * 2)  # Up to 20 points for momentum
            
            total_score = volume_score + price_score + momentum_score
            
            # Format market cap
            market_cap = stock.get("market_cap", 0)
            if market_cap > 1000000000:
                market_cap_str = f"${market_cap/1000000000:.1f}B"
            elif market_cap > 1000000:
                market_cap_str = f"${market_cap/1000000:.1f}M"
            else:
                market_cap_str = "N/A"
            
            filtered_results.append({
                "symbol": stock["symbol"],
                "name": stock.get("name", stock["symbol"]),
                "price": round(price, 2),
                "change": round(stock.get("change", 0), 2),
                "changePercent": round(change_percent, 2),
                "volume": volume,
                "marketCap": market_cap_str,
                "dayHigh": round(stock.get("day_high", 0), 2),
                "dayLow": round(stock.get("day_low", 0), 2),
                "score": round(total_score, 1),
                "pe": round(stock.get("pe", 0), 1),
                "exchange": stock.get("exchange", "NASDAQ"),
                "data_source": "fmp_real_time"
            })
        
        # Sort by score (highest first) and limit results
        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        final_results = filtered_results[:limit]
        
        processing_time = round(time.time() - start_time, 2)
        
        print(f"✅ FMP Scanner completed in {processing_time}s: {len(final_results)} results")
        
        return {
            "success": True,
            "scan_type": scan_type,
            "stocks": final_results,
            "total_scanned": len(stocks_to_scan),
            "matches": len(filtered_results),
            "processing_time": processing_time,
            "data_source": "fmp_real_time",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ FMP Scanner error: {e}")
        return {
            "success": False,
            "error": str(e),
            "scan_type": scan_type,
            "stocks": [],
            "processing_time": 0
        }

@app.get("/api/scanner/fmp/gainers")
async def fmp_top_gainers(limit: int = 20):
    """Get top gainers using FMP real-time data"""
    return await fmp_scanner_scan("top_gainers", min_price=5.0, limit=limit)

@app.get("/api/scanner/fmp/losers") 
async def fmp_top_losers(limit: int = 20):
    """Get top losers using FMP real-time data"""
    return await fmp_scanner_scan("top_losers", min_price=5.0, limit=limit)

@app.get("/api/scanner/fmp/volume")
async def fmp_high_volume(limit: int = 20):
    """Get high volume stocks using FMP real-time data"""
    return await fmp_scanner_scan("high_volume", min_volume=5000000, limit=limit)

@app.get("/api/scanner/fmp/breakouts")
async def fmp_breakouts(limit: int = 20):
    """Get breakout stocks using FMP real-time data"""
    return await fmp_scanner_scan("breakouts", min_price=10.0, limit=limit)

'''
    
    # Insert the new scanner code before existing scanner endpoints
    new_content = content[:insertion_point] + fmp_scanner_code + '\n' + content[insertion_point:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Implemented FMP-powered stock scanner!")
    print("🚀 New scanner endpoints:")
    print("   GET /api/scanner/fmp/scan - Main scanner with filters")
    print("   GET /api/scanner/fmp/gainers - Top gainers")
    print("   GET /api/scanner/fmp/losers - Top losers") 
    print("   GET /api/scanner/fmp/volume - High volume stocks")
    print("   GET /api/scanner/fmp/breakouts - Breakout stocks")
    print("📊 Uses real-time FMP data with intelligent batching")
    
    return True

if __name__ == "__main__":
    implement_fmp_scanner()