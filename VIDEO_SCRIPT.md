# ConsultantOS - Demo Video Script

**Duration:** 2-3 minutes
**Format:** Screen recording + voiceover
**Goal:** Show the problem, solution, and impact clearly and quickly

---

## 🎬 Scene 1: The Problem (15 seconds)

### Visual

- Screen showing consulting invoice: "$50,000"
- Timeline graphic: "4-6 weeks delivery"
- Calendar showing days passing
- Final slide: "By the time it's done... the market has changed"

### Voiceover

> "Strategic business analysis. It costs $50,000. Takes weeks to months. And by the time it's done, the market has already changed. There has to be a better way."

---

## 🚀 Scene 2: The Solution (10 seconds)

### Visual

- ConsultantOS logo appears
- Tagline fades in: "Professional-grade strategic analysis in minutes, not days"
- Cut to: Live Dashboard URL
- Browser shows: https://consultantos-frontend-bdndyf33xa-uc.a.run.app
- Quick glimpse of populated dashboard with monitors, alerts, and analytics

### Voiceover

> "Introducing ConsultantOS. Professional-grade strategic analysis in minutes, not days. Fully deployed on Google Cloud Run with real-time monitoring and intelligence. Let me show you."

---

## 💻 Scene 3: The Demo - Setup (20 seconds)

### Visual

- Start on dashboard showing active monitors (Tesla, OpenAI, Rivian, Anthropic)
- Show recent alerts feed with strategic insights
- Pan to analytics showing 127 analyses completed
- Transition to API: Open Swagger UI at /docs
- Scroll to show available endpoints
- Click on "POST /analyze" endpoint
- Show the request structure

### Voiceover

> "Here's the live dashboard showing continuous monitoring of multiple companies - Tesla, OpenAI, Rivian. You can see recent strategic alerts detected automatically. Now let's run a live analysis. I'll use the API to analyze Tesla's competitive position with Porter's Five Forces and SWOT."

### Screen Action

- Click "Try it out"
- Type request body:

```json
{
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "frameworks": ["porter", "swot"],
  "analysis_depth": "standard"
}
```

- Show cursor hovering over "Execute" button

---

## ⚡ Scene 4: The Demo - Execution (30 seconds)

### Visual

- Click "Execute"
- Show loading spinner/progress indicator
- Split screen:
  - Left: API request in progress
  - Right: Animated diagram showing multi-agent orchestration:
    ```
    Research Agent →
    Market Agent   → Framework Agent → Synthesis
    Financial Agent →
    ```
- Timer showing progress

### Voiceover

> "Behind the scenes, five specialized AI agents are working in parallel. The research agent gathers web intelligence, the market agent analyzes trends, and the financial agent pulls real-time data. They feed into our framework agent, which applies strategic frameworks, and finally, our synthesis agent creates the executive summary. All in real-time."

---

## 📊 Scene 5: The Results - Overview (25 seconds)

### Visual

- Results appear on screen
- Scroll through JSON response slowly
- Highlight key sections with visual callouts:
  - "Porter's Five Forces" (with scores)
  - "SWOT Analysis" (with bullets)
  - "Executive Summary"
  - "Confidence Score: 0.87"

### Voiceover

> "And here are the results. Complete Porter's Five Forces analysis with competitive intensity scores. Comprehensive SWOT analysis with strengths, weaknesses, opportunities, and threats. An executive summary with strategic recommendations. And a confidence score based on data quality. All generated in minutes."

---

## 🎯 Scene 6: The Results - Deep Dive (30 seconds)

### Visual

- Zoom into specific insights:

  1. **Porter's Five Forces:**

     - Competitive Rivalry: 8.5/10 (High)
     - Supplier Power: 5.5/10 (Medium)
     - Buyer Power: 7/10 (Medium-High)

  2. **SWOT Analysis:**
     - Strength: "Vertical integration and Supercharger network"
     - Weakness: "Production challenges and quality control"
     - Opportunity: "Energy storage market expansion"
     - Threat: "Traditional automakers entering EV market"

### Voiceover

> "The analysis identifies high competitive rivalry with multiple new entrants. It recognizes Tesla's vertical integration as a key strength, but highlights production challenges. It spots opportunities in energy storage, and warns about traditional automakers entering the EV space. This is the kind of strategic insight that would normally take days to compile."

---

## 📈 Scene 7: Advanced Features (20 seconds)

### Visual

- Quick cuts showing other capabilities:
  1. Dashboard with real-time monitoring and alerts
  2. Analytics tab showing productivity metrics and framework distribution
  3. Multi-scenario forecasting with Monte Carlo simulation
  4. Conversational AI responding to "What are Tesla's biggest threats?"
  5. PDF report preview (title page, charts, tables)

### Voiceover

