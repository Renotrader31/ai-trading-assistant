#!/usr/bin/env python3
"""
Adjust scanner filters to be more realistic for current market conditions
The filters are currently too strict, resulting in 0 matches
"""

def adjust_scanner_filters():
    """Make scanner filters more realistic to get actual results"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the scanner filter section
    filter_start = content.find('# Scanner type filters')
    if filter_start == -1:
        filter_start = content.find('if scan_type == "top_gainers" and change_percent < 2.0:')
    
    if filter_start == -1:
        print("❌ Could not find scanner filters")
        return False
    
    # Find the end of the filter section
    filter_end = content.find('# Calculate scanner score safely', filter_start)
    
    if filter_end == -1:
        print("❌ Could not find end of filters")
        return False
    
    # Replace with more realistic filters
    new_filters = '''                # Scanner type filters - ADJUSTED FOR REAL MARKET CONDITIONS
                if scan_type == "top_gainers" and change_percent < 0.5:  # Lowered from 2.0% to 0.5%
                    continue
                elif scan_type == "top_losers" and change_percent > -0.5:  # Lowered from -2.0% to -0.5%
                    continue
                elif scan_type == "high_volume" and volume < min_volume * 0.8:  # Lowered from 1.5x to 0.8x
                    continue
                elif scan_type == "breakouts" and change_percent < 1.5:  # Lowered from 3.0% to 1.5%
                    continue
                elif scan_type == "under_10" and price >= 10.0:
                    continue
                elif scan_type == "momentum" and (change_percent < 0.3 or volume < min_volume * 0.5):  # Much more lenient
                    continue
                
                '''
    
    # Find the exact text to replace
    old_filter_section = content[filter_start:filter_end]
    new_content = content.replace(old_filter_section, new_filters)
    
    # Also update the /api/scanner/fmp/gainers endpoint to be more lenient
    gainers_start = content.find('@app.get("/api/scanner/fmp/gainers")')
    if gainers_start != -1:
        gainers_end = content.find('return await fmp_scanner_scan("top_gainers"', gainers_start) + 100
        old_gainers = content[gainers_start:gainers_end]
        
        new_gainers_endpoint = '''@app.get("/api/scanner/fmp/gainers")
async def fmp_top_gainers(limit: int = 20):
    """Get top gainers using FMP real-time data - REALISTIC FILTERS"""
    return await fmp_scanner_scan("top_gainers", min_price=1.0, limit=limit)  # Lowered min price

@app.get("/api/scanner/fmp/losers") 
async def fmp_top_losers(limit: int = 20):
    """Get top losers using FMP real-time data - REALISTIC FILTERS"""
    return await fmp_scanner_scan("top_losers", min_price=1.0, limit=limit)  # Lowered min price

@app.get("/api/scanner/fmp/volume")
async def fmp_high_volume(limit: int = 20):
    """Get high volume stocks using FMP real-time data - REALISTIC FILTERS"""
    return await fmp_scanner_scan("high_volume", min_volume=500000, limit=limit)  # Lowered volume req

@app.get("/api/scanner/fmp/breakouts")
async def fmp_breakouts(limit: int = 20):
    """Get breakout stocks using FMP real-time data - REALISTIC FILTERS"""'''
        
        new_content = new_content.replace(old_gainers, new_gainers_endpoint)
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Adjusted scanner filters for realistic market conditions")
    print("📊 New filter thresholds:")
    print("   • Top Gainers: 0.5%+ (was 2.0%)")  
    print("   • Top Losers: -0.5%+ (was -2.0%)")
    print("   • High Volume: 0.8x min volume (was 1.5x)")
    print("   • Breakouts: 1.5%+ (was 3.0%)")
    print("   • Min Price: $1.00 (was $5.00)")
    print("   • Min Volume: 500K (was 1M+)")
    
    return True

if __name__ == "__main__":
    adjust_scanner_filters()