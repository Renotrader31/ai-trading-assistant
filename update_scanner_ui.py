#!/usr/bin/env python3
"""
Update the scanner UI to use FMP real-time endpoints
"""

def update_scanner_ui():
    """Update the HTML to use new FMP scanner endpoints"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the scanner JavaScript section
    js_start = content.find('// Enhanced Scanner Functions with Full Universe Support')
    if js_start == -1:
        js_start = content.find('async function runScan() {')
    
    if js_start == -1:
        print("❌ Could not find scanner JavaScript section")
        return False
    
    # Find the end of runScan function
    js_end = content.find('function displayScanResults(data, processingTime) {', js_start)
    
    if js_end == -1:
        print("❌ Could not find end of scanner functions")
        return False
    
    # New JavaScript functions for FMP scanner
    new_js = '''        // FMP Real-Time Scanner Functions
        
        async function runScan() {
            const scanType = document.getElementById('scanType')?.value || 'ALL';
            const minPrice = parseFloat(document.getElementById('minPrice')?.value || 5);
            const maxPrice = parseFloat(document.getElementById('maxPrice')?.value || 500);
            const minVolume = parseInt(document.getElementById('minVolume')?.value || 1000000);
            const limit = parseInt(document.getElementById('limitResults')?.value || 25);
            
            const resultsDiv = document.getElementById('scannerResults');
            const scanButton = document.getElementById('scanButton');
            
            if (scanButton) {
                scanButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Scanning...';
                scanButton.disabled = true;
            }
            
            // Map scanner types to FMP endpoints
            const scannerEndpoints = {
                'TOP_GAINERS': '/api/scanner/fmp/gainers',
                'top_gainers': '/api/scanner/fmp/gainers',
                'TOP_LOSERS': '/api/scanner/fmp/losers', 
                'top_losers': '/api/scanner/fmp/losers',
                'HIGH_VOLUME': '/api/scanner/fmp/volume',
                'high_volume': '/api/scanner/fmp/volume',
                'BREAKOUT_STOCKS': '/api/scanner/fmp/breakouts',
                'breakouts': '/api/scanner/fmp/breakouts'
            };
            
            resultsDiv.innerHTML = `
                <div class="text-center text-blue-400 mt-8">
                    <i class="fas fa-rocket text-4xl mb-4"></i>
                    <p class="text-lg font-semibold">🚀 Scanning with FMP Real-Time Data</p>
                    <p class="text-sm mt-2">Using <strong>${scanType.replace('_', ' ')}</strong> scanner</p>
                    <div class="mt-4">
                        <div class="inline-flex items-center px-4 py-2 rounded-full text-sm bg-blue-600/20 text-blue-300 border border-blue-500/30">
                            <i class="fas fa-lightning-bolt mr-2"></i>TRUE Real-Time Data (No Delay)
                        </div>
                    </div>
                    <div class="mt-2 text-xs text-gray-400">
                        Price: $${minPrice}-$${maxPrice} | Min Volume: ${minVolume.toLocaleString()} | Limit: ${limit}
                    </div>
                </div>
            `;
            
            const startTime = Date.now();
            
            try {
                let apiUrl;
                
                // Use specific endpoint or generic scanner
                if (scannerEndpoints[scanType]) {
                    apiUrl = `${scannerEndpoints[scanType]}?limit=${limit}`;
                } else {
                    // Use generic FMP scanner with parameters
                    const params = new URLSearchParams({
                        scan_type: scanType.toLowerCase(),
                        min_price: minPrice,
                        max_price: maxPrice, 
                        min_volume: minVolume,
                        limit: limit
                    });
                    apiUrl = `/api/scanner/fmp/scan?${params}`;
                }
                
                console.log('🔍 FMP Scanner URL:', apiUrl);
                
                const response = await fetch(apiUrl);
                const data = await response.json();
                
                if (!data.success) {
                    throw new Error(data.error || 'Scanner API error');
                }
                
                const processingTime = ((Date.now() - startTime) / 1000).toFixed(2);
                displayFMPScanResults(data, processingTime);
                
            } catch (error) {
                console.error('FMP Scanner error:', error);
                resultsDiv.innerHTML = `
                    <div class="text-center text-red-400 mt-8">
                        <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                        <p class="text-lg font-semibold">Scanner Error</p>
                        <p class="text-sm mt-2">${error.message}</p>
                        <div class="mt-4 space-x-2">
                            <button onclick="runScan()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm">
                                <i class="fas fa-redo mr-2"></i>Try Again
                            </button>
                            <button onclick="setQuickScan('top_gainers')" class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm">
                                <i class="fas fa-chart-line mr-2"></i>Top Gainers
                            </button>
                        </div>
                    </div>
                `;
            } finally {
                if (scanButton) {
                    scanButton.innerHTML = '<i class="fas fa-search mr-2"></i>Scan Now';
                    scanButton.disabled = false;
                }
            }
        }

        function displayFMPScanResults(data, processingTime) {
            const resultsDiv = document.getElementById('scannerResults');
            
            // Update statistics
            const scanResultsEl = document.getElementById('scanResults');
            const scanTotalEl = document.getElementById('scanTotal');
            const scanTimeEl = document.getElementById('scanTime');
            
            if (scanResultsEl) scanResultsEl.textContent = data.stocks.length || 0;
            if (scanTotalEl) scanTotalEl.textContent = data.total_scanned || 0;
            if (scanTimeEl) {
                scanTimeEl.textContent = `Last scan: ${processingTime}s (${data.processing_time}s server) • FMP Real-Time`;
            }
            
            if (data.stocks.length === 0) {
                resultsDiv.innerHTML = `
                    <div class="text-center text-gray-400 mt-8">
                        <i class="fas fa-search text-4xl mb-4"></i>
                        <p>No stocks found matching your criteria</p>
                        <p class="text-sm mt-2">Try adjusting your filters or selecting a different scanner type</p>
                        <div class="mt-4">
                            <button onclick="setQuickScan('top_gainers')" class="bg-green-600 hover:bg-green-700 px-3 py-2 rounded-lg text-sm mr-2">
                                📈 Top Gainers
                            </button>
                            <button onclick="setQuickScan('top_losers')" class="bg-red-600 hover:bg-red-700 px-3 py-2 rounded-lg text-sm mr-2">
                                📉 Top Losers
                            </button>
                            <button onclick="setQuickScan('high_volume')" class="bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded-lg text-sm">
                                📊 High Volume
                            </button>
                        </div>
                    </div>
                `;
                return;
            }
            
            let html = '';
            data.stocks.forEach(stock => {
                const changeColor = stock.changePercent >= 0 ? 'text-green-400' : 'text-red-400';
                const changeIcon = stock.changePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
                const changeBg = stock.changePercent >= 0 ? 'bg-green-600/20' : 'bg-red-600/20';
                
                html += `
                    <div class="scanner-result-row bg-gray-800/50 hover:bg-gray-700/50 rounded-lg p-4 cursor-pointer transition-all border border-gray-700/50 hover:border-blue-500/30" onclick="analyzeStock('${stock.symbol}')">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-4">
                                <div>
                                    <div class="font-bold text-white text-lg">${stock.symbol}</div>
                                    <div class="text-sm text-gray-400 truncate max-w-48">${stock.name}</div>
                                    <div class="text-xs text-gray-500">${stock.exchange}</div>
                                </div>
                                <div class="text-right">
                                    <div class="font-semibold text-lg text-white">$${stock.price}</div>
                                    <div class="${changeColor} text-sm font-medium ${changeBg} px-2 py-1 rounded">
                                        <i class="fas ${changeIcon} mr-1"></i>
                                        ${stock.changePercent > 0 ? '+' : ''}${stock.changePercent}%
                                    </div>
                                    <div class="text-xs text-gray-400 mt-1">
                                        ${stock.change > 0 ? '+' : ''}$${stock.change}
                                    </div>
                                </div>
                            </div>
                            <div class="flex items-center space-x-4 text-sm">
                                <div class="text-center">
                                    <div class="text-gray-400 text-xs">Volume</div>
                                    <div class="text-white font-medium">${formatNumber(stock.volume)}</div>
                                </div>
                                <div class="text-center">
                                    <div class="text-gray-400 text-xs">Market Cap</div>
                                    <div class="text-white">${stock.marketCap}</div>
                                </div>
                                <div class="text-center">
                                    <div class="text-gray-400 text-xs">Day Range</div>
                                    <div class="text-white text-xs">$${stock.dayLow} - $${stock.dayHigh}</div>
                                </div>
                                <div class="text-center">
                                    <div class="text-gray-400 text-xs">P/E</div>
                                    <div class="text-white">${stock.pe || 'N/A'}</div>
                                </div>
                                <div class="text-center">
                                    <div class="text-gray-400 text-xs">Score</div>
                                    <div class="text-yellow-400 font-bold text-lg">${Math.round(stock.score)}</div>
                                </div>
                                <div class="text-center">
                                    <i class="fas fa-lightning-bolt text-blue-400" title="Real-time FMP data"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            // Add header showing data source
            const headerHtml = `
                <div class="mb-4 p-3 bg-gradient-to-r from-blue-600/20 to-green-600/20 rounded-lg border border-blue-500/30">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <i class="fas fa-lightning-bolt text-blue-400 mr-2"></i>
                            <span class="text-white font-medium">Real-Time Results</span>
                            <span class="text-green-400 ml-2">• Live FMP Data</span>
                        </div>
                        <div class="text-sm text-gray-300">
                            Found ${data.stocks.length} stocks • Scanned ${data.total_scanned} • ${data.processing_time}s
                        </div>
                    </div>
                </div>
            `;
            
            resultsDiv.innerHTML = headerHtml + html;
        }
        
        // Update quick scan functions for FMP
        function setQuickScan(scanType) {
            const scanTypeSelect = document.getElementById('scanType');
            if (scanTypeSelect) {
                // Map to FMP scanner types
                const fmpScanTypes = {
                    'TOP_GAINERS': 'top_gainers',
                    'TOP_LOSERS': 'top_losers', 
                    'HIGH_VOLUME': 'high_volume',
                    'BREAKOUT_STOCKS': 'breakouts'
                };
                
                scanTypeSelect.value = fmpScanTypes[scanType] || scanType;
                runScan();
            }
        }

        '''
    
    # Replace the scanner JavaScript
    new_content = content[:js_start] + new_js + content[js_end:]
    
    # Write the updated main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated scanner UI for FMP real-time data")
    print("🎯 Scanner now uses FMP endpoints with real-time data")
    print("⚡ Enhanced UI shows live data indicators and better formatting")
    
    return True

if __name__ == "__main__":
    update_scanner_ui()