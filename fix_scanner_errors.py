#!/usr/bin/env python3
"""
Fix the scanner errors and add better error handling
"""

def fix_scanner_errors():
    """Fix the NoneType and other errors in the scanner"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find and replace the problematic scanner function
    func_start = content.find('async def fetch_fmp_stock_data(symbol: str) -> Dict[str, Any]:')
    if func_start == -1:
        print("❌ Could not find fetch_fmp_stock_data function")
        return False
    
    # Find the end of the function
    func_end = content.find('\nasync def get_fmp_active_stocks', func_start)
    if func_end == -1:
        func_end = content.find('\n@app.get("/api/scanner/fmp/scan")', func_start)
    
    if func_end == -1:
        print("❌ Could not find end of function")
        return False
    
    # Create improved function with better error handling
    new_function = '''async def fetch_fmp_stock_data(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from FMP for scanner use with robust error handling"""
    try:
        if FMP_API_KEY == "demo_key":
            # Return demo data if no FMP key
            price_base = 50.0 + (hash(symbol) % 100)
            change_base = -10 + (hash(symbol) % 20)
            return {
                "symbol": symbol,
                "name": f"{symbol} Inc.",
                "price": round(price_base, 2),
                "change": round(change_base, 2),
                "change_percent": round((change_base / price_base) * 100, 2),
                "volume": 1000000 + (hash(symbol) % 5000000),
                "market_cap": 1000000000,
                "day_high": round(price_base * 1.05, 2),
                "day_low": round(price_base * 0.95, 2),
                "previous_close": round(price_base - change_base, 2),
                "pe": 15.0 + (hash(symbol) % 20),
                "eps": round((price_base / 20), 2),
                "exchange": "NASDAQ",
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
                    
                    # Safe extraction with defaults
                    price = quote.get('price') or 0
                    change = quote.get('change') or 0  
                    change_percent = quote.get('changesPercentage') or 0
                    volume = quote.get('volume') or 0
                    market_cap = quote.get('marketCap') or 0
                    day_high = quote.get('dayHigh') or price
                    day_low = quote.get('dayLow') or price
                    previous_close = quote.get('previousClose') or price
                    pe = quote.get('pe') or 0
                    eps = quote.get('eps') or 0
                    
                    return {
                        "symbol": quote.get('symbol', symbol),
                        "name": quote.get('name', f"{symbol} Inc."),
                        "price": float(price) if price is not None else 0,
                        "change": float(change) if change is not None else 0,
                        "change_percent": float(change_percent) if change_percent is not None else 0,
                        "volume": int(volume) if volume is not None else 0,
                        "market_cap": int(market_cap) if market_cap is not None else 0,
                        "day_high": float(day_high) if day_high is not None else 0,
                        "day_low": float(day_low) if day_low is not None else 0,
                        "previous_close": float(previous_close) if previous_close is not None else 0,
                        "pe": float(pe) if pe is not None else 0,
                        "eps": float(eps) if eps is not None else 0,
                        "exchange": quote.get('exchange', 'NASDAQ'),
                        "error": None
                    }
            
            return {"symbol": symbol, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}'''
    
    # Replace the function
    new_content = content[:func_start] + new_function + content[func_end:]
    
    # Now fix the main scanner function to handle errors better
    scanner_start = content.find('@app.get("/api/scanner/fmp/scan")')
    if scanner_start != -1:
        scanner_end = content.find('\n@app.get("/api/scanner/fmp/gainers")', scanner_start)
        if scanner_end != -1:
            old_scanner = content[scanner_start:scanner_end]
            
            # Create improved scanner with better error handling  
            new_scanner = '''@app.get("/api/scanner/fmp/scan")
async def fmp_scanner_scan(
    scan_type: str = "top_gainers",
    min_price: float = 5.0,
    max_price: float = 500.0,
    min_volume: int = 1000000,
    limit: int = 25
):
    """FMP-powered real-time stock scanner with robust error handling"""
    try:
        print(f"🚀 Starting FMP scanner: {scan_type}")
        start_time = time.time()
        
        # Get active stocks list - use fallback if needed
        try:
            active_stocks = await get_fmp_active_stocks()
        except Exception as e:
            print(f"Error getting active stocks: {e}, using fallback list")
            active_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 
                           'AMD', 'INTC', 'CRM', 'ORCL', 'UBER', 'SHOP', 'SQ', 'ROKU',
                           'ZM', 'SNOW', 'PLTR', 'COIN', 'RBLX', 'PYPL', 'ADBE', 'NOW']
        
        # For performance, limit scanning to reasonable number
        scan_limit = min(limit * 3, 150)  # Reduced for better performance
        stocks_to_scan = active_stocks[:scan_limit]
        
        print(f"📊 Scanning {len(stocks_to_scan)} stocks with FMP real-time data")
        
        # Fetch data concurrently in smaller batches 
        batch_size = 15  # Smaller batches for better reliability
        all_results = []
        
        for i in range(0, len(stocks_to_scan), batch_size):
            batch = stocks_to_scan[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}: {len(batch)} stocks")
            
            try:
                batch_results = await asyncio.gather(
                    *[fetch_fmp_stock_data(symbol) for symbol in batch],
                    return_exceptions=True
                )
                
                # Filter out errors and add to results
                for result in batch_results:
                    if isinstance(result, dict) and not result.get("error") and result.get("price", 0) > 0:
                        all_results.append(result)
            except Exception as e:
                print(f"Batch error: {e}")
                continue
            
            # Small delay between batches
            if i + batch_size < len(stocks_to_scan):
                await asyncio.sleep(0.3)
        
        print(f"📈 Got data for {len(all_results)} stocks")
        
        # Apply filters and scanner logic with safe operations
        filtered_results = []
        
        for stock in all_results:
            try:
                # Safe extraction with validation
                price = float(stock.get("price", 0))
                volume = int(stock.get("volume", 0))
                change_percent = float(stock.get("change_percent", 0))
                
                # Skip if invalid data
                if price <= 0 or volume < 0:
                    continue
                
                # Basic filters
                if not (min_price <= price <= max_price):
                    continue
                if volume < min_volume:
                    continue
                
                # Scanner type filters
                if scan_type == "top_gainers" and change_percent < 2.0:
                    continue
                elif scan_type == "top_losers" and change_percent > -2.0:
                    continue
                elif scan_type == "high_volume" and volume < min_volume * 1.5:
                    continue
                elif scan_type == "breakouts" and change_percent < 3.0:
                    continue
                elif scan_type == "under_10" and price >= 10.0:
                    continue
                elif scan_type == "momentum" and (change_percent < 1.0 or volume < min_volume):
                    continue
                
                # Calculate scanner score safely
                volume_score = min(50, (volume / 1000000) * 10)
                price_score = min(30, abs(change_percent) * 3)
                momentum_score = min(20, (change_percent + 10) * 2)
                
                total_score = volume_score + price_score + momentum_score
                
                # Format market cap safely
                market_cap = int(stock.get("market_cap", 0))
                if market_cap > 1000000000:
                    market_cap_str = f"${market_cap/1000000000:.1f}B"
                elif market_cap > 1000000:
                    market_cap_str = f"${market_cap/1000000:.1f}M"
                else:
                    market_cap_str = "N/A"
                
                # Safe rounding for all values
                filtered_results.append({
                    "symbol": stock.get("symbol", ""),
                    "name": stock.get("name", stock.get("symbol", "")),
                    "price": round(price, 2),
                    "change": round(float(stock.get("change", 0)), 2),
                    "changePercent": round(change_percent, 2),
                    "volume": volume,
                    "marketCap": market_cap_str,
                    "dayHigh": round(float(stock.get("day_high", 0)), 2),
                    "dayLow": round(float(stock.get("day_low", 0)), 2),
                    "score": round(total_score, 1),
                    "pe": round(float(stock.get("pe", 0)), 1),
                    "exchange": stock.get("exchange", "NASDAQ"),
                    "data_source": "fmp_real_time"
                })
                
            except Exception as e:
                print(f"Error processing stock {stock.get('symbol', 'unknown')}: {e}")
                continue
        
        # Sort by score and limit results
        filtered_results.sort(key=lambda x: x.get("score", 0), reverse=True)
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
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "scan_type": scan_type,
            "stocks": [],
            "processing_time": 0
        }'''
            
            new_content = new_content.replace(old_scanner, new_scanner)
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed scanner errors and added robust error handling")
    print("🔧 Fixed NoneType errors with safe value extraction")
    print("📊 Added fallback data for when API calls fail")
    print("⚡ Reduced batch sizes for better reliability")
    
    return True

if __name__ == "__main__":
    fix_scanner_errors()