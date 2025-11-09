# Frontend Feedback System Implementation Guide

## Overview

This guide provides specifications for implementing the feedback UI components in the Next.js 14 frontend to complete the quality flywheel system.

---

## Required Components

### 1. InsightFeedback Component

**Location**: `frontend/app/components/feedback/InsightFeedback.tsx`

**Purpose**: Inline feedback widget attached to each insight in reports

**Features**:
- Star rating (1-5)
- Quick feedback text input
- "Correct this insight" button
- Compact design that doesn't interrupt reading flow

**Component Specification**:

```typescript
'use client';

import { useState } from 'react';
import { Star, Edit } from 'lucide-react';

interface InsightFeedbackProps {
  insightId: string;
  reportId: string;
  section: string;  // porter, swot, pestel, blue_ocean
  onCorrectionClick: () => void;
}

export function InsightFeedback({
  insightId,
  reportId,
  section,
  onCorrectionClick
}: InsightFeedbackProps) {
  const [rating, setRating] = useState<number | null>(null);
  const [hoveredStar, setHoveredStar] = useState<number | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!rating) return;

    const response = await fetch(
      `/api/feedback/insights/${insightId}/rating?rating=${rating}&report_id=${reportId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback_text: feedbackText || null })
      }
    );

    if (response.ok) {
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
    }
  };

  return (
    <div className="feedback-widget border-t mt-4 pt-3 flex items-center justify-between">
      {/* Star Rating */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Rate this insight:</span>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              onMouseEnter={() => setHoveredStar(star)}
              onMouseLeave={() => setHoveredStar(null)}
              onClick={() => setRating(star)}
              className="transition-transform hover:scale-110"
            >
              <Star
                className={`w-5 h-5 ${
                  star <= (hoveredStar || rating || 0)
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
        </div>
      </div>

      {/* Quick Feedback */}
      {rating && !submitted && (
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Optional: Why this rating?"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            className="text-sm border rounded px-2 py-1 w-64"
          />
          <button
            onClick={handleSubmit}
            className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
          >
            Submit
          </button>
        </div>
      )}

      {/* Success Message */}
      {submitted && (
        <span className="text-sm text-green-600">✓ Thanks for your feedback!</span>
      )}

      {/* Correction Button */}
      <button
        onClick={onCorrectionClick}
        className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600"
      >
        <Edit className="w-4 h-4" />
        Correct
      </button>
    </div>
  );
}
```

**CSS Styling**:
```css
.feedback-widget {
  background: linear-gradient(to right, transparent, rgba(59, 130, 246, 0.05), transparent);
  border-top: 1px solid #e5e7eb;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

### 2. CorrectionModal Component

**Location**: `frontend/app/components/feedback/CorrectionModal.tsx`

**Purpose**: Modal dialog for submitting detailed corrections

**Features**:
- Show original insight text
- Text area for corrected version
- Optional explanation field
- Error category selector
- Submit for review

**Component Specification**:

```typescript
'use client';

import { useState } from 'react';
import { X } from 'lucide-react';

interface CorrectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  insightId: string;
  reportId: string;
  section: string;
  originalText: string;
}

type ErrorCategory = 'factual' | 'tone' | 'relevance' | 'depth' | 'structure' | 'other';

export function CorrectionModal({
  isOpen,
  onClose,
  insightId,
  reportId,
  section,
  originalText
}: CorrectionModalProps) {
  const [correctedText, setCorrectedText] = useState('');
  const [explanation, setExplanation] = useState('');
  const [errorCategory, setErrorCategory] = useState<ErrorCategory>('factual');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);

    try {
      const response = await fetch(
        `/api/feedback/insights/${insightId}/correction`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            report_id: reportId,
            section,
            original_text: originalText,
            corrected_text: correctedText,
            explanation,
            error_category: errorCategory
          })
        }
      );

      if (response.ok) {
        alert('✓ Correction submitted! Thanks for helping improve our analysis.');
        onClose();
      } else {
        alert('✗ Failed to submit correction. Please try again.');
      }
    } catch (error) {
      alert('✗ Error submitting correction. Please check your connection.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Correct This Insight</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Original Text */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Original Insight ({section.toUpperCase()})
          </label>
          <div className="p-3 bg-red-50 border border-red-200 rounded text-sm">
            {originalText}
          </div>
        </div>

        {/* Corrected Text */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Correction *
          </label>
          <textarea
            value={correctedText}
            onChange={(e) => setCorrectedText(e.target.value)}
            placeholder="Provide the corrected version of this insight..."
            className="w-full p-3 border border-gray-300 rounded resize-none h-32"
            required
          />
        </div>

        {/* Explanation */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Explanation (Optional)
          </label>
          <textarea
            value={explanation}
            onChange={(e) => setExplanation(e.target.value)}
            placeholder="Why is this correction needed? What was wrong with the original?"
            className="w-full p-3 border border-gray-300 rounded resize-none h-24"
          />
        </div>

        {/* Error Category */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type of Error
          </label>
          <select
            value={errorCategory}
            onChange={(e) => setErrorCategory(e.target.value as ErrorCategory)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="factual">Factual Error - Incorrect data or facts</option>
            <option value="depth">Depth Issue - Too shallow or too detailed</option>
            <option value="relevance">Relevance - Not relevant to analysis</option>
            <option value="tone">Tone Issue - Inappropriate language</option>
            <option value="structure">Structure - Poor organization</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!correctedText.trim() || submitting}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Submitting...' : 'Submit Correction'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

### 3. QualityMetricsPanel Component

**Location**: `frontend/app/components/feedback/QualityMetricsPanel.tsx`

**Purpose**: Display quality metrics for a specific report

**Features**:
- Average rating with star visualization
- User satisfaction score
- Correction count
- Framework-specific quality breakdown
- Trend indicators

**Component Specification**:

```typescript
'use client';

import { useEffect, useState } from 'react';
import { Star, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

interface QualityMetrics {
  report_id: string;
  avg_rating: number;
  total_ratings: number;
  corrections_count: number;
  user_satisfaction: number;
  frameworks_quality: Record<string, number>;
  needs_improvement: boolean;
}

interface QualityMetricsPanelProps {
  reportId: string;
}

export function QualityMetricsPanel({ reportId }: QualityMetricsPanelProps) {
  const [metrics, setMetrics] = useState<QualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/feedback/reports/${reportId}/quality`)
      .then(res => res.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [reportId]);

  if (loading) {
    return <div className="animate-pulse bg-gray-100 rounded-lg p-4 h-48" />;
  }

  if (!metrics || metrics.total_ratings === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
        <p className="text-sm text-blue-800">
          No feedback yet. Be the first to rate this analysis!
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Quality Metrics</h3>

      {/* Overall Rating */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Overall Rating</span>
          <span className="text-2xl font-bold">{metrics.avg_rating.toFixed(1)}/5.0</span>
        </div>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              className={`w-6 h-6 ${
                star <= Math.round(metrics.avg_rating)
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-gray-300'
              }`}
            />
          ))}
        </div>
        <p className="text-xs text-gray-600 mt-1">
          Based on {metrics.total_ratings} rating{metrics.total_ratings !== 1 ? 's' : ''}
        </p>
      </div>

      {/* User Satisfaction */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">User Satisfaction</span>
          <span className="text-lg font-semibold">
            {(metrics.user_satisfaction * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              metrics.user_satisfaction >= 0.8 ? 'bg-green-500' :
              metrics.user_satisfaction >= 0.6 ? 'bg-yellow-500' :
              'bg-red-500'
            }`}
            style={{ width: `${metrics.user_satisfaction * 100}%` }}
          />
        </div>
      </div>

      {/* Corrections */}
      {metrics.corrections_count > 0 && (
        <div className="mb-4 bg-orange-50 border border-orange-200 rounded p-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-orange-600" />
            <span className="text-sm font-medium text-orange-800">
              {metrics.corrections_count} correction{metrics.corrections_count !== 1 ? 's' : ''} submitted
            </span>
          </div>
        </div>
      )}

      {/* Framework Breakdown */}
      {Object.keys(metrics.frameworks_quality).length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">Framework Quality</h4>
          <div className="space-y-2">
            {Object.entries(metrics.frameworks_quality).map(([framework, rating]) => (
              <div key={framework} className="flex items-center justify-between">
                <span className="text-sm capitalize">{framework}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{rating.toFixed(1)}</span>
                  {rating >= 4.0 ? (
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  ) : rating < 3.5 ? (
                    <TrendingDown className="w-4 h-4 text-red-600" />
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Needs Improvement Warning */}
      {metrics.needs_improvement && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded p-3">
          <p className="text-sm text-red-800 font-medium">
            ⚠️ This report has quality issues. Review feedback for improvements.
          </p>
        </div>
      )}
    </div>
  );
}
```

---

### 4. AdminQualityDashboard Component

**Location**: `frontend/app/admin/quality/page.tsx`

**Purpose**: Admin dashboard for monitoring and managing feedback

**Features**:
- System-wide quality trends
- Pending corrections queue
- Framework performance comparison
- Error category distribution
- Learning patterns visualization

**Component Specification**:

```typescript
'use client';

import { useEffect, useState } from 'react';
import { BarChart, LineChart, TrendingUp, AlertTriangle } from 'lucide-react';

interface QualityReport {
  time_period: string;
  overall_avg_rating: number;
  total_reports: number;
  total_ratings: number;
  total_corrections: number;
  user_satisfaction: number;
  most_corrected_patterns: Array<{
    error_category: string;
    count: number;
    percentage: number;
  }>;
  improvement_recommendations: string[];
}

interface PendingCorrection {
  id: string;
  insight_id: string;
  section: string;
  original_text: string;
  corrected_text: string;
  explanation: string;
  error_category: string;
  created_at: string;
}

export default function AdminQualityDashboard() {
  const [report, setReport] = useState<QualityReport | null>(null);
  const [pending, setPending] = useState<PendingCorrection[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [days]);

  const loadData = async () => {
    setLoading(true);

    // Load quality report
    const reportRes = await fetch(`/api/feedback/quality/report?days=${days}`);
    const reportData = await reportRes.json();
    setReport(reportData);

    // Load pending corrections
    const pendingRes = await fetch('/api/feedback/corrections/pending?limit=50');
    const pendingData = await pendingRes.json();
    setPending(pendingData);

    setLoading(false);
  };

  const validateCorrection = async (correctionId: string, approved: boolean) => {
    await fetch(
      `/api/feedback/corrections/${correctionId}/validate?approved=${approved}`,
      { method: 'POST' }
    );
    loadData(); // Refresh
  };

  if (loading || !report) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Quality Dashboard</h1>

      {/* Time Period Selector */}
      <div className="mb-6 flex gap-2">
        {[7, 30, 90].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-4 py-2 rounded ${
              days === d
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            Last {d} days
          </button>
        ))}
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Average Rating"
          value={`${report.overall_avg_rating.toFixed(2)}/5.0`}
          icon={<TrendingUp className="w-6 h-6 text-green-600" />}
          trend={report.overall_avg_rating >= 4.0 ? 'good' : 'warning'}
        />
        <MetricCard
          title="User Satisfaction"
          value={`${(report.user_satisfaction * 100).toFixed(0)}%`}
          icon={<BarChart className="w-6 h-6 text-blue-600" />}
          trend={report.user_satisfaction >= 0.8 ? 'good' : 'warning'}
        />
        <MetricCard
          title="Total Reports"
          value={report.total_reports.toString()}
          icon={<LineChart className="w-6 h-6 text-purple-600" />}
        />
        <MetricCard
          title="Total Corrections"
          value={report.total_corrections.toString()}
          icon={<AlertTriangle className="w-6 h-6 text-orange-600" />}
          trend={report.total_corrections > 50 ? 'warning' : 'good'}
        />
      </div>

      {/* Error Categories */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Most Common Issues</h2>
        <div className="space-y-3">
          {report.most_corrected_patterns.map((pattern, idx) => (
            <div key={idx}>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium capitalize">
                  {pattern.error_category}
                </span>
                <span className="text-sm text-gray-600">
                  {pattern.count} ({pattern.percentage}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full"
                  style={{ width: `${pattern.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Improvement Recommendations</h2>
        <ul className="space-y-2">
          {report.improvement_recommendations.map((rec, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">•</span>
              <span className="text-sm">{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Pending Corrections */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">
          Pending Corrections ({pending.length})
        </h2>
        <div className="space-y-4">
          {pending.slice(0, 10).map((correction) => (
            <div key={correction.id} className="border rounded p-4">
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm font-medium capitalize">
                  {correction.section} - {correction.error_category}
                </span>
                <span className="text-xs text-gray-600">
                  {new Date(correction.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                <div>
                  <p className="font-medium text-red-600 mb-1">Original:</p>
                  <p className="text-gray-700">{correction.original_text.substring(0, 200)}...</p>
                </div>
                <div>
                  <p className="font-medium text-green-600 mb-1">Corrected:</p>
                  <p className="text-gray-700">{correction.corrected_text.substring(0, 200)}...</p>
                </div>
              </div>
              {correction.explanation && (
                <p className="text-sm text-gray-600 mb-3">
                  <strong>Explanation:</strong> {correction.explanation}
                </p>
              )}
              <div className="flex gap-2">
                <button
                  onClick={() => validateCorrection(correction.id, true)}
                  className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => validateCorrection(correction.id, false)}
                  className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                >
                  ✗ Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  icon,
  trend
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  trend?: 'good' | 'warning';
}) {
  return (
    <div className={`bg-white rounded-lg shadow p-4 ${
      trend === 'warning' ? 'border-l-4 border-orange-500' :
      trend === 'good' ? 'border-l-4 border-green-500' : ''
    }`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-600">{title}</span>
        {icon}
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
```

---

## Integration Steps

### Step 1: Install Dependencies

```bash
cd frontend
npm install lucide-react  # For icons
```

### Step 2: Create Component Files

Create the directory structure:
```bash
mkdir -p app/components/feedback
mkdir -p app/admin/quality
```

### Step 3: Add Components to Reports

In `app/analysis/[reportId]/page.tsx`, integrate feedback widgets:

```typescript
import { InsightFeedback } from '@/app/components/feedback/InsightFeedback';
import { CorrectionModal } from '@/app/components/feedback/CorrectionModal';
import { QualityMetricsPanel } from '@/app/components/feedback/QualityMetricsPanel';

export default function ReportPage({ params }: { params: { reportId: string } }) {
  const [correctionModal, setCorrectionModal] = useState<{
    open: boolean;
    insightId: string;
    section: string;
    text: string;
  } | null>(null);

  return (
    <div>
      {/* Quality Metrics in Sidebar */}
      <QualityMetricsPanel reportId={params.reportId} />

      {/* Each Insight with Feedback Widget */}
      <div className="insight-card">
        <p className="insight-text">{insightText}</p>
        <InsightFeedback
          insightId={insightId}
          reportId={params.reportId}
          section="porter"
          onCorrectionClick={() => setCorrectionModal({
            open: true,
            insightId,
            section: 'porter',
            text: insightText
          })}
        />
      </div>

      {/* Correction Modal */}
      {correctionModal && (
        <CorrectionModal
          isOpen={correctionModal.open}
          onClose={() => setCorrectionModal(null)}
          insightId={correctionModal.insightId}
          reportId={params.reportId}
          section={correctionModal.section}
          originalText={correctionModal.text}
        />
      )}
    </div>
  );
}
```

### Step 4: Add Admin Route

In `app/admin/layout.tsx`, add quality dashboard link:

```typescript
<nav>
  <Link href="/admin/quality">Quality Dashboard</Link>
</nav>
```

### Step 5: Configure API Proxy

In `next.config.js`, ensure API proxy is configured:

```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8080/:path*'
      }
    ];
  }
};
```

---

## Testing Checklist

- [ ] Star rating submits correctly
- [ ] Correction modal opens and closes
- [ ] Correction form validates required fields
- [ ] Quality metrics display correctly
- [ ] Admin dashboard loads pending corrections
- [ ] Approve/reject buttons work
- [ ] Error handling displays user-friendly messages
- [ ] Mobile responsiveness for all components
- [ ] Accessibility (keyboard navigation, screen readers)
- [ ] Loading states and animations

---

## Success Metrics

After implementing frontend components, monitor:

1. **Feedback Submission Rate**: > 40% of report viewers
2. **Correction Quality**: > 70% of submissions validated
3. **Time to Submit**: < 60 seconds for rating, < 3 minutes for correction
4. **User Satisfaction**: > 4.0/5.0 for feedback UI itself

---

## Next Steps

1. Implement components in order: InsightFeedback → CorrectionModal → QualityMetricsPanel → AdminQualityDashboard
2. Add unit tests for each component
3. Conduct user testing for feedback UI
4. Monitor backend API performance under feedback load
5. Iterate based on user feedback on the feedback system itself (meta!)

---

**Last Updated**: January 2025
