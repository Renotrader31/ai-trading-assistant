from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import httpx
import asyncio
from typing import Dict, Any
import os
from datetime import datetime
import uvicorn

# Create FastAPI app
app = FastAPI(title="AI Trading Assistant", description="Beautiful Polygon.io + Claude AI Platform")

# API Keys from environment
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "demo_key")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "demo_key")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

manager = ConnectionManager()

async def get_market_data(symbol: str) -> Dict[str, Any]:
    """Get market data from Polygon.io or return demo data"""
    if POLYGON_API_KEY == "demo_key":
        # Enhanced demo data for testing
        return {
            "demo": True,
            "symbol": symbol,
            "price": 175.50 + hash(symbol) % 50,
            "change": (hash(symbol) % 10) - 5,
            "volume": 50000000 + hash(symbol) % 20000000,
            "market_cap": "2.8T",
            "pe_ratio": 28.5,
            "52_week_high": 198.23,
            "52_week_low": 164.08
        }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get ticker details
            details_url = f"https://api.polygon.io/v3/reference/tickers/{symbol}?apikey={POLYGON_API_KEY}"
            details_response = await client.get(details_url)
            
            # Get previous close
            prev_close_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={POLYGON_API_KEY}"
            prev_close_response = await client.get(prev_close_url)
            
            # Get real-time quote (if available)
            quote_url = f"https://api.polygon.io/v2/last/trade/{symbol}?apikey={POLYGON_API_KEY}"
            quote_response = await client.get(quote_url)
            
            # Parse the responses
            details_data = details_response.json() if details_response.status_code == 200 else {}
            prev_close_data = prev_close_response.json() if prev_close_response.status_code == 200 else {}
            quote_data = quote_response.json() if quote_response.status_code == 200 else {}
            
            # Extract key information and format it consistently
            current_price = None
            prev_close_price = None
            
            # Try to get current price from last trade
            if quote_data.get('results'):
                current_price = quote_data['results'].get('p')
            
            # Get previous close price
            if prev_close_data.get('results') and len(prev_close_data['results']) > 0:
                prev_close_price = prev_close_data['results'][0].get('c')
                if not current_price:  # Use prev close as current if no real-time data
                    current_price = prev_close_price
            
            # Get company details
            company_name = symbol
            market_cap = "N/A"
            if details_data.get('results'):
                company_name = details_data['results'].get('name', symbol)
                market_cap = details_data['results'].get('market_cap', "N/A")
            
            # Calculate change if we have both prices
            change = 0
            change_percent = 0
            if current_price and prev_close_price:
                change = current_price - prev_close_price
                change_percent = (change / prev_close_price) * 100 if prev_close_price > 0 else 0
            
            # Format market data for AI analysis
            formatted_data = {
                "live_data": True,
                "symbol": symbol,
                "company_name": company_name,
                "price": current_price or 0,
                "previous_close": prev_close_price or 0,
                "change": change,
                "change_percent": change_percent,
                "market_cap": market_cap,
                "timestamp": datetime.now().isoformat(),
                "raw_data": {
                    "details": details_data,
                    "previous_close": prev_close_data,
                    "quote": quote_data
                }
            }
            
            return formatted_data
            
    except Exception as e:
        # Return error but with proper structure
        return {
            "error": str(e),
            "symbol": symbol,
            "live_data": False,
            "fallback": True
        }

