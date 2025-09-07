#!/usr/bin/env python3
"""
Build comprehensive stock universe from multiple sources
"""
import requests
import json
import time
from typing import List, Dict, Set

def fetch_nasdaq_stocks() -> List[str]:
    """Fetch NASDAQ-listed stocks"""
    try:
        print("📊 Fetching NASDAQ stocks...")
        url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
        response = requests.get(url, timeout=30)
        lines = response.text.splitlines()
        
        symbols = []
        for line in lines[1:]:  # Skip header
            if line and not line.startswith("File Creation"):
                parts = line.split('|')
                if parts[0] and len(parts[0]) <= 5:  # Valid symbol
                    symbols.append(parts[0].strip())
        
        print(f"✅ Found {len(symbols)} NASDAQ stocks")
        return symbols
    except Exception as e:
        print(f"❌ Error fetching NASDAQ stocks: {e}")
        return []

def fetch_nyse_stocks() -> List[str]:
    """Fetch NYSE and other exchange stocks"""
    try:
        print("📊 Fetching NYSE/Other stocks...")
        url = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
        response = requests.get(url, timeout=30)
        lines = response.text.splitlines()
        
        symbols = []
        for line in lines[1:]:  # Skip header
            if line and not line.startswith("File Creation"):
                parts = line.split('|')
                if parts[0] and len(parts[0]) <= 5:  # Valid symbol
                    symbols.append(parts[0].strip())
        
        print(f"✅ Found {len(symbols)} NYSE/Other stocks")
        return symbols
    except Exception as e:
        print(f"❌ Error fetching NYSE stocks: {e}")
        return []

def get_popular_stocks() -> List[str]:
    """Get curated list of popular/liquid stocks for fast scanning"""
    return [
        # Mega Cap Tech
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
        # Large Cap Tech
        'NFLX', 'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'NOW', 'PYPL',
        # Financial
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC',
        # Healthcare 
        'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'CVS', 'GILD', 'AMGN',
        # Consumer
        'WMT', 'HD', 'PG', 'KO', 'PEP', 'MCD', 'NKE', 'DIS',
        # Energy
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'OXY', 'PSX', 'VLO',
        # Communication
        'VZ', 'T', 'TMUS', 'CHTR', 'CMCSA', 'NFLX', 'PARA',
        # Industrial
        'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'RTX', 'LMT',
        # Popular Growth/Meme
        'UBER', 'SHOP', 'SQ', 'ROKU', 'ZM', 'SNOW', 'PLTR', 'COIN',
        'RBLX', 'HOOD', 'SOFI', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI',
        # ETFs
        'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'ARKK', 'SQQQ',
        # Biotech
        'BIIB', 'REGN', 'VRTX', 'CELG', 'ILMN', 'MRNA', 'BNTX',
        # Semiconductors
        'TSM', 'AVGO', 'TXN', 'QCOM', 'MU', 'AMAT', 'LRCX', 'KLAC',
        # Banking/Finance
        'BRK.A', 'BRK.B', 'V', 'MA', 'AXP', 'SPGI', 'BLK', 'SCHW',
        # REITs  
        'AMT', 'CCI', 'EQIX', 'PLD', 'SPG', 'O', 'WELL', 'PSA',
        # Retail
        'AMZN', 'COST', 'TGT', 'LOW', 'SBUX', 'CMG', 'LULU', 'ROST'
    ]

