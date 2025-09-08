#!/usr/bin/env python3
"""
Real-time API Debug Script for Railway Deployment
This script helps diagnose why the real-time Polygon API is failing
"""

import asyncio
import httpx
import os
import json
from datetime import datetime

async def debug_realtime_api():
    """Debug the exact real-time API issue in Railway"""
    
    print("🔍 REAL-TIME API DEBUG SCRIPT")
    print("=" * 50)
    
    # Check environment variables first
    polygon_key = os.getenv('POLYGON_API_KEY', 'NOT_SET')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', 'NOT_SET')
    
    print(f"📋 Environment Check:")
    print(f"   POLYGON_API_KEY: {'✅ SET' if polygon_key != 'NOT_SET' and polygon_key != 'demo_key' else '❌ MISSING'}")
    print(f"   Key Length: {len(polygon_key)}")
    print(f"   Key Preview: {polygon_key[:8]}..." if len(polygon_key) > 8 else f"   Full Key: {polygon_key}")
    
    if polygon_key in ['NOT_SET', 'demo_key']:
        print("\n❌ PROBLEM IDENTIFIED: Polygon API key is not configured!")
        print("   Please set POLYGON_API_KEY in Railway environment variables")
        return
    
    print(f"\n🔗 Testing Real-Time Endpoints:")
    symbol = "AMZN"
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Test 1: Current price endpoint (/v2/last/trade)
            print(f"\n1️⃣ Testing REAL-TIME endpoint: /v2/last/trade/{symbol}")
            current_url = f"https://api.polygon.io/v2/last/trade/{symbol}?apikey={polygon_key}"
            print(f"   URL: {current_url.replace(polygon_key, '***API_KEY***')}")
            
            current_response = await client.get(current_url)
            print(f"   Status Code: {current_response.status_code}")
            
            if current_response.status_code == 200:
                current_data = current_response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Response Keys: {list(current_data.keys())}")
                
                if current_data.get('results'):
                    current_price = current_data['results'].get('p')
                    timestamp = current_data['results'].get('t')
                    print(f"   🎯 LIVE PRICE: ${current_price}")
                    print(f"   🕐 Timestamp: {timestamp}")
                else:
                    print(f"   ❌ No results in response: {current_data}")
                    
            elif current_response.status_code == 401:
                print(f"   ❌ UNAUTHORIZED - Invalid API Key!")
                print(f"   Response: {current_response.text}")
                return
            elif current_response.status_code == 403:
                print(f"   ❌ FORBIDDEN - API Key lacks permissions for real-time data!")
                print(f"   Response: {current_response.text}")
                return
            else:
                print(f"   ❌ ERROR {current_response.status_code}: {current_response.text}")
            
            # Test 2: Previous close endpoint for comparison (/v2/aggs/ticker/prev)
            print(f"\n2️⃣ Testing PREVIOUS CLOSE endpoint: /v2/aggs/ticker/{symbol}/prev")
            prev_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={polygon_key}"
            prev_response = await client.get(prev_url)
            print(f"   Status Code: {prev_response.status_code}")
            
            if prev_response.status_code == 200:
                prev_data = prev_response.json()
                print(f"   ✅ SUCCESS!")
                if prev_data.get('results') and len(prev_data['results']) > 0:
                    prev_result = prev_data['results'][0]
                    prev_close = prev_result.get('c')
                    volume = prev_result.get('v')
                    print(f"   📅 PREVIOUS CLOSE: ${prev_close}")
                    print(f"   📊 Volume: {volume:,}")
                else:
                    print(f"   ❌ No results in response: {prev_data}")
            else:
                print(f"   ❌ ERROR {prev_response.status_code}: {prev_response.text}")
            
            # Test 3: Test our actual get_market_data function
            print(f"\n3️⃣ Testing OUR get_market_data() function:")
            
            # Import and test the actual function from main.py
            import sys
            sys.path.append('.')
            
            try:
                from main import get_market_data
                result = await get_market_data(symbol)
                print(f"   Function Result: {json.dumps(result, indent=2)}")
                print(f"   Data Source: {result.get('data_source', 'unknown')}")
                print(f"   Live Data: {result.get('live_data', False)}")
                print(f"   Price: ${result.get('price', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Function Error: {e}")
            
    except Exception as e:
        print(f"❌ HTTP Client Error: {e}")
    
    print(f"\n📝 SUMMARY:")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Symbol Tested: {symbol}")
    print(f"   API Key Status: {'CONFIGURED' if polygon_key not in ['NOT_SET', 'demo_key'] else 'MISSING'}")

if __name__ == "__main__":
    print("Starting real-time API debug...")
    asyncio.run(debug_realtime_api())