#!/usr/bin/env python3
import asyncio
import time
from main import scanner_stocks, fetch_stock_data_safely

async def test_scanner_performance():
    print("🧪 Testing optimized scanner performance...")
    
    start_time = time.time()
    
    # Test the scanner endpoint
    result = await scanner_stocks(
        min_price=10.0, 
        max_price=1000.0, 
        min_volume=1000000, 
        scan_type="ALL"
    )
    
    total_time = time.time() - start_time
    
    print(f"✅ Scanner completed in {total_time:.2f} seconds")
    print(f"📊 Scanned {result.get('total_scanned', 0)} stocks, found {result.get('matches', 0)} matches")
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return False
    
    if result.get('stocks'):
        print("📈 Sample results:")
        for stock in result['stocks'][:3]:
            print(f"  {stock['symbol']}: ${stock['price']} ({stock['changePercent']:+.2f}%)")
    
    # Test should complete in under 10 seconds with concurrency
    if total_time < 10:
        print(f"🎉 Performance test PASSED! Completed in {total_time:.2f}s (target: <10s)")
        return True
    else:
        print(f"⚠️ Performance test SLOW: {total_time:.2f}s (target: <10s)")
        return False

async def test_individual_fetch():
    print("\n🧪 Testing individual stock data fetch...")
    
    start_time = time.time()
    result = await fetch_stock_data_safely('AAPL')
    fetch_time = time.time() - start_time
    
    print(f"✅ Individual fetch completed in {fetch_time:.2f} seconds")
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return False
    else:
        print(f"📈 AAPL: ${result.get('price', 'N/A')}")
        return True

if __name__ == "__main__":
    async def run_tests():
        print("🚀 Starting performance tests...\n")
        
        # Test individual fetch first
        individual_success = await test_individual_fetch()
        
        # Test full scanner
        scanner_success = await test_scanner_performance()
        
        if individual_success and scanner_success:
            print("\n✅ All tests PASSED! WebSocket performance should be restored.")
        else:
            print("\n❌ Some tests FAILED. WebSocket issues may persist.")
    
    asyncio.run(run_tests())