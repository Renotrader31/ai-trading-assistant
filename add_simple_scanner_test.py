#!/usr/bin/env python3
"""
Add a simple scanner test endpoint to verify FMP functionality
"""

def add_simple_scanner_test():
    """Add a simple test endpoint for the scanner"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find where to insert the test endpoint (before existing scanner endpoints)
    insertion_point = content.find('@app.get("/api/scanner/fmp/scan")')
    
    if insertion_point == -1:
        print("❌ Could not find insertion point")
        return False
    
    # Simple test endpoint
    test_endpoint = '''@app.get("/test-scanner-simple")
async def test_scanner_simple():
    """Simple test to verify scanner functionality"""
    try:
        # Test a few stocks with FMP
        test_symbols = ["AAPL", "MSFT", "GOOGL"]
        results = []
        
        for symbol in test_symbols:
            try:
                stock_data = await fetch_fmp_stock_data(symbol)
                if not stock_data.get("error"):
                    results.append(stock_data)
            except Exception as e:
                results.append({"symbol": symbol, "error": str(e)})
        
        return {
            "test": "scanner_functionality",
            "fmp_api_key": "SET" if FMP_API_KEY != "demo_key" else "MISSING",
            "results": results,
            "success": len(results) > 0
        }
    except Exception as e:
        return {
            "test": "scanner_functionality", 
            "error": str(e),
            "success": False
        }

'''
    
    # Insert the test endpoint
    new_content = content[:insertion_point] + test_endpoint + '\n' + content[insertion_point:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added simple scanner test endpoint")
    print("🔗 Test URL: /test-scanner-simple")
    
    return True

if __name__ == "__main__":
    add_simple_scanner_test()