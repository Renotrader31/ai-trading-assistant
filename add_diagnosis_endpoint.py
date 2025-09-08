#!/usr/bin/env python3
"""
Script to add a diagnosis endpoint to main.py for debugging real-time API issues
This endpoint will help identify why real-time data is failing
"""

def add_diagnosis_endpoint():
    """Add a comprehensive diagnosis endpoint to main.py"""
    
    # Read the current main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the insertion point (before the WebSocket endpoint)
    insertion_point = content.find('@app.websocket("/ws")')
    
    if insertion_point == -1:
        print("❌ Could not find insertion point in main.py")
        return False
    
    # The new diagnosis endpoint
    diagnosis_endpoint = '''@app.get("/diagnosis/realtime/{symbol}")
async def diagnose_realtime_api(symbol: str = "AMZN"):
    """
    Comprehensive diagnosis of real-time API issue
    This endpoint tests every step of the real-time data pipeline
    """
    import os
    import traceback
    
    diagnosis = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "steps": [],
        "errors": [],
        "environment": {},
        "api_tests": {},
        "function_test": {}
    }
    
    # Step 1: Environment check
    diagnosis["steps"].append("Checking environment variables")
    polygon_key = os.getenv('POLYGON_API_KEY', 'NOT_SET')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', 'NOT_SET')
    
    diagnosis["environment"] = {
        "polygon_api_key_status": "SET" if polygon_key not in ['NOT_SET', 'demo_key'] else "MISSING",
        "polygon_key_length": len(polygon_key),
        "polygon_key_preview": f"{polygon_key[:8]}..." if len(polygon_key) > 8 else polygon_key,
        "anthropic_key_status": "SET" if anthropic_key not in ['NOT_SET', 'demo_key'] else "MISSING",
        "POLYGON_API_KEY_global": POLYGON_API_KEY,
        "keys_match": polygon_key == POLYGON_API_KEY
    }
    
    if polygon_key in ['NOT_SET', 'demo_key']:
        diagnosis["errors"].append("Polygon API key not configured in environment")
        return diagnosis
    
    # Step 2: Test real-time API endpoints directly
    diagnosis["steps"].append("Testing Polygon API endpoints")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test current price endpoint
            current_url = f"https://api.polygon.io/v2/last/trade/{symbol}?apikey={polygon_key}"
            current_response = await client.get(current_url)
            
            diagnosis["api_tests"]["current_price"] = {
                "url_template": f"/v2/last/trade/{symbol}",
                "status_code": current_response.status_code,
                "success": current_response.status_code == 200
            }
            
            if current_response.status_code == 200:
                current_data = current_response.json()
                diagnosis["api_tests"]["current_price"]["data"] = current_data
                if current_data.get('results'):
                    current_price = current_data['results'].get('p')
                    diagnosis["api_tests"]["current_price"]["live_price"] = current_price
                else:
                    diagnosis["errors"].append("Real-time endpoint returned no results")
            elif current_response.status_code == 401:
                diagnosis["errors"].append("Real-time API: Unauthorized - check API key")
            elif current_response.status_code == 403:
                diagnosis["errors"].append("Real-time API: Forbidden - API key lacks real-time permissions")
            else:
                diagnosis["errors"].append(f"Real-time API: HTTP {current_response.status_code} - {current_response.text[:100]}")
            
            # Test previous close endpoint
            prev_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={polygon_key}"
            prev_response = await client.get(prev_url)
            
            diagnosis["api_tests"]["previous_close"] = {
                "url_template": f"/v2/aggs/ticker/{symbol}/prev",
                "status_code": prev_response.status_code,
                "success": prev_response.status_code == 200
            }
            
            if prev_response.status_code == 200:
                prev_data = prev_response.json()
                diagnosis["api_tests"]["previous_close"]["data"] = prev_data
                if prev_data.get('results') and len(prev_data['results']) > 0:
                    prev_result = prev_data['results'][0]
                    diagnosis["api_tests"]["previous_close"]["close_price"] = prev_result.get('c')
                    diagnosis["api_tests"]["previous_close"]["volume"] = prev_result.get('v')
            
    except Exception as e:
        diagnosis["errors"].append(f"HTTP client error: {str(e)}")
        diagnosis["api_tests"]["exception"] = str(e)
    
    # Step 3: Test our get_market_data function
    diagnosis["steps"].append("Testing get_market_data function")
    
    try:
        result = await get_market_data(symbol)
        diagnosis["function_test"] = {
            "success": True,
            "result": result,
            "data_source": result.get("data_source"),
            "live_data_flag": result.get("live_data"),
            "price": result.get("price"),
            "is_fallback": result.get("data_source") in ["api_fallback", "error_fallback", "demo"]
        }
        
        # Identify the specific issue
        if diagnosis["function_test"]["is_fallback"]:
            diagnosis["errors"].append(f"get_market_data is using fallback data source: {result.get('data_source')}")
        
    except Exception as e:
        diagnosis["function_test"] = {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        diagnosis["errors"].append(f"get_market_data function error: {str(e)}")
    
    # Step 4: Generate recommendations
    diagnosis["recommendations"] = []
    
    if diagnosis["environment"]["polygon_api_key_status"] == "MISSING":
        diagnosis["recommendations"].append("Set POLYGON_API_KEY environment variable in Railway")
    
    if diagnosis["api_tests"].get("current_price", {}).get("status_code") == 403:
        diagnosis["recommendations"].append("Upgrade Polygon API plan to include real-time data access")
    
    if diagnosis["api_tests"].get("current_price", {}).get("status_code") == 401:
        diagnosis["recommendations"].append("Verify Polygon API key is valid and properly formatted")
    
    if diagnosis["function_test"].get("is_fallback"):
        diagnosis["recommendations"].append("Check get_market_data function logic for proper error handling")
    
    diagnosis["diagnosis_complete"] = True
    return diagnosis

'''
    
    # Insert the new endpoint
    new_content = content[:insertion_point] + diagnosis_endpoint + '\n\n' + content[insertion_point:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added diagnosis endpoint to main.py")
    print("🔗 New endpoint: GET /diagnosis/realtime/{symbol}")
    print("📝 This endpoint will help identify the exact real-time API issue")
    
    return True

if __name__ == "__main__":
    add_diagnosis_endpoint()