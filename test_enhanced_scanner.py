#!/usr/bin/env python3
"""Test the enhanced professional scanner"""
import asyncio
from main import scanner_stocks, get_scanner_types, get_sectors

async def test_enhanced_scanner():
    print("🚀 Testing Enhanced Professional Scanner...")
    
    # Test scanner types endpoint
    print("\n📊 Testing Scanner Types API...")
    scanner_types = await get_scanner_types()
    print(f"Available Scanner Types: {scanner_types['total_types']}")
    print(f"Universe Size: {scanner_types['universe_size']:,}")
    
    # Show some scanner types
    for i, (key, info) in enumerate(list(scanner_types['scanner_types'].items())[:5]):
        print(f"  {info['icon']} {info['name']}: {info['description']}")
    
    # Test sectors endpoint  
    print("\n🏢 Testing Sectors API...")
    sectors = await get_sectors()
    print(f"Available Sectors: {sectors['total_sectors']}")
    print(f"Sectors: {', '.join(sectors['sectors'][:8])}")
    
    # Test different scanner types
    print("\n🔍 Testing Scanner Performance...")
    test_scans = [
        ('ALL', 'All Stocks'),
        ('TOP_GAINERS', 'Top Gainers'), 
        ('HIGH_VOLUME', 'High Volume'),
        ('TECH_STOCKS', 'Technology Sector'),
        ('PENNY_STOCKS', 'Penny Stocks')
    ]
    
    for scan_type, name in test_scans:
        print(f"\n📈 Testing {name} scanner...")
        try:
            result = await scanner_stocks(scan_type=scan_type, limit=15, min_volume=100000)
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
            else:
                scanned = result['total_scanned']
                found = result['matches']
                time_taken = result.get('processing_time', 0)
                
                print(f"✅ Scanned: {scanned} | Found: {found} | Time: {time_taken:.2f}s")
                
                if result.get('stocks'):
                    top_2 = result['stocks'][:2]
                    for stock in top_2:
                        symbol = stock['symbol']
                        price = stock['price'] 
                        change = stock['changePercent']
                        sector = stock.get('sector', 'N/A')
                        score = stock.get('score', 0)
                        print(f"   📊 {symbol}: ${price} ({change:+.2f}%) | {sector} | Score: {score:.1f}")
                        
        except Exception as e:
            print(f"❌ Error testing {name}: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_scanner())