# ConsultantOS MVP Demo - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- Terminal access

### Step 1: Start Backend (2 minutes)
```bash
# From project root
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS

# Install dependencies (if not done)
pip install -r requirements.txt

# Start backend server
python main.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

### Step 2: Start Frontend (2 minutes)
```bash
# Open new terminal window
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected Output**:
```
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

### Step 3: Open Demo (30 seconds)
1. Open browser to: `http://localhost:3000/mvp-demo`
2. You should see the MVP demo page with Chat (left) and Forecast (right)

---

## 🎯 Demo Checklist

Before presenting, verify:
- [ ] Backend shows "Backend Online" (green indicator)
- [ ] Chat interface loads without errors
- [ ] Forecast chart displays with data
- [ ] No console errors (F12 → Console tab)

---

## 💬 Demo Script (6 Minutes)

### Introduction (30 seconds)
"Welcome to ConsultantOS - an AI-powered competitive intelligence platform built for this hackathon in just 2 days."

### Feature 1: AI Chat Assistant (2 minutes)
**Action**: Click into chat input field

"Our first feature is an intelligent chat assistant powered by Google Gemini 1.5."

**Type**: "What is competitive intelligence?"

**While waiting for response**:
- "The backend is processing this query through our FastAPI server"
- "It's being analyzed by Google's Gemini 1.5 AI model"
- "Responses typically take 2-3 seconds"

**When response appears**:
- "Notice the clean message interface"
- "Timestamps for each message"
- "Auto-scrolling to keep latest messages visible"

**Type follow-up**: "How can AI help with market analysis?"

"The system maintains conversation context, allowing for natural multi-turn dialogues."

### Feature 2: Market Forecast (2 minutes)
**Action**: Point to forecast chart on right

"Our second feature is an AI-powered market forecasting system."

**Key Points**:
- "Line chart shows predicted market trends"
- "Shaded areas represent confidence intervals"
- "Currently showing 30-day forecast"

**Action**: Change dropdown to "90 Days"

"The forecast is dynamic - we can easily adjust the time horizon."

**Point to statistics**:
- "Current value, predicted value, and percentage change"
- "95% confidence score indicates high prediction reliability"

### Technology Stack (1 minute)
**Action**: Scroll to footer

"The tech stack powering this demo:"

**Backend**:
- Python FastAPI for high-performance APIs
- Google Gemini 1.5 for AI intelligence
- Deployed on Google Cloud Run for scalability

**Frontend**:
- Next.js 14 with React 18
- TypeScript for type safety
- Recharts for data visualization
- Tailwind CSS for modern styling

### Responsive Design (30 seconds)
**Action**: Resize browser window

"The interface is fully responsive - works seamlessly on desktop, tablet, and mobile devices."

### Q&A (Remaining time)
"Happy to answer any questions about the implementation, architecture, or future roadmap!"

---

## 🐛 Troubleshooting

### Backend Not Running
**Symptom**: Red "Backend Offline" indicator

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8080/mvp/health

# If no response, start backend
python main.py
```

### Frontend Not Loading
**Symptom**: Page shows 404 or blank screen

**Solution**:
```bash
# Restart frontend
cd frontend
npm run dev
```

### Chat Not Responding
**Symptom**: Messages sent but no response

**Check**:
1. Browser console (F12) for errors
2. Backend logs for errors
3. Network tab to see if API calls succeed

**Common Fix**:
```bash
# Restart backend with fresh logs
python main.py
```

### Forecast Chart Not Rendering
**Symptom**: Blank right panel

**Check**:
1. Browser console for Recharts errors
2. Network tab for `/mvp/forecast` API call

**Fix**:
```bash
# Ensure dependencies installed
cd frontend
npm install recharts
```

### CORS Errors
**Symptom**: "CORS policy" errors in console

**Fix**: Backend is configured for localhost:3000. Ensure frontend is running on port 3000.

---

## 📊 Demo Data Examples

### Good Chat Questions to Ask:
1. "What is competitive intelligence?"
2. "How can AI improve market analysis?"
3. "What are the key components of a competitive strategy?"
4. "Explain Porter's Five Forces framework"
5. "What role does data play in strategic planning?"

### Forecast Scenarios to Show:
- **7 Days**: Short-term tactical predictions
- **30 Days**: Monthly planning horizon
- **90 Days**: Quarterly strategic forecast

---

## 🎨 Visual Presentation Tips

### Browser Setup:
- Use Chrome or Firefox (best compatibility)
- Full screen mode (F11)
- Zoom at 100% or 110% for better visibility
- Close unnecessary tabs
- Disable notifications

### Window Size:
- Minimum: 1280x800
- Recommended: 1440x900 or 1920x1080
- Split screen works well at 1920px+

### Demo Flow:
1. Start on homepage to show full platform
2. Click "Try MVP Demo" for dramatic reveal
3. Demonstrate chat first (more interactive)
4. Show forecast with period changes
5. Highlight responsive design
6. End with tech stack callout

---

## 📸 Screenshot Opportunities

Great moments to capture:
1. Homepage with "Try MVP Demo" button
2. Full MVP demo page (split screen)
3. Chat conversation in progress
4. Forecast chart with 90-day view
5. Mobile view (resize browser)
6. Backend health indicator (green)

---

## ⏱️ Time Management

**6-Minute Demo Breakdown**:
- Introduction: 30s
- Chat demo: 2m
- Forecast demo: 2m
- Tech stack: 1m
- Responsive design: 30s
- Q&A: Remaining

**10-Minute Extended Demo**:
- Add live coding explanation (+2m)
- Show API responses in Network tab (+1m)
- Demonstrate error handling (+1m)

**3-Minute Lightning Demo**:
- Quick intro: 20s
- Chat one question: 1m
- Forecast show chart: 1m
- Tech stack mention: 20s
- Rapid Q&A: 20s

---

## 🔐 Security Notes

**Demo Environment**:
- No authentication required for MVP
- Data is ephemeral (not persisted)
- Safe for public demonstration
- No sensitive information displayed

**Production Considerations**:
- Would add OAuth authentication
- Implement rate limiting
- Add data encryption
- Enable audit logging

---

## 📝 Post-Demo Actions

After successful demo:
1. ✅ Thank attendees
2. ✅ Share GitHub repository link
3. ✅ Provide contact information
4. ✅ Mention availability for Q&A
5. ✅ Collect feedback

---

## 🚀 Future Roadmap (Optional Mention)

**Phase 1** (Post-Hackathon):
- User authentication
- Data persistence (Firestore)
- Enhanced forecast metrics

**Phase 2** (Month 2):
- Multi-metric comparisons
- Export capabilities
- Dashboard customization

**Phase 3** (Month 3):
- Real-time WebSocket updates
- Mobile native apps
- Enterprise features

---

## 📞 Support During Demo

**If Something Breaks**:
1. Stay calm - explain it's a live demo
2. Check browser console for quick fix
3. Have backup screenshots ready
4. Transition to architecture discussion

**Backup Plan**:
- Screenshots in `/docs/screenshots/`
- Recorded demo video (if available)
- Architecture diagrams
- Code walkthrough

---

## ✅ Final Checklist

Before going live:
- [ ] Backend running and healthy
- [ ] Frontend running on port 3000
- [ ] Browser window clean and ready
- [ ] Demo script reviewed
- [ ] Questions anticipated
- [ ] Backup plan ready
- [ ] Screenshots captured
- [ ] Confidence level: HIGH

---

**Good luck with your demo! 🎉**

Built with ❤️ for the November 2025 Hackathon
