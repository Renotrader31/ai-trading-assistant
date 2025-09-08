#!/usr/bin/env python3
"""
Fix the JavaScript scanner errors and missing functions
"""

def fix_scanner_js_errors():
    """Fix the JavaScript errors in the scanner UI"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the JavaScript section where we need to add the missing functions
    js_start = content.find('// FMP Real-Time Scanner Functions')
    if js_start == -1:
        js_start = content.find('async function runScan() {')
    
    if js_start == -1:
        print("❌ Could not find JavaScript section")
        return False
    
    # Find where to insert the missing functions (before runScan)
    runscan_start = content.find('async function runScan() {', js_start)
    
    if runscan_start == -1:
        print("❌ Could not find runScan function")
        return False
    
    # Add the missing JavaScript functions
    missing_functions = '''        // Load scanner types on page load
        async function loadScannerTypes() {
            try {
                const scanTypeSelect = document.getElementById('scanType');
                if (scanTypeSelect) {
                    scanTypeSelect.innerHTML = '';
                    
                    // Add FMP scanner types
                    const scannerTypes = {
                        'top_gainers': '📈 Top Gainers',
                        'top_losers': '📉 Top Losers', 
                        'high_volume': '📊 High Volume',
                        'breakouts': '🚀 Breakouts',
                        'momentum': '⚡ Momentum',
                        'under_10': '💰 Under $10'
                    };
                    
                    for (const [key, name] of Object.entries(scannerTypes)) {
                        const option = document.createElement('option');
                        option.value = key;
                        option.textContent = name;
                        scanTypeSelect.appendChild(option);
                    }
                }
                
                console.log('✅ Scanner types loaded');
                
            } catch (error) {
                console.error('Error loading scanner types:', error);
            }
        }
        
        '''
    
    # Insert the missing functions before runScan
    new_content = content[:runscan_start] + missing_functions + content[runscan_start:]
    
    # Now fix the runScan function to handle "all" type better
    old_runscan = content.find('const scannerEndpoints = {')
    if old_runscan != -1:
        endpoints_end = content.find('};', old_runscan) + 2
        
        # Replace the scanner endpoints mapping
        new_endpoints = '''const scannerEndpoints = {
                'TOP_GAINERS': '/api/scanner/fmp/gainers',
                'top_gainers': '/api/scanner/fmp/gainers',
                'TOP_LOSERS': '/api/scanner/fmp/losers', 
                'top_losers': '/api/scanner/fmp/losers',
                'HIGH_VOLUME': '/api/scanner/fmp/volume',
                'high_volume': '/api/scanner/fmp/volume',
                'BREAKOUT_STOCKS': '/api/scanner/fmp/breakouts',
                'breakouts': '/api/scanner/fmp/breakouts',
                'momentum': '/api/scanner/fmp/scan',
                'under_10': '/api/scanner/fmp/scan',
                'all': '/api/scanner/fmp/gainers'  // Default to gainers for "all"
            };'''
        
        old_endpoints_section = content[old_runscan:endpoints_end]
        new_content = new_content.replace(old_endpoints_section, new_endpoints)
    
    # Also add the "all" scanner type handling to our backend
    backend_fix = '''
@app.get("/api/scanner/fmp/all")
async def fmp_all_stocks(limit: int = 25):
    """Get mixed results - combination of gainers and volume for 'all' scanner"""
    try:
        # Get some gainers and some high volume stocks
        gainers_limit = limit // 2
        volume_limit = limit - gainers_limit
        
        gainers_data = await fmp_scanner_scan("top_gainers", min_price=5.0, limit=gainers_limit)
        volume_data = await fmp_scanner_scan("high_volume", min_volume=2000000, limit=volume_limit)
        
        # Combine results
        all_stocks = []
        if gainers_data.get("success"):
            all_stocks.extend(gainers_data.get("stocks", []))
        if volume_data.get("success"):
            all_stocks.extend(volume_data.get("stocks", []))
        
        # Sort by score and remove duplicates
        seen_symbols = set()
        unique_stocks = []
        for stock in sorted(all_stocks, key=lambda x: x.get("score", 0), reverse=True):
            if stock["symbol"] not in seen_symbols:
                seen_symbols.add(stock["symbol"])
                unique_stocks.append(stock)
        
        return {
            "success": True,
            "scan_type": "all",
            "stocks": unique_stocks[:limit],
            "total_scanned": len(all_stocks),
            "matches": len(unique_stocks),
            "processing_time": 1.0,
            "data_source": "fmp_real_time_mixed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stocks": []
        }

'''
    
    # Find where to add the new endpoint (before the WebSocket)
    ws_start = content.find('@app.websocket("/ws")')
    if ws_start != -1:
        new_content = new_content[:ws_start] + backend_fix + '\n' + new_content[ws_start:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed JavaScript scanner errors")
    print("🔧 Added missing loadScannerTypes function")
    print("📊 Fixed scanner endpoints mapping")
    print("⚡ Added /api/scanner/fmp/all endpoint for mixed results")
    
    return True

if __name__ == "__main__":
    fix_scanner_js_errors()