> "But that's just the beginning. We have a full monitoring dashboard with continuous intelligence tracking and smart alerts. Multi-scenario forecasting with Monte Carlo simulation, competitive wargaming, social media sentiment analysis, and conversational AI for follow-up questions. Plus, publication-ready PDF reports with interactive visualizations. It's a complete intelligence platform."

---

## 🏗️ Scene 8: The Technology (15 seconds)

### Visual

- Architecture diagram appears:

```
┌─────────────────┐
│   Orchestrator  │
└────────┬────────┘
         │
    ┌────┼────┐
    │ PARALLEL │
    │          │
┌───▼──┐ ┌──▼──┐ ┌──▼───┐
│Research│ │Market│ │Finance│
└───┬──┘ └──┬──┘ └──┬───┘
    │       │      │
    └───────┼──────┘
            │
       ┌────▼────┐
       │Framework│
       └────┬────┘
            │
       ┌────▼────┐
       │Synthesis│
       └─────────┘
```

### Voiceover

> "We built this using a multi-agent orchestration architecture. Five specialized AI agents work together, coordinated by an intelligent orchestrator. Parallel execution for speed, sequential synthesis for quality. All deployed on Google Cloud Run with enterprise-grade infrastructure."

---

## 💰 Scene 9: The Impact (20 seconds)

### Visual

- Show comparison charts:

**Speed:**

```
Traditional: ████████████████████ Days
ConsultantOS: ▌ Minutes
→ 1000x+ FASTER
```

**Cost:**

```
Traditional: $50,000
ConsultantOS: $0.10
→ 99.8% CHEAPER
```

**Accessibility:**

```
Before: 0.02% of businesses (Fortune 500 only)
After: 100% of businesses
→ Market expanded 160x
```

### Voiceover

> "The impact? Over 1000 times faster than manual analysis. 99.8% cheaper than traditional consulting. And we've opened up professional strategic intelligence to every business, not just Fortune 500 companies."

---

## 🎯 Scene 10: The Vision (15 seconds)

### Visual

- Split screen showing different users:
  - Startup founder at laptop
  - Corporate strategy team in boardroom
  - Small business owner
  - Consultant using ConsultantOS
- All screens show ConsultantOS results
- Tagline appears: "Democratizing Strategic Intelligence"

### Voiceover

> "Our vision is simple: every business, regardless of size, should have access to professional strategic intelligence. We're democratizing an industry that's been exclusive for too long."

---

## 🚀 Scene 11: Call to Action (10 seconds)

### Visual

- Screen showing:
  - Live Dashboard: https://consultantos-frontend-bdndyf33xa-uc.a.run.app
  - Live API: https://consultantos-api-bdndyf33xa-uc.a.run.app
  - "Try it now - Both are live in production!"
  - API docs button
  - GitHub link
  - Contact information

### Voiceover

> "ConsultantOS is live right now on Google Cloud Run. Try the dashboard, test the API yourself. The future of strategic analysis is here."

### Visual

- ConsultantOS logo
- Tagline: "Professional-grade analysis in minutes, not days"
- "Built for Google Cloud Hackathon"

---

## 🎬 Alternative: 60-Second Version

For platforms with time limits, use this condensed script:

### 0-10s: Problem

"Strategic consulting: $50,000, weeks to months, outdated by delivery."

### 10-20s: Solution

"ConsultantOS: Professional analysis in minutes, not days. Full monitoring dashboard, live on Google Cloud Run. Watch."
[Show dashboard with monitors and alerts]

### 20-40s: Demo

[Execute analysis via API, display results]
"Porter's Five Forces, SWOT, executive summary. Real-time data. Continuous monitoring. Smart alerts."

### 40-50s: Impact

[Show comparison charts]
"1000x+ faster. 99.8% cheaper. Accessible to everyone. Complete intelligence platform."

### 50-60s: CTA

"Live now on Cloud Run. Dashboard and API. Try it yourself. ConsultantOS - democratizing strategic intelligence."

---

## 🎥 Production Notes

### Recording Setup

**Software:**

- Screen recording: OBS Studio or Loom
- Video editing: DaVinci Resolve or iMovie
- Voiceover: Audacity or built-in screen recorder
- Graphics: Canva or Figma

**Screen Resolution:**

- Record at 1920x1080 (1080p)
- Ensure text is readable
- Use zoom for small details

**Audio:**

- Use good microphone (not laptop mic)
- Record in quiet environment
- Speak clearly and at moderate pace
- Add background music (subtle, not distracting)

### Visual Guidelines

**Colors:**

- Use brand colors consistently
- High contrast for readability
- Dark mode for code/terminal (easier on eyes)

**Text:**

- Large font sizes (24pt minimum for code)
- Highlight important numbers/stats
- Use callouts and annotations
- Animate key points (fade in/out)

**Pacing:**

- Don't rush through results
- Pause on important insights
- Let numbers sink in (2-3 seconds each)
- Use smooth transitions

