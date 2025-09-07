# 🚀 AI Trading Assistant

Beautiful AI-powered trading platform with real-time market data and enhanced Claude AI analysis.

## ✨ Features

- **🤖 AI Analysis**: Real-time Claude AI integration for trading insights
- **📊 Live Market Data**: Polygon.io API for real-time stock data
- **💬 Interactive Chat**: WebSocket-powered real-time chat interface  
- **🎨 Beautiful UI**: Dark gradient theme with glass morphism effects
- **📱 Mobile Ready**: Fully responsive design
- **⚡ Enhanced Formatting**: Color-coded, structured AI responses

## 🚀 Quick Deploy

### Railway.app (Recommended)
1. Push this repo to GitHub
2. Connect Railway to your GitHub repo
3. Add environment variables:
   - `POLYGON_API_KEY` - Your Polygon.io API key
   - `ANTHROPIC_API_KEY` - Your Claude API key
4. Deploy automatically!

### Render.com
1. Connect your GitHub repo to Render
2. Set environment variables
3. Deploy with zero configuration

### fly.io
1. `fly launch`
2. `fly secrets set POLYGON_API_KEY=your_key ANTHROPIC_API_KEY=your_key`
3. `fly deploy`

## 🎯 Usage

Once deployed:
- Ask about any stock symbol (AAPL, TSLA, NVDA, etc.)
- Get AI-powered trading analysis and recommendations
- View real-time market data and technical indicators
- Receive enhanced formatted responses with financial highlights

## 🔧 Technical Stack

- **Framework**: FastAPI with WebSocket support
- **AI**: Anthropic Claude API integration
- **Market Data**: Polygon.io REST API
- **Frontend**: Embedded HTML with Tailwind CSS + FontAwesome
- **Deployment**: Production-ready with proper error handling

Built with ❤️ for professional traders! 📈