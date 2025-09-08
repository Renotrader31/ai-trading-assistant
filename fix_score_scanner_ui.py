#!/usr/bin/env python3
"""
Fix the score-based scanner UI integration
"""

def fix_score_scanner_ui():
    """Update the JavaScript scanner endpoints mapping to include score-based scanners"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the scanner endpoints definition
    old_endpoints = """const scannerEndpoints = {
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
            };"""
    
    # New endpoints with score-based options
    new_endpoints = """const scannerEndpoints = {
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
                'premium': '/api/scanner/fmp/premium',
                'elite': '/api/scanner/fmp/elite',
                'legendary': '/api/scanner/fmp/legendary',
                'all': '/api/scanner/fmp/gainers'  // Default to gainers for "all"
            };"""
    
    # Replace the endpoints mapping
    if old_endpoints in content:
        content = content.replace(old_endpoints, new_endpoints)
        print("✅ Updated scanner endpoints mapping with score-based options!")
    else:
        print("❌ Could not find scanner endpoints definition")
        return False
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(content)
    
    print("🎯 Score-Based Scanner Integration Complete!")
    print("📋 Added endpoints:")
    print("   premium → /api/scanner/fmp/premium (Score 80+)")
    print("   elite → /api/scanner/fmp/elite (Score 90+)")
    print("   legendary → /api/scanner/fmp/legendary (Score 95+)")
    print("")
    print("🔥 Users can now access premium trading opportunities via dropdown!")
    
    return True

if __name__ == "__main__":
    fix_score_scanner_ui()