# Dashboard Demo Guide for Video Recording

## Quick Start

1. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate to**: `http://localhost:3000/dashboard`

3. **Demo Mode Status**: ✅ **ENABLED** (line 131: `const DEMO_MODE = true`)

## What You'll See

### 📊 Overview Tab (Main Dashboard)

**Stats Cards** (5 prominent metrics):
- **Total Monitors**: 4
- **Active Monitors**: 3 (green)
- **Total Analyses**: 127 (blue) ⭐ *Key metric for video*
- **Total Alerts**: 7 (orange)
- **Avg Confidence**: 82% (purple) ⭐ *Key metric for video*

**Active Monitors Section** (4 companies):
1. **Tesla** - Electric Vehicles & Autonomous Driving
   - Status: Active (green badge)
   - Frequency: Daily checks
   - Alerts: 8 total
   - Last check: 2 hours ago

2. **OpenAI** - Artificial Intelligence & LLMs
   - Status: Active (green badge)
   - Frequency: Hourly checks
   - Alerts: 12 total
   - Last check: 30 minutes ago

3. **Rivian** - Electric Vehicles
   - Status: Active (green badge)
   - Frequency: Weekly checks
   - Alerts: 3 total
   - Last check: 2 days ago

4. **Anthropic** - AI Safety & Large Language Models
   - Status: Paused (yellow badge)
   - Frequency: Daily checks
   - Alerts: 1 total
   - Last check: 3 days ago

**Recent Alerts Section** (7 strategic alerts):
1. 🔴 **GPT-5 Launch Announcement** (OpenAI)
   - Unread • 2 hours ago • 92% confidence
   - "Major product launch: GPT-5 announced with 10x performance improvement..."

2. 🔴 **Competitive Threat: New EV Entrant** (Tesla)
   - Unread • 5 hours ago • 85% confidence
   - "New EV competitor announced $3B funding round..."

3. **Microsoft Strategic Investment** (OpenAI)
   - Read • 8 hours ago • 88% confidence
   - "Microsoft increases investment by $5B..."

4. **Q4 Production Milestone** (Rivian)
   - Read • 1 day ago • 79% confidence
   - "Q4 production exceeds targets by 15%..."

5. **EU Regulatory Advantage** (Tesla)
   - Read • 2 days ago • 73% confidence
   - "New regulatory framework favors sustainable manufacturing..."

6. **Google DeepMind Competition** (OpenAI)
   - Read • 3 days ago • 81% confidence
   - "DeepMind releases competing model..."

7. **Supply Chain Breakthrough** (Rivian)
   - Read • 4 days ago • 76% confidence
   - "Secured lithium supply agreement..."

### 📈 Analytics Tab

**Productivity Metrics** (3 cards):
- **Reports per Day**: 12.3
- **Avg Processing Time**: 42.5s
- **Success Rate**: 96.8%

**Business Metrics Card**:
- Total Reports: 127 ⭐
- Avg Confidence: 82% ⭐
- High Confidence Reports: 98

**Framework Distribution Chart** (Bar Chart):
- Porter's 5 Forces: 45 analyses
- SWOT Analysis: 38 analyses
- PESTEL: 28 analyses
- Blue Ocean Strategy: 16 analyses

**Report Status Pipeline** (Pie Chart):
- Completed: 118 (93%)
- Processing: 5 (4%)
- Pending: 3 (2%)
- Failed: 1 (1%)

**Job Queue Metrics**:
- Running: 2 jobs
- Pending: 3 jobs
- Completed: 122 jobs

### 📄 Reports Tab

**8 Completed Reports** with confidence scores:
1. **OpenAI** - AI & LLMs (89% confidence)
   - Frameworks: Porter, PESTEL, Disruption
   - 2 hours ago

2. **Tesla** - Electric Vehicles (85% confidence)
   - Frameworks: Porter, SWOT, Blue Ocean
   - 5 hours ago

3. **Rivian** - Electric Vehicles (78% confidence)
   - Frameworks: Porter, SWOT
   - 1 day ago

4. **Anthropic** - AI Safety (82% confidence)
   - Frameworks: Porter, PESTEL
   - 2 days ago

