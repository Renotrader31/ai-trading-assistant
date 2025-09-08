#!/usr/bin/env python3
"""
Add debug endpoint to see raw scanner data before filtering
"""

def add_scanner_debug():
    """Add endpoint to debug scanner data"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find where to add debug endpoint
    insertion_point = content.find('@app.get("/test-scanner-simple")')
    
    if insertion_point == -1:
        print("❌ Could not find insertion point")
        return False
    
    debug_endpoint = '''@app.get("/debug/scanner-data/{limit}")
async def debug_scanner_data(limit: int = 10):
    """Debug endpoint to see raw scanner data before filtering"""
    try:
        # Get some active stocks
        active_stocks = await get_fmp_active_stocks()
        test_stocks = active_stocks[:limit]
        
        print(f"🔍 Testing {len(test_stocks)} stocks: {test_stocks}")
        
        # Fetch their data
        results = []
        for symbol in test_stocks:
            stock_data = await fetch_fmp_stock_data(symbol)
            if not stock_data.get("error"):
                results.append({
                    "symbol": stock_data.get("symbol"),
                    "price": stock_data.get("price"),
                    "change_percent": stock_data.get("change_percent"),
                    "volume": stock_data.get("volume"),
                    "meets_gainers": stock_data.get("change_percent", 0) >= 0.5,
                    "meets_losers": stock_data.get("change_percent", 0) <= -0.5,
                    "meets_volume": stock_data.get("volume", 0) >= 500000
                })
        
        return {
            "debug": "raw_scanner_data",
            "tested_stocks": test_stocks,
            "results": results,
            "summary": {
                "total_tested": len(results),
                "gainers_0_5": len([r for r in results if r.get("meets_gainers")]),
                "losers_0_5": len([r for r in results if r.get("meets_losers")]),
                "high_volume": len([r for r in results if r.get("meets_volume")])
            }
        }
        
    except Exception as e:
        return {"debug": "error", "error": str(e)}

'''
    
    # Insert the debug endpoint
    new_content = content[:insertion_point] + debug_endpoint + '\n' + content[insertion_point:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added scanner debug endpoint")
    print("🔗 Test URL: /debug/scanner-data/15")
    
    return True

if __name__ == "__main__":
    add_scanner_debug()