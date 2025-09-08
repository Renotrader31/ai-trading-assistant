# Real-Time API Debugging Guide

## Problem Summary
The AI Trading Assistant is returning `"data_source": "api_fallback"` instead of live Polygon.io data, even though the real-time API implementation is in place.

## 🚀 Quick Fixes Applied

### 1. Enhanced Error Handling & Debugging
- ✅ Improved `get_market_data()` function with detailed logging
- ✅ Added specific error handling for 401 (Unauthorized) and 403 (Forbidden) responses
- ✅ Enhanced timeout handling (increased to 15 seconds)
- ✅ Better JSON parsing with try/catch blocks

### 2. Added Comprehensive Diagnosis Endpoint
- ✅ New endpoint: `GET /diagnosis/realtime/{symbol}`
- ✅ Tests every step of the real-time API pipeline
- ✅ Provides detailed error reporting and recommendations

## 🔍 Debugging Steps for Railway Deployment

### Step 1: Deploy the Enhanced Code
```bash
git add .
git commit -m "Enhanced real-time API with comprehensive debugging"
git push origin main
```

### Step 2: Test the New Diagnosis Endpoint
Visit your Railway app URL and test:
```
https://your-app.railway.app/diagnosis/realtime/AMZN
```

This will show you exactly what's failing in the API pipeline.

### Step 3: Check Environment Variables in Railway
Verify in your Railway dashboard:
1. Go to your project → Variables tab
2. Confirm `POLYGON_API_KEY` is set and has the correct value
3. The key should be ~32 characters long (not 8 characters like "demo_key")

### Step 4: Test API Key Permissions
The diagnosis endpoint will tell you if you get:
- **401 Unauthorized**: Invalid API key
- **403 Forbidden**: Valid key but lacks real-time data permissions
- **200 Success**: Key works, look for other issues

## 🔧 Most Likely Issues & Solutions

### Issue 1: Missing Environment Variable
**Symptoms:** API key shows as "demo_key" or 8 characters
**Solution:** Set `POLYGON_API_KEY` in Railway environment variables

### Issue 2: Invalid API Key  
**Symptoms:** 401 Unauthorized responses
**Solution:** Verify the API key in Polygon.io dashboard and re-set in Railway

### Issue 3: Insufficient API Permissions
**Symptoms:** 403 Forbidden responses for `/v2/last/trade` endpoint
**Solution:** Upgrade your Polygon.io plan to include real-time data access

### Issue 4: Rate Limiting
**Symptoms:** Intermittent failures, occasional 429 responses
**Solution:** The enhanced code includes better timeout handling

## 📊 What the Enhanced Code Does

### Real-Time Data Flow:
1. **Step 1:** Fetch current price from `/v2/last/trade/{symbol}` (LIVE data)
2. **Step 2:** Fetch previous close from `/v2/aggs/ticker/{symbol}/prev` (for change calculation)
3. **Step 3:** Calculate change: `current_price - previous_close`
4. **Step 4:** Return data with `"data_source": "polygon_real_time"`

### Enhanced Error Tracking:
- `polygon_real_time`: ✅ Success with live current price
- `polygon_previous_close`: ⚠️ Real-time failed, using previous close
- `unauthorized_error`: ❌ Invalid API key
- `permission_error`: ❌ Key lacks real-time permissions  
- `api_fallback`: ❌ All API calls failed
- `error_fallback`: ❌ Exception occurred

## 🎯 Testing Commands

After deployment, test these endpoints:

```bash
# 1. Test the diagnosis endpoint
curl https://your-app.railway.app/diagnosis/realtime/AMZN

# 2. Test the market data endpoint directly  
curl https://your-app.railway.app/debug/market/AMZN

# 3. Test environment variables
curl https://your-app.railway.app/debug/env

# 4. Test API status
curl https://your-app.railway.app/debug/api-status
```

## 🔍 Reading the Debug Output

### Good Response (Working):
```json
{
  "symbol": "AMZN", 
  "price": 236.99,
  "data_source": "polygon_real_time",
  "live_data": true,
  "api_success": true
}
```

### Bad Response (Still Failing):
```json
{
  "symbol": "AMZN",
  "price": 150.00,
  "data_source": "api_fallback", 
  "live_data": false,
  "note": "All API calls failed"
}
```

## 🚨 If Still Not Working

If you're still getting fallback data after deploying these fixes:

1. **Check Railway Logs**: Look for the detailed console output from the enhanced logging
2. **Verify API Key Format**: Should be ~32 characters, not "demo_key"
3. **Test API Key Directly**: Use the diagnosis endpoint to see the exact error
4. **Check Polygon Plan**: Ensure your plan includes real-time market data access

## 📝 Next Steps

Once live data is working:
1. ✅ Verify AMZN shows current price (not previous day)
2. ✅ Test with multiple symbols (AAPL, TSLA, GOOGL)
3. ✅ Confirm `data_source` shows "polygon_real_time"
4. 🔄 Return to implementing scanner functionality

## 🆘 Emergency Fallback

If you need to quickly revert to the previous version:
```bash
git log --oneline -5  # Find the previous commit
git revert <commit-hash>  # Revert the changes
git push origin main
```

The enhanced version includes all the debugging tools to identify exactly what's failing in your Railway environment.