async def get_ai_analysis(user_message: str, market_data: Dict[str, Any]) -> str:
    """Get AI analysis from Claude or return enhanced demo response"""
    if ANTHROPIC_API_KEY == "demo_key":
        # Enhanced demo AI responses
        query_lower = user_message.lower()
        
        # Extract stock symbol if present
        import re
        ticker_match = re.search(r'\\b([A-Z]{2,5})\\b', user_message.upper())
        ticker = ticker_match.group(1) if ticker_match else "MARKET"
        
        if any(word in query_lower for word in ['aapl', 'apple']):
            return generate_demo_stock_analysis("AAPL", market_data)
        elif any(word in query_lower for word in ['tsla', 'tesla']):
            return generate_demo_stock_analysis("TSLA", market_data)
        elif any(word in query_lower for word in ['market', 'overview', 'sentiment']):
            return generate_demo_market_analysis()
        elif any(word in query_lower for word in ['tips', 'advice', 'strategy']):
            return generate_demo_trading_tips()
        else:
            return generate_demo_stock_analysis(ticker, market_data)
    
    # Try different Claude models in order of preference
    models_to_try = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022", 
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    
    try:
        # Real Claude AI integration with model fallback
        data_source = "LIVE POLYGON.IO DATA" if market_data.get("live_data") else "DEMO DATA"
        
        context = f"""
        User Query: {user_message}
        
        DATA SOURCE: {data_source}
        
        Market Data: {json.dumps(market_data, indent=2)}
        
        IMPORTANT: Use the EXACT price and market data provided above. If live_data=true, this is real-time market data from Polygon.io API.
        
        Please provide a comprehensive trading analysis with enhanced formatting using the ACTUAL market data:
        
        ## 📊 Market Analysis for {market_data.get('symbol', 'SYMBOL')}
        
        **Current Price**: ${market_data.get('price', 0):.2f}
        **Previous Close**: ${market_data.get('previous_close', 0):.2f}  
        **Change**: {'+' if market_data.get('change', 0) >= 0 else ''}{market_data.get('change', 0):.2f} ({market_data.get('change_percent', 0):+.2f}%)
        
        [Your detailed analysis based on the ACTUAL price data above]
        
        ## 🎯 Trading Recommendations  
        [Your recommendations with specific price targets based on current ${market_data.get('price', 0):.2f} price]
        
        ## ⚠️ Risk Assessment
        [Risk factors and mitigation strategies]
        
        ## 📈 Technical Indicators
        [Key technical levels and signals based on current data]
        
        Use markdown formatting, emojis, and highlight key financial data with **bold** text.
        Ensure all price references use the ACTUAL current price of ${market_data.get('price', 0):.2f}.
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            last_error = None
            
            # Try each model in order
            for model in models_to_try:
                try:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": ANTHROPIC_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        },
                        json={
                            "model": model,
                            "max_tokens": 1000,
                            "messages": [{"role": "user", "content": context}]
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result["content"][0]["text"]
                    elif response.status_code == 401:
                        return f"❌ **API Key Error**: Invalid or missing Anthropic API key. Please check your ANTHROPIC_API_KEY environment variable."
                    elif response.status_code == 404:
                        # Try next model if 404
                        continue
                    else:
                        error_text = ""
                        try:
                            error_json = response.json()
                            error_text = error_json.get("error", {}).get("message", str(response.text))
                        except:
                            error_text = response.text
                        last_error = f"❌ **Error {response.status_code}**: {error_text}"
                        continue
                        
                except Exception as e:
                    last_error = f"❌ **Model {model} Error**: {str(e)}"
                    continue
            
            # If all models failed
            return f"❌ **All Models Failed**: {last_error or 'Unable to connect to Claude API'}"
                
    except Exception as e:
        return f"❌ **Error**: {str(e)}"

def generate_demo_stock_analysis(ticker: str, market_data: Dict[str, Any]) -> str:
    """Generate enhanced demo stock analysis"""
    price = market_data.get("price", 175.50)
    change = market_data.get("change", 2.25)
    
    return f"""## 📊 Market Analysis for {ticker}

**Current Price**: ${price:.2f} (**{'+' if change > 0 else ''}{change:.2f}** / **{change/price*100:.1f}%**)

The stock is showing **{'strong bullish' if change > 0 else 'bearish'}** momentum with significant volume activity. Technical indicators suggest a **{'continuation of upward trend' if change > 0 else 'potential reversal opportunity'}**.

## 🎯 Trading Recommendations

**Entry Strategy**: Consider **{'dollar-cost averaging' if change > 0 else 'accumulation on dips'}** around **${price-5:.2f} - ${price+5:.2f}** range.

**Price Targets**:
• **Short-term**: ${price+10:.2f} (resistance level)
• **Medium-term**: ${price+25:.2f} (next major resistance)
• **Support**: ${price-15:.2f} (key support zone)

## ⚠️ Risk Assessment

