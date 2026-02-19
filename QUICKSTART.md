# 🚀 Quick Start Guide - 5 Minutes

Get the AI-powered lead generation system running in 5 minutes.

## ✅ Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] OpenAI API key (get at https://platform.openai.com/api-keys)
- [ ] Serper API key (provided: `7d96d845cbccec41f1f2b35b0d0da05cef94c149`)

## 📦 Step 1: Install (2 minutes)

```bash
# Navigate to project directory
cd SerperDev

# Install dependencies
pip install -r requirements_ui.txt
```

**What this installs:**
- `streamlit` - Web interface
- `openai` - AI query generation
- `pandas` - Data handling
- `plotly` - Charts

## 🎮 Step 2: Launch UI (30 seconds)

```bash
streamlit run app.py
```

**Result:**
- Browser opens automatically at `http://localhost:8501`
- You'll see the main interface

## 🔑 Step 3: Enter API Keys (1 minute)

In the **sidebar**:

1. **OpenAI API Key**: Paste your key
2. **Serper API Key**: Already filled (or use your own)

## ⚙️ Step 4: Configure Search (1 minute)

Fill in the form:

```
Sector: lanyard
Customer Profile: B2B suppliers selling custom lanyards for events
Countries: US
Cities per Country: 5
Maximum Total Queries: 1000
Native Language: ✓ (checked)
```

Click **"Generate AI Query Plan"**

## 🤖 Step 5: Review AI Plan (30 seconds)

AI generates:
- 12-15 query variations
- 5 recommended cities
- Optimization strategy

**Review the queries and cities**

If good → Click **"Start Search Execution"**

If not → Provide feedback and regenerate

## ✅ Done!

The system will:
1. Search across 5 US cities
2. Execute ~1000 API calls
3. Find 3,000-5,000 businesses
4. **NEW**: Capture Google's related searches and autocomplete suggestions
5. Export to CSV (main results + related searches)

**Time: ~10-15 minutes**

---

## 💡 Tips for First Run

### **Start Small**
```
Countries: 1
Cities: 3
Max Queries: 500
```

This gives you ~1,500 leads in 5 minutes

### **Test AI Generation First**
Just go through steps 1-5 without executing

Verify:
- Queries make sense for your sector
- City selection is appropriate
- Translations are correct (if enabled)

### **Understand the Output**

**Main Results CSV:**
```csv
domain,url,title,description,country,city,query
customlanyard.com,https://...,Custom Lanyards Inc,...,US,New York,lanyard supplier
eventpromo.com,https://...,Event Promotional Products,...,US,Los Angeles,custom lanyard
```

**Related Searches CSV (NEW - January 2026):**
```csv
original_query,related_search
custom lanyard manufacturer,Custom lanyard manufacturer usa
custom lanyard manufacturer,Custom lanyards no minimum
custom lanyard manufacturer,High-quality custom lanyards
```

---

## 🐛 Common First-Time Issues

### **Issue: Streamlit won't start**

```bash
# Try this instead:
python -m streamlit run app.py
```

### **Issue: OpenAI error "Invalid API key"**

**Check:**
1. Key copied correctly (no extra spaces)
2. Billing enabled at https://platform.openai.com/account/billing
3. API key not revoked

### **Issue: No results showing**

**Likely:**
- Network proxy blocking Serper API
- Try from different network
- Check Serper API key is valid

---

## 📊 What to Expect

### **Performance (5 cities, 1000 queries)**

| Metric | Value |
|--------|-------|
| AI Generation | 10-20 seconds |
| Search Execution | 10-15 minutes |
| Total Results | 3,000-6,000 |
| Unique Domains | 2,000-4,000 |
| API Calls Used | ~1,000 |
| Cost | ~$10 |

### **Data Quality**

- ✅ Real business websites
- ✅ Deduplicated by domain
- ✅ Includes title + description
- ✅ Location tagged
- ✅ Source query tracked

### **Next Steps After First Run**

1. **Review Results**: Open CSV, spot-check quality
2. **Adjust Queries**: If needed, provide feedback to AI
3. **Scale Up**: Increase to 10 cities, 5000 queries
4. **Go Multi-Country**: Add UK, CA, AU

---

## 🎯 Quick Reference

### **Optimal Settings for Different Use Cases**

**Small Test Run:**
```
Countries: 1
Cities: 3
Queries: 500
Duration: 5-8 minutes
Cost: $5
Results: ~1,500
```

**Medium Campaign:**
```
Countries: 2-3
Cities: 10
Queries: 2,000
Duration: 20-30 minutes
Cost: $20
Results: ~8,000
```

**Large Campaign:**
```
Countries: 5+
Cities: 20
Queries: 10,000
Duration: 90-120 minutes
Cost: $100
Results: ~40,000
```

---

## 📞 Need Help?

1. **Read Full Docs**: `README_UI.md`
2. **Check Config**: `config/countries.py`, `config/queries.py`
3. **Test Components**:
   - AI: `python ai_query_generator.py`
   - Search: `python serper_search_v2.py`

---

**You're all set! 🎉**

Run `streamlit run app.py` and start generating leads!
