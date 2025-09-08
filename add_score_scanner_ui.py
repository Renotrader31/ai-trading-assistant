#!/usr/bin/env python3
"""
Add score-based scanner options to the UI
"""

def add_score_scanner_ui():
    """Update the JavaScript scanner types to include score-based scanners"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the scanner types definition
    old_scanner_types = """const scannerTypes = {
                        'top_gainers': '📈 Top Gainers',
                        'top_losers': '📉 Top Losers', 
                        'high_volume': '📊 High Volume',
                        'breakouts': '🚀 Breakouts',
                        'momentum': '⚡ Momentum',
                        'under_10': '💰 Under $10'
                    };"""
    
    # New scanner types with score-based options
    new_scanner_types = """const scannerTypes = {
                        'top_gainers': '📈 Top Gainers',
                        'top_losers': '📉 Top Losers', 
                        'high_volume': '📊 High Volume',
                        'breakouts': '🚀 Breakouts',
                        'momentum': '⚡ Momentum',
                        'under_10': '💰 Under $10',
                        'premium': '🎯 Premium Opportunities (Score 80+)',
                        'elite': '⭐ Elite Opportunities (Score 90+)',
                        'legendary': '🏆 Legendary Opportunities (Score 95+)'
                    };"""
    
    # Replace the scanner types
    if old_scanner_types in content:
        content = content.replace(old_scanner_types, new_scanner_types)
        print("✅ Updated scanner types with score-based options!")
    else:
        print("❌ Could not find scanner types definition")
        return False
    
    # Now I need to update the runScan function to handle the new scanner types
    # Find the URL mapping section
    scan_url_section = content.find("scanType === 'top_gainers'")
    if scan_url_section == -1:
        print("❌ Could not find scan URL mapping section")
        return False
    
    # Find the full URL mapping section to replace
    old_url_mapping = """if (scanType === 'top_gainers') {
                        scanUrl = `/api/scanner/fmp/gainers?limit=${limit}`;
                    } else if (scanType === 'top_losers') {
                        scanUrl = `/api/scanner/fmp/losers?limit=${limit}`;
                    } else if (scanType === 'high_volume') {
                        scanUrl = `/api/scanner/fmp/volume?limit=${limit}`;
                    } else if (scanType === 'breakouts') {
                        scanUrl = `/api/scanner/fmp/breakouts?limit=${limit}`;
                    } else if (scanType === 'momentum') {
                        scanUrl = `/api/scanner/fmp/momentum?limit=${limit}`;
                    } else if (scanType === 'under_10') {
                        scanUrl = `/api/scanner/fmp/under10?limit=${limit}`;
                    }"""
    
    new_url_mapping = """if (scanType === 'top_gainers') {
                        scanUrl = `/api/scanner/fmp/gainers?limit=${limit}`;
                    } else if (scanType === 'top_losers') {
                        scanUrl = `/api/scanner/fmp/losers?limit=${limit}`;
                    } else if (scanType === 'high_volume') {
                        scanUrl = `/api/scanner/fmp/volume?limit=${limit}`;
                    } else if (scanType === 'breakouts') {
                        scanUrl = `/api/scanner/fmp/breakouts?limit=${limit}`;
                    } else if (scanType === 'momentum') {
                        scanUrl = `/api/scanner/fmp/momentum?limit=${limit}`;
                    } else if (scanType === 'under_10') {
                        scanUrl = `/api/scanner/fmp/under10?limit=${limit}`;
                    } else if (scanType === 'premium') {
                        scanUrl = `/api/scanner/fmp/premium?limit=${limit}`;
                    } else if (scanType === 'elite') {
                        scanUrl = `/api/scanner/fmp/elite?limit=${limit}`;
                    } else if (scanType === 'legendary') {
                        scanUrl = `/api/scanner/fmp/legendary?limit=${limit}`;
                    }"""
    
    # Replace the URL mapping
    if old_url_mapping in content:
        content = content.replace(old_url_mapping, new_url_mapping)
        print("✅ Updated URL mapping for score-based scanners!")
    else:
        print("❌ Could not find URL mapping section")
        return False
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(content)
    
    print("🎯 Score-Based Scanner UI Update Complete!")
    print("📋 New scanner options available in dropdown:")
    print("   🎯 Premium Opportunities (Score 80+)")
    print("   ⭐ Elite Opportunities (Score 90+)")
    print("   🏆 Legendary Opportunities (Score 95+)")
    print("")
    print("🔥 Users can now find the highest quality trading opportunities!")
    
    return True

if __name__ == "__main__":
    add_score_scanner_ui()