**Risk Level**: **Medium** 
• Market volatility remains elevated
• Consider **position sizing** at 2-3% of portfolio
• **Stop-loss** recommended at ${price-20:.2f}

## 📈 Technical Indicators

**RSI**: 58.2 (Neutral zone)
**MACD**: Bullish crossover detected
**Volume**: Above average (**25% higher**)
**Moving Averages**: Trading above **50-day** and **200-day** MA

**Next catalyst**: Earnings report in 2 weeks - expect increased volatility."""

def generate_demo_market_analysis() -> str:
    """Generate demo market analysis"""
    return """## 📊 Market Overview & Sentiment

**Current Market State**: **Cautiously Optimistic**

The markets are showing **mixed signals** with tech leading while financials lag. Overall sentiment remains **positive** despite recent volatility.

## 🎯 Sector Recommendations

**Outperforming Sectors**:
• **Technology** (+2.3%) - AI and cloud computing driving growth
• **Healthcare** (+1.8%) - Biotech breakthroughs supporting sector
• **Energy** (+1.2%) - Oil prices stabilizing

**Underperforming**:
• **Real Estate** (-0.8%) - Interest rate concerns
• **Utilities** (-0.5%) - Defensive rotation

## ⚠️ Market Risks

**Key Concerns**:
• **Federal Reserve** policy uncertainty
• **Inflation** data pending this week
• **Geopolitical tensions** in emerging markets

## 📈 Trading Strategy

**Recommended Approach**:
• **60%** large-cap growth stocks
• **25%** defensive positions
• **15%** cash for opportunities

**Watch for**: FOMC minutes release and CPI data."""

def generate_demo_trading_tips() -> str:
    """Generate demo trading tips"""
    return """## 🎯 Professional Trading Tips

### **Risk Management Fundamentals**

**1. Position Sizing**
• Never risk more than **2-3%** of portfolio on single trade
• Use **Kelly Criterion** for optimal position sizing
• Diversify across **8-12** uncorrelated positions

**2. Stop-Loss Strategy**
• Set stops at **15-20%** below entry for growth stocks
• Use **trailing stops** to protect profits
• **Never** move stops against you

### **Entry & Exit Tactics**

**Best Entry Times**:
• **10:00-11:00 AM ET** (after morning volatility)
• **2:00-3:00 PM ET** (afternoon momentum)
• Avoid first/last 30 minutes unless scalping

**Exit Rules**:
• Take **partial profits** at 20-25% gains
• **Scale out** in 3 tranches: 25%, 50%, 25%
• Let winners run, cut losers quickly

### **Market Psychology**

**Emotional Control**:
• **Fear** and **greed** are your biggest enemies
• Stick to your **predetermined plan**
• Keep a trading journal for self-analysis

**Contrarian Signals**:
• **Extreme optimism** = time to be cautious
• **Widespread pessimism** = opportunity zones