def get_sector_mapping() -> Dict[str, str]:
    """Basic sector mapping for popular stocks"""
    return {
        # Technology
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 
        'GOOG': 'Technology', 'META': 'Technology', 'NVDA': 'Technology',
        'NFLX': 'Technology', 'AMD': 'Technology', 'INTC': 'Technology',
        'CRM': 'Technology', 'ORCL': 'Technology', 'ADBE': 'Technology',
        'NOW': 'Technology', 'PYPL': 'Technology', 'UBER': 'Technology',
        'SHOP': 'Technology', 'SQ': 'Technology', 'ROKU': 'Technology',
        'ZM': 'Technology', 'SNOW': 'Technology', 'PLTR': 'Technology',
        
        # Financial
        'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial',
        'GS': 'Financial', 'MS': 'Financial', 'C': 'Financial',
        'BRK.A': 'Financial', 'BRK.B': 'Financial', 'V': 'Financial',
        'MA': 'Financial', 'AXP': 'Financial', 'COIN': 'Financial',
        
        # Healthcare
        'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare',
        'ABBV': 'Healthcare', 'MRK': 'Healthcare', 'BIIB': 'Healthcare',
        'REGN': 'Healthcare', 'VRTX': 'Healthcare', 'MRNA': 'Healthcare',
        
        # Consumer Discretionary  
        'AMZN': 'Consumer Discretionary', 'TSLA': 'Consumer Discretionary',
        'HD': 'Consumer Discretionary', 'MCD': 'Consumer Discretionary',
        'NKE': 'Consumer Discretionary', 'DIS': 'Consumer Discretionary',
        'SBUX': 'Consumer Discretionary', 'CMG': 'Consumer Discretionary',
        
        # Consumer Staples
        'WMT': 'Consumer Staples', 'PG': 'Consumer Staples',
        'KO': 'Consumer Staples', 'PEP': 'Consumer Staples',
        'COST': 'Consumer Staples',
        
        # Energy
        'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy',
        'SLB': 'Energy', 'EOG': 'Energy', 'OXY': 'Energy',
        
        # Communication Services
        'VZ': 'Communication Services', 'T': 'Communication Services',
        'TMUS': 'Communication Services', 'CHTR': 'Communication Services',
        
        # Industrials
        'BA': 'Industrials', 'CAT': 'Industrials', 'GE': 'Industrials',
        'MMM': 'Industrials', 'HON': 'Industrials', 'UPS': 'Industrials',
        
        # ETF
        'SPY': 'ETF', 'QQQ': 'ETF', 'IWM': 'ETF', 'DIA': 'ETF',
        'VTI': 'ETF', 'VOO': 'ETF', 'ARKK': 'ETF',
        
        # Auto
        'RIVN': 'Automotive', 'LCID': 'Automotive', 'NIO': 'Automotive',
        'XPEV': 'Automotive', 'LI': 'Automotive'
    }

def build_comprehensive_universe() -> Dict:
    """Build the complete stock universe"""
    print("🚀 Building comprehensive stock universe...")
    
    # Fetch from official sources
    nasdaq_stocks = fetch_nasdaq_stocks()
    nyse_stocks = fetch_nyse_stocks()
    
    # Combine and deduplicate
    all_symbols = set()
    all_symbols.update(nasdaq_stocks)
    all_symbols.update(nyse_stocks)
    
    # Remove invalid symbols
    valid_symbols = []
    for symbol in all_symbols:
        if symbol and len(symbol) <= 5 and symbol.isalpha():
            valid_symbols.append(symbol)
    
    # Get popular stocks for quick scanning
    popular = get_popular_stocks()
    
    # Get sector mapping
    sectors = get_sector_mapping()
    
    universe = {
        'total_stocks': len(valid_symbols),
        'popular_stocks': popular,
        'all_stocks': sorted(valid_symbols),
        'nasdaq_count': len(nasdaq_stocks),
        'nyse_count': len(nyse_stocks),
        'sectors': sectors,
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    print(f"✅ Built universe with {len(valid_symbols)} total stocks")
    print(f"📊 NASDAQ: {len(nasdaq_stocks)}, NYSE: {len(nyse_stocks)}")
    print(f"⭐ Popular stocks: {len(popular)}")
    
    return universe

def save_universe(universe: Dict, filename: str = "stock_universe.json"):
    """Save the stock universe to file"""
    try:
        with open(filename, 'w') as f:
            json.dump(universe, f, indent=2)
        print(f"💾 Saved universe to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving universe: {e}")
        return False

if __name__ == "__main__":
    # Build the universe
    universe = build_comprehensive_universe()
    
    # Save to file
    save_universe(universe)
    
    # Print summary
    print(f"\n📈 STOCK UNIVERSE SUMMARY")
    print(f"{'='*50}")
    print(f"Total Stocks: {universe['total_stocks']:,}")
    print(f"NASDAQ: {universe['nasdaq_count']:,}")
    print(f"NYSE/Other: {universe['nyse_count']:,}")
    print(f"Popular/Liquid: {len(universe['popular_stocks'])}")
    print(f"Sectors Mapped: {len(universe['sectors'])}")
    print(f"Last Updated: {universe['last_updated']}")