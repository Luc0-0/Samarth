# 🎯 Working Questions for Project Samarth

## ✅ **Historical Data Questions** (2001-2014)
*These questions work with the local DuckDB database*

### **🌾 Agriculture Production**
- "Compare rice production in Maharashtra and Punjab"
- "Which state has the highest wheat production?"
- "Show me cotton production trend from 2010 to 2014"
- "Average crop production in Karnataka"
- "Total sugarcane production across all states"
- "Compare area under cultivation for rice vs wheat"
- "Production trend of groundnut from 2005 to 2012"

### **🌧️ Rainfall Analysis**
- "Compare average rainfall in Maharashtra and Punjab"
- "Which state receives the highest annual rainfall?"
- "Rainfall trend in Tamil Nadu from 2001 to 2010"
- "Average monsoon rainfall in Gujarat"
- "Compare rainfall patterns between Kerala and Rajasthan"
- "Monthly rainfall distribution in West Bengal"

### **📊 Cross-Domain Analysis**
- "Correlation between rainfall and rice production"
- "Impact of rainfall on crop yield in Punjab"
- "Relationship between precipitation and agricultural output"
- "Compare rainfall and production patterns in Maharashtra"

### **🏆 Ranking & Comparison**
- "Top 5 states by rice production"
- "Lowest rainfall states in India"
- "Compare productivity of wheat across northern states"
- "Ranking of states by total agricultural area"

## ❌ **Live Data Issues** (Currently Not Working)
*These questions trigger live API calls but fail due to API limitations*

### **💰 Market Prices** (Intended but failing)
- "What are current crop prices in Maharashtra?"
- "Latest market rates for wheat"
- "Recent commodity prices in Punjab"
- "Live mandi prices today"
- "Current price of rice in Karnataka"

### **📈 Current Production** (Intended but failing)
- "Current crop production in Gujarat"
- "Latest agricultural output data"
- "Recent harvest data for cotton"
- "Live production statistics"

## 🔧 **Why Live Data Fails**

### **API Resource ID Issues:**
1. **Hardcoded IDs**: Using fixed resource IDs that may not exist
2. **API Changes**: Government APIs change resource IDs frequently  
3. **Authentication**: API key may need refresh or different permissions
4. **Data Format**: API response format may have changed

### **Current Resource IDs in Code:**
```python
# These may be outdated/invalid:
"9ef84268-d588-465a-a308-a864a43d0070"  # Market prices
"3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"  # Agriculture production
```

## 🎯 **Recommended Demo Questions**

### **For Presentations** (Guaranteed to work)
1. **"Compare average rainfall in Maharashtra and Punjab"**
   - Shows comparison capability
   - Fast response (~200ms)
   - Clear data visualization

2. **"Which state has the highest rice production?"**
   - Demonstrates ranking
   - Shows agricultural focus
   - Good for government audience

3. **"Show me cotton production trend from 2010 to 2014"**
   - Trend analysis capability
   - Time series data
   - Visual charts

4. **"Correlation between rainfall and rice production"**
   - Cross-domain analysis
   - Statistical insights
   - Advanced analytics

### **For Technical Demos**
1. **"Compare rice vs wheat production across northern states"**
2. **"Average monsoon rainfall impact on crop yield"**
3. **"Top 5 agricultural states by total production"**

## 🚀 **Quick Fix for Live Data**

To make live data work, you need to:

1. **Update Resource IDs**: Get current IDs from data.gov.in
2. **Test API Key**: Verify it works with current endpoints
3. **Handle API Changes**: Add better error handling
4. **Fallback Strategy**: Show historical data when live fails

## 💡 **Pro Tips**

- **Use "average" or "compare"** for reliable results
- **Specify states** for faster queries  
- **Avoid "current/latest"** until live API is fixed
- **Include time ranges** for trend analysis
- **Use crop names** from the supported list: rice, wheat, cotton, sugarcane, etc.

---

**🎬 For demos, stick to historical questions - they're fast, reliable, and showcase the system's intelligence perfectly!**