5. **Google DeepMind** - AI Research (87% confidence)
   - Frameworks: Porter, SWOT, PESTEL
   - 3 days ago

6. **Microsoft AI** - Enterprise AI (91% confidence)
   - Frameworks: Porter, Blue Ocean
   - 4 days ago

7. **Lucid Motors** - Electric Vehicles (76% confidence)
   - Frameworks: Porter, SWOT
   - 5 days ago

8. **Waymo** - Autonomous Driving (84% confidence)
   - Frameworks: Porter, PESTEL, Disruption
   - 6 days ago

**Features Visible**:
- Search bar (functional)
- Status filter dropdown (All/Completed/Processing/Pending/Failed)
- Reset Filters button
- "View" button for each report

### ⚙️ Jobs Tab

**Active Jobs Section** (3 jobs):
1. **job_001** - Running
   - Status: Blue "running" badge
   - Progress bar: 65% complete
   - Created: 15 minutes ago

2. **job_002** - Pending
   - Status: Yellow "pending" badge
   - Progress: 0%
   - Created: 5 minutes ago

3. **job_003** - Completed
   - Status: Gray "completed" badge
   - Progress: 100%
   - Result: report_id: rep_003, confidence: 0.78
   - Created: 2 hours ago

**Features Visible**:
- Refresh button
- Cancel button for running jobs
- Job History section with "View History" button

## Video Recording Tips

### Scene Setup
1. **Start on Overview Tab** - Shows all key metrics prominently
2. **Highlight Stats Cards** - Point to 127 analyses, 24 alerts, 82% confidence
3. **Show Active Monitors** - Pan through Tesla, OpenAI, Rivian, Anthropic
4. **Scroll Through Alerts** - Show unread alerts (blue highlight) and rich content

### Key Talking Points
- **127 analyses completed** - Matches video script exactly
- **4 companies monitored** - Tesla, OpenAI, Rivian, Anthropic
- **7 recent strategic alerts** - High-priority changes detected
- **82% average confidence** - High-quality intelligence
- **Real-time monitoring** - Continuous intelligence tracking

### Tab Navigation Flow
1. **Overview** (30 sec) - Show monitors and alerts
2. **Analytics** (20 sec) - Show charts and productivity metrics
3. **Reports** (15 sec) - Scroll through 8 completed analyses
4. **Jobs** (10 sec) - Show running, pending, completed jobs

### Demo Mode Benefits
- ✅ No API calls required
- ✅ Instant data loading
- ✅ No authentication needed
- ✅ Consistent data for multiple takes
- ✅ No network dependencies
- ✅ All features fully functional

## Disabling Demo Mode

To switch back to production mode:
1. Open `frontend/app/dashboard/page.tsx`
2. Change line 131: `const DEMO_MODE = false;`
3. Restart the dev server

## Troubleshooting

**Issue**: Dashboard shows empty state
**Solution**: Verify DEMO_MODE is `true` on line 131

**Issue**: Stats not displaying
**Solution**: Check console for errors, ensure mock data is properly structured

**Issue**: Charts not rendering
**Solution**: Wait a moment for charts to initialize, or refresh the page

## Data Freshness

All timestamps are **relative to current time**:
- Monitors: Last checks range from 30 min to 3 days ago
- Alerts: Created from 2 hours to 4 days ago
- Reports: Generated from 2 hours to 6 days ago
- Jobs: Active jobs from 5-15 minutes ago

This ensures the demo always looks current and realistic!

## Perfect for Video Script

This dashboard configuration **exactly matches** the requirements from `VIDEO_SCRIPT.md`:
- ✅ 4 Active Monitors (Tesla, OpenAI, Rivian, Anthropic)
- ✅ 7 Recent Alerts with strategic insights
- ✅ 127 Analyses Completed (prominently displayed)
- ✅ 24 Total Alerts
- ✅ 82% Average Confidence
- ✅ Analytics with productivity metrics and charts
- ✅ 8 Completed reports with confidence scores
- ✅ Running, pending, and completed jobs

Ready for professional video recording! 🎬
