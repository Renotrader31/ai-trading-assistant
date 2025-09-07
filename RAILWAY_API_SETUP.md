# 🚀 Railway API Keys Setup Guide

## Quick Start - Fix the 404 Errors

Your AI trading assistant is deployed successfully at:
**https://ai-trading-assistant-production.up.railway.app**

The 404 errors you're seeing are because the API keys need to be configured in Railway. Here's how to fix it:

## 🔑 Step 1: Get Your Anthropic API Key

1. **Visit Anthropic Console**: https://console.anthropic.com/
2. **Sign up/Login** with your account
3. **Generate API Key**:
   - Go to "API Keys" section
   - Click "Create Key" 
   - Copy the key (starts with `sk-ant-...`)

## 🛠️ Step 2: Configure Railway Environment Variables

1. **Open Railway Dashboard**: https://railway.app/dashboard
2. **Find Your Project**: "ai-trading-assistant-production"
3. **Go to Variables Tab**:
   - Click on your project
   - Navigate to "Variables" tab
   - Click "New Variable"

4. **Add Required Variables**:

### Primary API Key (REQUIRED)
```
Variable Name: ANTHROPIC_API_KEY
Variable Value: sk-ant-api03-[your-actual-api-key-here]
```

### Optional: Polygon.io API Key (for real market data)
```
Variable Name: POLYGON_API_KEY  
Variable Value: [your-polygon-api-key]
```

## 🔧 Step 3: Deploy Changes

1. **Save Variables** in Railway dashboard
2. **Automatic Redeploy**: Railway will automatically redeploy your app
3. **Wait 2-3 minutes** for the deployment to complete

## ✅ Step 4: Test Your Assistant

1. **Visit Your App**: https://ai-trading-assistant-production.up.railway.app
2. **Try These Test Messages**:
   - "What do you think about AAPL?"
   - "Give me swing trading tips"
   - "Analyze the current market sentiment"

## 🎯 Expected Results

### ✅ With API Key Configured:
- Real Claude AI responses with detailed market analysis
- Professional trading recommendations
- Enhanced formatting with emojis and markdown

### ❌ Without API Key (current state):
- Error: "AI service returned 404"
- Demo mode responses only

## 🔍 Troubleshooting

### Issue: Still getting 404 errors
**Solution**: 
1. Verify API key is correctly copied (no extra spaces)
2. Check Railway Variables tab shows the key is set
3. Wait for automatic redeploy to complete

### Issue: "Invalid API Key" (401 error)  
**Solution**:
1. Generate a new API key from Anthropic Console
2. Ensure key starts with `sk-ant-api03-`
3. Update the Railway variable with new key

### Issue: "Model not found" error
**Solution**:
- The app now includes fallback models
- Should work with any valid Anthropic API key
- Contact Anthropic support if access issues persist

## 💰 API Costs (Anthropic Claude)

- **Claude 3.5 Haiku**: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- **Claude 3.5 Sonnet**: $3 per 1M input tokens, $15 per 1M output tokens

**Estimated Cost**: $0.01 - $0.05 per trading analysis query

## 🚀 Next Steps

Once API keys are working:
1. **Test real market queries** with current stocks
2. **Add Polygon.io key** for live market data
3. **Customize trading strategies** for your needs

---

**Need Help?** The app includes detailed error messages to help diagnose API key issues.