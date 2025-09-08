#!/usr/bin/env python3
"""
Add a simple debug endpoint that's guaranteed to work
This will help verify deployment is working
"""

def add_simple_debug_endpoint():
    """Add a simple debug endpoint to main.py"""
    
    # Read the current main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find where to insert (before existing debug endpoints)
    insertion_point = content.find('@app.get("/debug/env")')
    
    if insertion_point == -1:
        print("❌ Could not find insertion point in main.py")
        return False
    
    # Simple debug endpoint
    simple_debug = '''@app.get("/simple-debug")
async def simple_debug():
    """Simple debug endpoint to test deployment"""
    import os
    from datetime import datetime
    
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "deployment_working": True,
        "polygon_key_status": "SET" if os.getenv("POLYGON_API_KEY", "demo_key") != "demo_key" else "MISSING",
        "message": "If you can see this, the deployment is working!"
    }

@app.get("/test-realtime/{symbol}")
async def test_realtime_simple(symbol: str):
    """Simplified real-time test that's easier to debug"""
    import os
    
    polygon_key = os.getenv("POLYGON_API_KEY", "demo_key") 
    
    if polygon_key == "demo_key":
        return {
            "error": "Polygon API key not configured",
            "symbol": symbol,
            "key_status": "MISSING"
        }
    
    try:
        # Test the function directly
        result = await get_market_data(symbol)
        return {
            "success": True,
            "symbol": symbol,
            "result": result,
            "data_source": result.get("data_source"),
            "is_live": result.get("live_data", False)
        }
    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol,
            "success": False
        }

'''
    
    # Insert the new endpoint
    new_content = content[:insertion_point] + simple_debug + '\n' + content[insertion_point:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added simple debug endpoints to main.py")
    print("🔗 New endpoints:")
    print("   GET /simple-debug - Basic deployment test")
    print("   GET /test-realtime/{symbol} - Simplified real-time test")
    
    return True

if __name__ == "__main__":
    add_simple_debug_endpoint()