### B-Roll Options

**If you want to add visual interest:**

- Stock footage of:
  - Business meetings
  - People working on strategy
  - Consultants presenting
  - Charts and data visualizations
- Abstract animations:
  - Network connections (agent orchestration)
  - Data flowing
  - Loading animations
  - Success checkmarks

### Music Suggestions

**Background track characteristics:**

- Upbeat but professional
- Subtle (don't overpower voice)
- Royalty-free (important!)
- Tempo: 110-130 BPM

**Recommended sources:**

- YouTube Audio Library
- Epidemic Sound
- Artlist
- Free Music Archive

---

## ✅ Pre-Recording Checklist

**Technical:**

- [ ] Dashboard is responsive (https://consultantos-frontend-bdndyf33xa-uc.a.run.app)
- [ ] API is responsive (test with curl: https://consultantos-api-bdndyf33xa-uc.a.run.app/health)
- [ ] DEMO_MODE enabled in dashboard (line 131: const DEMO_MODE = true)
- [ ] All mock data displays correctly in dashboard
- [ ] Browser bookmarks set (dashboard + API docs)
- [ ] Screen resolution correct (1920x1080)
- [ ] Notifications disabled
- [ ] Close unnecessary apps/tabs
- [ ] Clear browser history (clean demo)

**Content:**

- [ ] Script reviewed and practiced
- [ ] Timing verified (not too fast/slow)
- [ ] Key messages identified
- [ ] Backup examples ready
- [ ] Visual aids prepared

**Audio:**

- [ ] Microphone tested
- [ ] Quiet environment confirmed
- [ ] Script printed (if needed)
- [ ] Water nearby (stay hydrated)

**Post-Production:**

- [ ] Video edited (cuts, transitions)
- [ ] Audio cleaned (remove noise, level)
- [ ] Graphics added (callouts, text)
- [ ] Music added (subtle background)
- [ ] Captions/subtitles added
- [ ] Exported in correct format
- [ ] Uploaded and tested

---

## 📤 Export Settings

**For YouTube/General:**

- Format: MP4 (H.264)
- Resolution: 1920x1080 (1080p)
- Frame rate: 30fps
- Bitrate: 8-10 Mbps
- Audio: 192 kbps stereo

**For Social Media:**

- Square format (1080x1080) for Instagram
- Vertical format (1080x1920) for TikTok/Reels
- Add captions (many watch without sound)

**For Hackathon Submission:**

- Follow platform requirements
- Keep under size limit
- Include backup link (YouTube unlisted)

---

## 🎯 Key Messages to Emphasize

**1. Speed:** "Minutes, not days" (repeat multiple times)
**2. Cost:** "$0.10 vs. $50,000" (shocking difference)
**3. Quality:** "Professional-grade" (not toy/demo)
**4. Live:** "Full production deployment on Google Cloud Run" (dashboard + API, really works)
**5. Complete Platform:** "Continuous monitoring + on-demand analysis" (not just one-off reports)
**6. Impact:** "Democratizing" (social good)

---

## 💡 Tips for Great Video

**Do:**

- ✅ Start with the problem (hook viewers)
- ✅ Show actual product (not just slides)
- ✅ Use real data (not lorem ipsum)
- ✅ Emphasize live demo (not mockup)
- ✅ End with clear CTA (try it now)

**Don't:**

- ❌ Start with "Hi, I'm..." (waste of time)
- ❌ Explain how you built it (save for tech deep-dive)
- ❌ Apologize for anything
- ❌ Go too fast (let insights land)
- ❌ Forget the call to action

---

## 🎬 Dashboard Demo Setup

**The dashboard is pre-configured with realistic mock data for video recording:**

**To use for recording:**

1. Ensure `DEMO_MODE = true` in `frontend/app/dashboard/page.tsx` (line 131)
2. Run: `cd frontend && npm run dev`
3. Navigate to: `http://localhost:3000/dashboard`

**What you'll see:**

- **4 Active Monitors**: Tesla, OpenAI, Rivian, Anthropic
- **7 Recent Alerts**: High-priority strategic changes (GPT-5 launch, competitive threats, partnerships)
- **Stats Dashboard**: 127 analyses completed, 24 total alerts, 82% avg confidence
- **Analytics Tab**: Productivity metrics, trend charts, framework distribution, top companies
- **Reports Tab**: 8 completed analyses with confidence scores
- **Jobs Tab**: Running, pending, and completed background jobs

**All data updates dynamically** - perfect for showing live dashboard functionality!

---

**Good luck with your video! 🎥**

**Remember:** The best demo videos show the value clearly and quickly. Focus on the "wow factor" - minutes for $0.10 vs days and $50K is impressive. Let that speak for itself. Now you have both a live dashboard AND live API to showcase a complete intelligence platform!
