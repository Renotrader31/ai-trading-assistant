import os
import asyncio
import httpx

async def test_polygon_api():
    # Check if API key is set
    api_key = os.environ.get('POLYGON_API_KEY', 'not_set')
    print(f'API Key status: {"SET" if api_key != "not_set" and api_key != "demo_key" else "NOT SET"}')
    print(f'API Key length: {len(api_key) if api_key != "not_set" else 0}')
    
    if api_key == 'not_set' or api_key == 'demo_key':
        print('❌ No Polygon API key found!')
        return
    
    # Test the actual API call
    symbol = 'AMZN'
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={api_key}'
            print(f'Testing URL: {url[:60]}...')
            
            response = await client.get(url)
            print(f'Response status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'Response data keys: {list(data.keys())}')
                
                if data.get('results'):
                    result = data['results'][0]
                    print(f'Results keys: {list(result.keys())}')
                    print(f'Close price (c): {result.get("c")}')
                    print(f'Open price (o): {result.get("o")}')
                    print(f'Volume (v): {result.get("v")}')
                    print(f'✅ SUCCESS: Real AMZN price is ${result.get("c")}')
                else:
                    print('❌ No results in response')
                    print(f'Full response: {data}')
            else:
                print(f'❌ API Error: {response.status_code}')
                print(f'Error response: {response.text}')
                
    except Exception as e:
        print(f'❌ Exception: {e}')

if __name__ == "__main__":
    asyncio.run(test_polygon_api())