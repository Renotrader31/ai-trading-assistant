#!/usr/bin/env python3
"""
Add "Scan by Score" functionality - find stocks above certain score thresholds
"""

def add_score_scanner():
    """Add score-based scanner endpoints and functionality"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find where to add new scanner endpoints (before the existing ones)
    insertion_point = content.find('@app.get("/api/scanner/fmp/gainers")')
    
    if insertion_point == -1:
        print("❌ Could not find insertion point")
        return False
    
    # New score-based scanner endpoints
    score_scanners = '''@app.get("/api/scanner/fmp/score/{min_score}")
async def fmp_scan_by_score(min_score: int = 70, limit: int = 25):
    """Scan for stocks above a specific score threshold - PREMIUM OPPORTUNITIES"""
    try:
        print(f"🎯 Score Scanner: Finding stocks with score >= {min_score}")
        start_time = time.time()
        
        # Get a larger pool to find high-scoring stocks
        active_stocks = await get_fmp_active_stocks()
        scan_pool = active_stocks[:200]  # Larger pool for better results
        
        # Fetch data in batches
        batch_size = 20
        all_results = []
        
        for i in range(0, len(scan_pool), batch_size):
            batch = scan_pool[i:i + batch_size]
            try:
                batch_results = await asyncio.gather(
                    *[fetch_fmp_stock_data(symbol) for symbol in batch],
                    return_exceptions=True
                )
                
                for result in batch_results:
                    if isinstance(result, dict) and not result.get("error") and result.get("price", 0) > 0:
                        all_results.append(result)
            except Exception as e:
                print(f"Batch error in score scanner: {e}")
                continue
            
            await asyncio.sleep(0.2)  # Rate limiting
        
        print(f"📊 Score scanner got data for {len(all_results)} stocks")
        
        # Calculate scores and filter by minimum score
        scored_results = []
        
        for stock in all_results:
            try:
                price = float(stock.get("price", 0))
                volume = int(stock.get("volume", 0))
                change_percent = float(stock.get("change_percent", 0))
                
                if price <= 0 or volume < 100000:  # Basic validation
                    continue
                
                # Calculate the same score as main scanner
                volume_score = min(50, (volume / 1000000) * 10)
                price_score = min(30, abs(change_percent) * 3)
                momentum_score = min(20, (change_percent + 10) * 2)
                total_score = volume_score + price_score + momentum_score
                
                # Only include if meets score threshold
                if total_score >= min_score:
                    # Format market cap
                    market_cap = int(stock.get("market_cap", 0))
                    if market_cap > 1000000000:
                        market_cap_str = f"${market_cap/1000000000:.1f}B"
                    elif market_cap > 1000000:
                        market_cap_str = f"${market_cap/1000000:.1f}M"
                    else:
                        market_cap_str = "N/A"
                    
                    scored_results.append({
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
                        "data_source": "fmp_score_scanner",
                        "score_breakdown": {
                            "volume_score": round(volume_score, 1),
                            "price_score": round(price_score, 1), 
                            "momentum_score": round(momentum_score, 1)
                        }
                    })
                    
            except Exception as e:
                print(f"Error scoring stock {stock.get('symbol', 'unknown')}: {e}")
                continue
        
        # Sort by score (highest first) and limit
        scored_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        final_results = scored_results[:limit]
        
        processing_time = round(time.time() - start_time, 2)
        
        print(f"🎯 Score Scanner found {len(final_results)} stocks with score >= {min_score}")
        
        return {
            "success": True,
            "scan_type": f"score_above_{min_score}",
            "min_score_threshold": min_score,
            "stocks": final_results,
            "total_scanned": len(scan_pool),
            "matches": len(scored_results),
            "processing_time": processing_time,
            "data_source": "fmp_score_scanner",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Score Scanner error: {e}")
        return {
            "success": False,
            "error": str(e),
            "scan_type": f"score_above_{min_score}",
            "stocks": []
        }

@app.get("/api/scanner/fmp/premium")
async def fmp_premium_opportunities(limit: int = 20):
    """Find premium opportunities (score 80+) - HIGHEST QUALITY"""
    return await fmp_scan_by_score(80, limit)

@app.get("/api/scanner/fmp/elite") 
async def fmp_elite_opportunities(limit: int = 15):
    """Find elite opportunities (score 90+) - EXCEPTIONAL QUALITY"""
    return await fmp_scan_by_score(90, limit)

@app.get("/api/scanner/fmp/legendary")
async def fmp_legendary_opportunities(limit: int = 10):
    """Find legendary opportunities (score 95+) - ULTRA RARE"""
    return await fmp_scan_by_score(95, limit)

'''
    
    # Insert the new endpoints
    new_content = content[:insertion_point] + score_scanners + '\n' + content[insertion_point:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added Score-Based Scanner functionality!")
    print("🎯 New scanner endpoints:")
    print("   /api/scanner/fmp/score/{min_score} - Custom score threshold")
    print("   /api/scanner/fmp/premium - Score 80+ (Premium opportunities)")
    print("   /api/scanner/fmp/elite - Score 90+ (Elite opportunities)")
    print("   /api/scanner/fmp/legendary - Score 95+ (Legendary opportunities)")
    print("")
    print("🔥 Examples:")
    print("   /api/scanner/fmp/score/75 - Find stocks scoring 75+")
    print("   /api/scanner/fmp/premium - Find the highest quality setups")
    print("   /api/scanner/fmp/legendary - Find once-in-a-lifetime opportunities!")
    
    return True

if __name__ == "__main__":
    add_score_scanner()