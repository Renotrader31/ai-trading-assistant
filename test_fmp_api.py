#!/usr/bin/env python3
"""
Test FMP (Financial Modeling Prep) API for real-time data
"""

import asyncio
import httpx
import json

async def test_fmp_api():
    """Test FMP API endpoints for real-time data"""
    
    # Your FMP API key
    fmp_key = "m2XfxOS0sZxs6hLEY5yRzUgDyp5Dur4V"
    symbol = "AMZN"
    
    print("🔍 Testing FMP API for Real-Time Data")
    print("=" * 50)
    print(f"🔑 API Key: {fmp_key[:12]}...")
    print(f"📊 Testing Symbol: {symbol}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            
            # Test 1: Real-time price quote
            print(f"\n1️⃣ Testing Real-Time Quote:")
            quote_url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={fmp_key}"
            print(f"   URL: {quote_url.replace(fmp_key, '***')}")
            
            quote_response = await client.get(quote_url)
            print(f"   Status: {quote_response.status_code}")
            
            if quote_response.status_code == 200:
                quote_data = quote_response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Data: {json.dumps(quote_data, indent=2)}")
            else:
                print(f"   ❌ ERROR: {quote_response.text}")
            
            # Test 2: Real-time price (alternative endpoint)
            print(f"\n2️⃣ Testing Real-Time Price:")
            price_url = f"https://financialmodelingprep.com/api/v3/stock/real-time-price/{symbol}?apikey={fmp_key}"
            print(f"   URL: {price_url.replace(fmp_key, '***')}")
            
            price_response = await client.get(price_url)
            print(f"   Status: {price_response.status_code}")
            
            if price_response.status_code == 200:
                price_data = price_response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Data: {json.dumps(price_data, indent=2)}")
            else:
                print(f"   ❌ ERROR: {price_response.text}")
            
            # Test 3: Historical intraday (for recent data)
            print(f"\n3️⃣ Testing Intraday Data:")
            intraday_url = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{symbol}?apikey={fmp_key}"
            print(f"   URL: {intraday_url.replace(fmp_key, '***')}")
            
            intraday_response = await client.get(intraday_url)
            print(f"   Status: {intraday_response.status_code}")
            
            if intraday_response.status_code == 200:
                intraday_data = intraday_response.json()
                print(f"   ✅ SUCCESS!")
                if isinstance(intraday_data, list) and len(intraday_data) > 0:
                    print(f"   Latest data: {json.dumps(intraday_data[0], indent=2)}")
                    print(f"   Data points: {len(intraday_data)}")
                else:
                    print(f"   Data: {json.dumps(intraday_data, indent=2)}")
            else:
                print(f"   ❌ ERROR: {intraday_response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print(f"\n📝 Summary:")
    print(f"   FMP API provides multiple endpoints for market data")
    print(f"   Will use the best performing endpoint for real-time data")

if __name__ == "__main__":
    asyncio.run(test_fmp_api())