# 🎬 Demo Questions - Quick Reference

## ✅ **GUARANTEED TO WORK** (Use for demos)

### **🏆 Best Demo Questions**
```
1. "Compare average rainfall in Maharashtra and Punjab"
2. "Which state has the highest rice production?"  
3. "Show me cotton production trend from 2010 to 2014"
4. "Correlation between rainfall and rice production"
```

### **🌾 Agriculture Questions**
- Compare rice production in Maharashtra and Punjab
- Which state has the highest wheat production?
- Average crop production in Karnataka
- Total sugarcane production across all states
- Production trend of groundnut from 2005 to 2012
- Top 5 states by rice production

### **🌧️ Climate Questions**  
- Compare average rainfall in Maharashtra and Punjab
- Which state receives the highest annual rainfall?
- Rainfall trend in Tamil Nadu from 2001 to 2010
- Average monsoon rainfall in Gujarat
- Monthly rainfall distribution in West Bengal

### **📊 Advanced Analytics**
- Correlation between rainfall and rice production
- Impact of rainfall on crop yield in Punjab
- Relationship between precipitation and agricultural output
- Compare rainfall and production patterns in Maharashtra

## ❌ **AVOID FOR DEMOS** (Live API issues)

### **💰 Market Price Questions** (Currently failing)
- ~~"What are current crop prices in Maharashtra?"~~
- ~~"Latest market rates for wheat"~~
- ~~"Recent commodity prices in Punjab"~~
- ~~"Live mandi prices today"~~

### **📈 Current Data Questions** (Currently failing)
- ~~"Current crop production in Gujarat"~~
- ~~"Latest agricultural output data"~~
- ~~"Recent harvest data for cotton"~~

## 🎯 **Demo Script Template**

### **Opening (30 seconds)**
*"I'll demonstrate how Project Samarth answers complex questions about Indian agriculture using natural language."*

### **Question 1: Comparison (30 seconds)**
**Ask:** *"Compare average rainfall in Maharashtra and Punjab"*
**Show:** Data table, citations, processing time (~200ms)

### **Question 2: Ranking (30 seconds)**  
**Ask:** *"Which state has the highest rice production?"*
**Show:** Ranking results, multiple data sources

### **Question 3: Advanced (45 seconds)**
**Ask:** *"Correlation between rainfall and rice production"*
**Show:** Statistical analysis, cross-domain insights

### **Provenance Demo (15 seconds)**
**Click:** "Show Provenance" → SQL transparency, audit trail

## 💡 **Pro Tips**

- **Fast Response**: Historical queries respond in ~200ms
- **Rich Data**: Each answer includes citations and provenance  
- **Visual Appeal**: Data tables and trend information
- **Government Focus**: All data sourced from official ministries
- **Cross-Domain**: Agriculture + climate integration

## 🚨 **Troubleshooting**

**If you get "No live data available":**
1. Remove words: "current", "latest", "recent", "live"
2. Use historical timeframes: "from 2010 to 2014"
3. Stick to the guaranteed working questions above

**Backend not responding:**
1. Check if `python run_server.py` is running
2. Verify http://localhost:8000/health works
3. Use live demo: https://samarth-two.vercel.app

---

**🎬 Stick to historical questions for flawless demos!**