**Remember**: Consistency beats home runs every time! 📈"""

@app.get("/", response_class=HTMLResponse)
async def get_root():
    """Serve the beautiful AI assistant interface"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Trading Assistant - Polygon.io + Claude AI</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #0A0E27 0%, #1a1f3a 50%, #0f1419 100%);
            min-height: 100vh;
            font-family: system-ui, -apple-system, sans-serif;
        }
        
        .glass-effect {
            background: rgba(31, 41, 55, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        .gradient-text {
            background: linear-gradient(to right, #60A5FA, #A78BFA, #F472B6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .ai-chat-bubble {
            max-width: 85%;
            word-wrap: break-word;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .ai-user { 
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        
        .ai-assistant { 
            background: rgba(55, 65, 81, 0.7);
            color: #E5E7EB;
            margin-right: auto;
            border-bottom-left-radius: 5px;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        .ai-response {
            line-height: 1.6;
        }
        
        .ai-response h3 {
            color: #60A5FA;
            font-weight: 600;
            margin: 12px 0 8px 0;
            font-size: 1.1em;
        }
        
        .ai-response h4 {
            color: #A78BFA;
            font-weight: 600;
            margin: 10px 0 6px 0;
            font-size: 1em;
        }
        
        .ai-response strong {
            color: #F472B6;
            font-weight: 600;
        }
        
        .ai-response .highlight {
            background: rgba(59, 130, 246, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            color: #60A5FA;
        }
        
        .chat-input {
            background: rgba(31, 41, 55, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
        }
        
        .chat-input:focus-within {
            border-color: #3B82F6;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
        }
        
        .send-button {
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .send-button:hover {
            background: linear-gradient(135deg, #1D4ED8, #1E40AF);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        .status-card {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2));
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 15px;
        }
        
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            color: #A78BFA;
            font-style: italic;
        }
        
        .typing-dots {
            display: inline-flex;
            margin-left: 8px;
        }
        
        .typing-dots span {
            background: #A78BFA;
            width: 4px;
            height: 4px;
            border-radius: 50%;
            display: inline-block;
            margin: 0 1px;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .connection-status {
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .status-connected {
            background: rgba(34, 197, 94, 0.2);
            color: #22C55E;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        .status-connecting {
            background: rgba(251, 191, 36, 0.2);
            color: #FBBF24;
            border: 1px solid rgba(251, 191, 36, 0.3);
        }
        
        .status-disconnected {
            background: rgba(239, 68, 68, 0.2);
            color: #EF4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .feature-icon {
            background: linear-gradient(135deg, #3B82F6, #A78BFA);
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            margin-bottom: 12px;
        }

        .scroll-fade {
            mask-image: linear-gradient(to bottom, transparent 0%, black 5%, black 95%, transparent 100%);
        }
    </style>
</head>
<body class="text-white">
    <div class="min-h-screen p-4">
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-4xl md:text-5xl font-bold gradient-text mb-2">
                <i class="fas fa-robot mr-3"></i>AI Trading Assistant
            </h1>
            <p class="text-xl text-gray-300">Powered by Polygon.io Real-Time Data + Claude AI Analysis</p>
        </div>

        <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Main Chat Interface -->
            <div class="lg:col-span-2">
                <div class="glass-effect rounded-2xl p-6 h-[600px] flex flex-col">
                    <!-- Chat Header -->
                    <div class="flex items-center justify-between mb-4 pb-4 border-b border-gray-600">
                        <div class="flex items-center">
                            <i class="fas fa-comments text-blue-400 mr-3 text-xl"></i>
                            <h2 class="text-xl font-semibold">AI Trading Chat</h2>
                        </div>
                        <div id="connectionStatus" class="connection-status status-connecting">
                            <i class="fas fa-wifi mr-2"></i>Connecting...
                        </div>
                    </div>

                    <!-- Chat Messages -->
                    <div id="chatMessages" class="flex-1 overflow-y-auto pr-2 scroll-fade">
                        <div class="ai-chat-bubble ai-assistant">
                            <div class="flex items-start">
                                <i class="fas fa-robot text-blue-400 mr-3 mt-1"></i>
                                <div>
                                    <div class="text-sm text-gray-400 mb-1">AI Assistant</div>
                                    <div class="ai-response">
                                        Hello! I'm your <strong>AI Trading Assistant</strong>. 
                                        <br><br>
                                        <h3><i class="fas fa-chart-line mr-2"></i>What I can help with:</h3>
                                        • <span class="highlight">Stock Analysis</span> - Ask about any ticker (AAPL, TSLA, NVDA, etc.)
                                        <br>• <span class="highlight">Market Insights</span> - Get real-time data and AI analysis
                                        <br>• <span class="highlight">Trading Strategies</span> - Professional recommendations
                                        <br>• <span class="highlight">Risk Assessment</span> - Smart risk management advice
                                        <br><br>
                                        Try asking: <em>"What do you think about AAPL right now?"</em> 📈
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Chat Input -->
                    <div class="mt-4">
                        <div class="chat-input flex items-center p-3">
                            <input 
                                type="text" 
                                id="messageInput" 
                                placeholder="Ask about stocks, market trends, trading strategies..."
                                class="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none text-sm"
                                maxlength="500"
                            >
                            <button 
                                onclick="sendMessage()" 
                                class="send-button px-4 py-2 ml-3 text-white font-medium text-sm"
                            >
                                <i class="fas fa-paper-plane mr-1"></i>Send
                            </button>
                        </div>
                        <div class="text-xs text-gray-500 mt-2 text-center">
                            Powered by Claude AI • Enhanced response formatting • Real-time analysis
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Platform Status -->
                <div class="glass-effect rounded-2xl p-6">
                    <h3 class="text-lg font-semibold mb-4 gradient-text">
                        <i class="fas fa-tachometer-alt mr-2"></i>Platform Status
                    </h3>
                    <div class="space-y-3">
                        <div class="status-card">
                            <div class="flex items-center justify-between">
                                <span class="text-sm">Market Data</span>
                                <span class="text-green-400"><i class="fas fa-check-circle"></i> Live</span>
                            </div>
                        </div>
                        <div class="status-card">
                            <div class="flex items-center justify-between">
                                <span class="text-sm">AI Analysis</span>
                                <span class="text-blue-400"><i class="fas fa-brain"></i> Active</span>
                            </div>
                        </div>
                        <div class="status-card">
                            <div class="flex items-center justify-between">
                                <span class="text-sm">WebSocket</span>
                                <span id="wsStatusIndicator" class="text-yellow-400">
                                    <i class="fas fa-spinner fa-spin"></i> Connecting
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Features -->
                <div class="glass-effect rounded-2xl p-6">
                    <h3 class="text-lg font-semibold mb-4 gradient-text">
                        <i class="fas fa-star mr-2"></i>Key Features
                    </h3>
                    <div class="space-y-4">
                        <div class="flex items-start">
                            <div class="feature-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="ml-3">
                                <h4 class="font-medium text-sm">Real-Time Data</h4>
                                <p class="text-xs text-gray-400">Live market data from Polygon.io</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <div class="feature-icon">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="ml-3">
                                <h4 class="font-medium text-sm">AI Analysis</h4>
                                <p class="text-xs text-gray-400">Claude AI trading insights</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <div class="feature-icon">
                                <i class="fas fa-bolt"></i>
                            </div>
                            <div class="ml-3">
                                <h4 class="font-medium text-sm">Enhanced UI</h4>
                                <p class="text-xs text-gray-400">Beautiful readable responses</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <div class="feature-icon">
                                <i class="fas fa-mobile-alt"></i>
                            </div>
                            <div class="ml-3">
                                <h4 class="font-medium text-sm">Mobile Ready</h4>
                                <p class="text-xs text-gray-400">Responsive design</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="glass-effect rounded-2xl p-6">
                    <h3 class="text-lg font-semibold mb-4 gradient-text">
                        <i class="fas fa-bolt mr-2"></i>Quick Actions
                    </h3>
                    <div class="grid grid-cols-2 gap-2">
                        <button onclick="quickAsk('AAPL analysis')" class="send-button p-2 text-xs rounded">
                            <i class="fab fa-apple mr-1"></i>AAPL
                        </button>
                        <button onclick="quickAsk('TSLA analysis')" class="send-button p-2 text-xs rounded">
                            <i class="fas fa-car mr-1"></i>TSLA
                        </button>
                        <button onclick="quickAsk('market overview')" class="send-button p-2 text-xs rounded">
                            <i class="fas fa-chart-bar mr-1"></i>Market
                        </button>
                        <button onclick="quickAsk('trading tips')" class="send-button p-2 text-xs rounded">
                            <i class="fas fa-lightbulb mr-1"></i>Tips
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let isConnected = false;

        // WebSocket connection
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = protocol + '//' + window.location.host + '/ws';
            
            updateConnectionStatus('connecting');
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                isConnected = true;
                updateConnectionStatus('connected');
                console.log('WebSocket connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                displayAIMessage(data.message);
            };
            
            ws.onclose = function() {
                isConnected = false;
                updateConnectionStatus('disconnected');
                console.log('WebSocket disconnected');
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateConnectionStatus('disconnected');
            };
        }

        function updateConnectionStatus(status) {
            const statusElement = document.getElementById('connectionStatus');
            const wsIndicator = document.getElementById('wsStatusIndicator');
            
            switch(status) {
                case 'connected':
                    statusElement.className = 'connection-status status-connected';
                    statusElement.innerHTML = '<i class="fas fa-wifi mr-2"></i>Connected';
                    wsIndicator.innerHTML = '<i class="fas fa-check-circle"></i> Connected';
                    wsIndicator.className = 'text-green-400';
                    break;
                case 'connecting':
                    statusElement.className = 'connection-status status-connecting';
                    statusElement.innerHTML = '<i class="fas fa-wifi mr-2"></i>Connecting...';
                    wsIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting';
                    wsIndicator.className = 'text-yellow-400';
                    break;
                case 'disconnected':
                    statusElement.className = 'connection-status status-disconnected';
                    statusElement.innerHTML = '<i class="fas fa-wifi mr-2"></i>Disconnected';
                    wsIndicator.innerHTML = '<i class="fas fa-times-circle"></i> Disconnected';
                    wsIndicator.className = 'text-red-400';
                    break;
            }
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message && isConnected) {
                displayUserMessage(message);
                showTypingIndicator();
                ws.send(JSON.stringify({message: message}));
                input.value = '';
            } else if (!isConnected) {
                displaySystemMessage('Not connected to server. Trying to reconnect...');
                connectWebSocket();
            }
        }

        function quickAsk(query) {
            const input = document.getElementById('messageInput');
            input.value = query;
            sendMessage();
        }

        function displayUserMessage(message) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'ai-chat-bubble ai-user';
            messageDiv.innerHTML = '<div class="flex items-start justify-end"><div class="text-right"><div class="text-sm text-blue-200 mb-1">You</div><div>' + message + '</div></div><i class="fas fa-user text-blue-200 ml-3 mt-1"></i></div>';
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }

        function displayAIMessage(message) {
            removeTypingIndicator();
            
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'ai-chat-bubble ai-assistant';
            
            const formattedMessage = formatAIResponse(message);
            
            messageDiv.innerHTML = '<div class="flex items-start"><i class="fas fa-robot text-blue-400 mr-3 mt-1"></i><div><div class="text-sm text-gray-400 mb-1">AI Assistant</div><div class="ai-response">' + formattedMessage + '</div></div></div>';
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }

        function formatAIResponse(message) {
            return message
                .replace(/## (.*?)$/gm, '<h3><i class="fas fa-chart-line mr-2"></i>$1</h3>')
                .replace(/### (.*?)$/gm, '<h4><i class="fas fa-arrow-right mr-2"></i>$1</h4>')
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\n/g, '<br>')
                .replace(/(\\$[\\d,]+\\.?\\d*|\\d+\\.?\\d*%)/g, '<span class="highlight">$1</span>')
                .replace(/\\b([A-Z]{2,5})\\b/g, '<span class="highlight">$1</span>')
                .replace(/📊/g, '<i class="fas fa-chart-bar text-blue-400"></i>')
                .replace(/📈/g, '<i class="fas fa-chart-line text-green-400"></i>')
                .replace(/📉/g, '<i class="fas fa-chart-line-down text-red-400"></i>')
                .replace(/🎯/g, '<i class="fas fa-bullseye text-yellow-400"></i>')
                .replace(/⚠️/g, '<i class="fas fa-exclamation-triangle text-orange-400"></i>')
                .replace(/✅/g, '<i class="fas fa-check-circle text-green-400"></i>')
                .replace(/❌/g, '<i class="fas fa-times-circle text-red-400"></i>');
        }

        function displaySystemMessage(message) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'ai-chat-bubble ai-assistant opacity-75';
            messageDiv.innerHTML = '<div class="flex items-start"><i class="fas fa-info-circle text-gray-400 mr-3 mt-1"></i><div><div class="text-sm text-gray-500 mb-1">System</div><div class="text-gray-400 text-sm">' + message + '</div></div></div>';
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }

        function showTypingIndicator() {
            const messagesDiv = document.getElementById('chatMessages');
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typingIndicator';
            typingDiv.className = 'ai-chat-bubble ai-assistant';
            typingDiv.innerHTML = '<div class="flex items-start"><i class="fas fa-robot text-blue-400 mr-3 mt-1"></i><div><div class="text-sm text-gray-400 mb-1">AI Assistant</div><div class="typing-indicator">Analyzing market data and generating insights<div class="typing-dots"><span></span><span></span><span></span></div></div></div></div>';
            messagesDiv.appendChild(typingDiv);
            scrollToBottom();
        }

        function removeTypingIndicator() {
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        function scrollToBottom() {
            const messagesDiv = document.getElementById('chatMessages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        window.addEventListener('load', function() {
            connectWebSocket();
            displaySystemMessage('Welcome to your AI Trading Assistant! Connecting to real-time services...');
        });

        window.addEventListener('focus', function() {
            if (!isConnected) {
                connectWebSocket();
            }
        });
    </script>
</body>
</html>"""

@app.get("/debug/api-status")
async def debug_api_status():
    """Debug endpoint to check API key configuration and connectivity"""
    try:
        # Check environment variables
        anthropic_key_status = "CONFIGURED" if ANTHROPIC_API_KEY != "demo_key" else "MISSING"
        polygon_key_status = "CONFIGURED" if POLYGON_API_KEY != "demo_key" else "MISSING"
        
        # Test Anthropic API connectivity
        anthropic_test = "UNTESTED"
        if ANTHROPIC_API_KEY != "demo_key":
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": ANTHROPIC_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        },
                        json={
                            "model": "claude-3-5-haiku-20241022",
                            "max_tokens": 10,
                            "messages": [{"role": "user", "content": "test"}]
                        }
                    )
                    if response.status_code == 200:
                        anthropic_test = "✅ CONNECTED"
                    elif response.status_code == 401:
                        anthropic_test = "❌ INVALID_KEY"
                    elif response.status_code == 404:
                        anthropic_test = "❌ MODEL_NOT_FOUND"
                    else:
                        anthropic_test = f"❌ ERROR_{response.status_code}"
            except Exception as e:
                anthropic_test = f"❌ CONNECTION_ERROR: {str(e)}"
        
        # Test Polygon API connectivity
        polygon_test = "UNTESTED"
        if POLYGON_API_KEY != "demo_key":
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?adjusted=true&apikey={POLYGON_API_KEY}"
                    )
                    if response.status_code == 200:
                        polygon_test = "✅ CONNECTED"
                    elif response.status_code == 401:
                        polygon_test = "❌ INVALID_KEY"
                    else:
                        polygon_test = f"❌ ERROR_{response.status_code}"
            except Exception as e:
                polygon_test = f"❌ CONNECTION_ERROR: {str(e)}"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "api_keys": {
                "anthropic": {
                    "status": anthropic_key_status,
                    "key_prefix": f"{ANTHROPIC_API_KEY[:12]}..." if ANTHROPIC_API_KEY != "demo_key" else "demo_key",
                    "connectivity": anthropic_test
                },
                "polygon": {
                    "status": polygon_key_status,
                    "key_prefix": f"{POLYGON_API_KEY[:8]}..." if POLYGON_API_KEY != "demo_key" else "demo_key",
                    "connectivity": polygon_test
                }
            },
            "environment": {
                "anthropic_env": "SET" if os.getenv("ANTHROPIC_API_KEY") else "MISSING",
                "polygon_env": "SET" if os.getenv("POLYGON_API_KEY") else "MISSING"
            }
        }
        
    except Exception as e:
        return {"error": f"Debug endpoint error: {str(e)}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if user_message:
                # Extract potential stock symbol
                import re
                symbol_match = re.search(r'\\b([A-Z]{1,5})\\b', user_message.upper())
                symbol = symbol_match.group(1) if symbol_match else None
                
                # Get market data if symbol found
                market_data = {}
                if symbol:
                    market_data = await get_market_data(symbol)
                
                # Get AI analysis
                ai_response = await get_ai_analysis(user_message, market_data)
                
                # Send response back
                await manager.send_personal_message(
                    json.dumps({"message": ai_response}), 
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({"message": f"❌ **Error**: {str(e)}"}), 
            websocket
        )
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "polygon_configured": POLYGON_API_KEY != "demo_key",
        "anthropic_configured": ANTHROPIC_API_KEY != "demo_key"
    }

# For production deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)