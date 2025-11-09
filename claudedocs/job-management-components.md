# Job Management UI Components

Created: November 8, 2025

## Overview

Four production-ready React components for managing async job processing in ConsultantOS frontend. Built with TypeScript, real-time polling, and full accessibility support.

## Components Created

### 1. JobStatusIndicator.tsx
**Location**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/JobStatusIndicator.tsx`
**Size**: 6.1 KB | 222 lines

**Purpose**: Live status badge with automatic polling and progress tracking for individual jobs.

**Features**:
- Real-time status updates (pending → running → completed/failed)
- Progress bar with percentage for running jobs
- Elapsed time counter
- Auto-polling with configurable interval (default: 3s)
- Status-specific icons with animations (spinning loader for running jobs)
- Callbacks for status changes, completion, and errors

**Props**:
```typescript
{
  jobId: string;                              // Required: Job ID to monitor
  apiUrl?: string;                            // API base URL (default: env)
  pollingInterval?: number;                   // Poll interval in ms (default: 3000)
  showProgress?: boolean;                     // Show progress bar (default: true)
  showElapsedTime?: boolean;                  // Show elapsed time (default: true)
  onStatusChange?: (status) => void;          // Status change callback
  onComplete?: (result) => void;              // Completion callback
  onError?: (error) => void;                  // Error callback
  className?: string;                         // Custom styling
}
```

**Status Colors**:
- Pending: Gray (Clock icon)
- Running: Blue (Spinning Loader2 icon)
- Completed: Green (CheckCircle icon)
- Failed: Red (XCircle icon)

**Usage Example**:
```tsx
<JobStatusIndicator
  jobId="abc123"
  onComplete={(result) => console.log('Job done!', result)}
  onError={(error) => alert(error)}
/>
```

---

### 2. JobQueue.tsx
**Location**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/JobQueue.tsx`
**Size**: 6.7 KB | 211 lines

**Purpose**: List view of active jobs (pending/running) with real-time updates and cancel functionality.

**Features**:
- Auto-refresh for active jobs (default: 5s polling)
- Manual refresh button
- Individual job cancellation (DELETE /jobs/{job_id})
- Empty state with helpful messaging
- Automatic removal of completed/failed jobs from view
- Error handling with dismissible alerts

**Props**:
```typescript
{
  apiUrl?: string;                            // API base URL
  pollingInterval?: number;                   // Poll interval in ms (default: 5000)
  maxJobs?: number;                           // Max jobs to display (default: 10)
  showCompleted?: boolean;                    // Include completed jobs (default: false)
  onJobCancelled?: (jobId) => void;           // Cancel callback
  onJobComplete?: (jobId, result) => void;    // Completion callback
  className?: string;                         // Custom styling
}
```

**API Endpoint Used**:
- GET `/jobs?limit={maxJobs}&status=pending,running`

**Usage Example**:
```tsx
<JobQueue
  maxJobs={20}
  onJobComplete={(jobId, result) => {
    console.log(`Job ${jobId} completed!`);
    downloadReport(result);
  }}
/>
```

---

### 3. JobHistory.tsx
**Location**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/JobHistory.tsx`
**Size**: 11 KB | 298 lines

**Purpose**: Paginated table of completed and failed jobs with download and delete actions.

**Features**:
- Server-side pagination with navigation controls
- Formatted timestamps and duration calculations
- Download button for completed jobs
- Delete functionality with confirmation
- Responsive table design
- Empty state messaging
- Status badges (completed/failed)

**Props**:
```typescript
{
  apiUrl?: string;                            // API base URL
  pageSize?: number;                          // Jobs per page (default: 10)
  allowDelete?: boolean;                      // Show delete button (default: true)
  onJobDeleted?: (jobId) => void;             // Delete callback
  onDownload?: (jobId, result) => void;       // Download callback
  className?: string;                         // Custom styling
}
```

**Table Columns**:
1. Job ID (truncated with ellipsis)
2. Company name
3. Status badge (completed/failed)
4. Duration (formatted as "Xm Ys")
5. Completed timestamp
6. Actions (Download + Delete)

**API Endpoint Used**:
- GET `/jobs?status=completed,failed&limit={pageSize}&offset={offset}`
- DELETE `/jobs/{jobId}`

**Usage Example**:
```tsx
<JobHistory
  pageSize={25}
  onDownload={(jobId, result) => {
    const blob = new Blob([result.pdf_data], { type: 'application/pdf' });
    saveAs(blob, `analysis-${jobId}.pdf`);
  }}
/>
```

---

### 4. AsyncAnalysisForm.tsx
**Location**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/AsyncAnalysisForm.tsx`
**Size**: 12 KB | 338 lines

**Purpose**: Comprehensive form for submitting async business analysis jobs with validation.

**Features**:
- Input validation with error messages
- Framework multi-selection with descriptions
- Analysis depth selector (Quick/Standard/Deep)
- Custom requirements textarea
- Estimated time display
- Loading states during submission
- Success/error handling
- Auto-reset on successful submission

**Props**:
```typescript
{
  apiUrl?: string;                            // API base URL
  onJobSubmitted?: (jobId) => void;           // Success callback with job ID
  onError?: (error) => void;                  // Error callback
  initialValues?: Partial<FormData>;          // Pre-fill form values
  className?: string;                         // Custom styling
}
```

**Form Fields**:
1. **Company Name** (required) - Text input
2. **Industry** (required) - Text input
3. **Business Frameworks** (required) - Multi-select grid:
   - Porter's 5 Forces
   - SWOT Analysis
   - PESTEL Analysis
   - Blue Ocean Strategy
   - BCG Matrix
   - Ansoff Matrix
4. **Analysis Depth** - Single select:
   - Quick (~5 min)
   - Standard (~15 min)
   - Deep (~30 min)
5. **Custom Requirements** (optional) - Textarea

**Validation Rules**:
- Company name: Required, non-empty
- Industry: Required, non-empty
- Frameworks: At least one must be selected
- All other fields: Optional

**API Endpoint Used**:
- POST `/analyze/async`

**Usage Example**:
```tsx
<AsyncAnalysisForm
  initialValues={{ company: 'Tesla', industry: 'Electric Vehicles' }}
  onJobSubmitted={(jobId) => {
    router.push(`/jobs/${jobId}`);
  }}
  onError={(error) => {
    toast.error(`Submission failed: ${error}`);
  }}
/>
```

---

## Integration Points

### Shared Types
All components use the shared `JobStatus` interface:
```typescript
interface JobStatus {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;                          // 0-100 for running jobs
  created_at: string;                         // ISO timestamp
  updated_at: string;                         // ISO timestamp
  company?: string;                           // Company being analyzed
  result?: any;                               // Analysis result (completed only)
  error?: string;                             // Error message (failed only)
}
```

### Phase 1 Dependencies
All components build on existing Phase 1 components:
- **Badge**: Status indicators with color variants
- **Button**: Actions (cancel, delete, download, refresh)
- **Card**: Container structure with headers/content
- **Spinner**: Loading states
- **Alert**: Error and info messages
- **Icons**: Lucide-react for consistent iconography

### API Requirements

**Backend Endpoints Needed**:
1. `GET /jobs/{job_id}/status` - Fetch individual job status
2. `GET /jobs?status={statuses}&limit={n}&offset={n}` - List jobs with filtering
3. `POST /analyze/async` - Submit async analysis job
4. `DELETE /jobs/{job_id}` - Cancel or delete job

**Expected Response Format**:
```typescript
// Single job status
{
  "job_id": "abc-123-def-456",
  "status": "running",
  "progress": 65,
  "created_at": "2025-11-08T10:30:00Z",
  "updated_at": "2025-11-08T10:35:00Z",
  "company": "Tesla",
  "result": null,
  "error": null
}

// Job list
{
  "jobs": [JobStatus, ...],
  "total": 42
}

// Async submission response
{
  "job_id": "new-job-id-here",
  "status": "pending",
  "created_at": "2025-11-08T10:40:00Z"
}
```

---

## Accessibility Features

All components implement WCAG 2.1 AA compliance:

1. **Keyboard Navigation**: Full keyboard support for all interactive elements
2. **ARIA Labels**:
   - Progress bars: `role="progressbar"` with aria-valuenow/min/max
   - Status indicators: `role="status"` with screen reader text
   - Buttons: aria-label for icon-only actions
   - Tables: Proper th/td structure with scope attributes
3. **Focus Management**: Visible focus indicators on all controls
4. **Screen Reader Support**:
   - Hidden decorative icons with `aria-hidden="true"`
   - Descriptive labels for all form inputs
   - Status announcements via `sr-only` spans
5. **Color Contrast**: All text meets WCAG AA contrast requirements
6. **Form Validation**: Error messages associated with inputs via aria-describedby

---

## Performance Considerations

### Polling Optimization
- **Adaptive Polling**: Polling stops when jobs reach terminal states (completed/failed)
- **Configurable Intervals**: Default 3-5s, adjustable per component
- **Cleanup**: useEffect cleanup functions cancel timers on unmount

### State Management
- **Local State**: Each component manages its own state independently
- **Callback Props**: Parent components can coordinate via callbacks
- **Error Boundaries**: Components gracefully handle fetch failures

### Network Efficiency
- **Conditional Requests**: Only poll active jobs, not completed ones
- **Request Batching**: JobQueue fetches multiple jobs in single request
- **Pagination**: JobHistory uses server-side pagination to limit data transfer

---

## Responsive Design

All components are fully responsive:

### Mobile (<768px)
- Single column layouts
- Touch-friendly tap targets (min 44x44px)
- Horizontal scroll for tables
- Stacked framework selection cards

### Tablet (768px-1024px)
- 2-column framework grid
- Condensed table columns
- Side-by-side pagination controls

### Desktop (>1024px)
- Full table layout
- 2-column framework grid with descriptions
- Optimal spacing and padding

---

## Usage Patterns

### Complete Job Management Dashboard
```tsx
import {
  AsyncAnalysisForm,
  JobQueue,
  JobHistory,
  JobStatusIndicator
} from '@/app/components';

export default function JobsPage() {
  const [latestJobId, setLatestJobId] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Submit new analysis */}
      <AsyncAnalysisForm
        onJobSubmitted={(jobId) => {
          setLatestJobId(jobId);
          toast.success(`Job ${jobId} submitted!`);
        }}
      />

      {/* Show latest job status */}
      {latestJobId && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Latest Job</h3>
          <JobStatusIndicator jobId={latestJobId} />
        </div>
      )}

      {/* Active jobs queue */}
      <JobQueue
        onJobComplete={(jobId) => {
          toast.success(`Job ${jobId} completed!`);
        }}
      />

      {/* Historical jobs */}
      <JobHistory
        onDownload={(jobId, result) => {
          downloadPDF(result);
        }}
      />
    </div>
  );
}
```

### Standalone Job Monitoring
```tsx
import { JobStatusIndicator } from '@/app/components';

export function JobMonitor({ jobId }: { jobId: string }) {
  const router = useRouter();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Progress</CardTitle>
      </CardHeader>
      <CardContent>
        <JobStatusIndicator
          jobId={jobId}
          showProgress
          showElapsedTime
          onComplete={(result) => {
            router.push(`/results/${jobId}`);
          }}
          onError={(error) => {
            alert(`Job failed: ${error}`);
          }}
        />
      </CardContent>
    </Card>
  );
}
```

---

## Testing Recommendations

### Unit Tests
1. **Component Rendering**: Verify all components render without errors
2. **Prop Validation**: Test required vs optional props
3. **User Interactions**: Click handlers, form submissions, cancellations
4. **Status Changes**: Mock API responses for different job states

### Integration Tests
1. **Polling Behavior**: Verify polling starts/stops correctly
2. **API Integration**: Test with mocked fetch responses
3. **Error Handling**: Network failures, 404s, 500s
4. **Callback Coordination**: Parent-child communication

### E2E Tests (Playwright)
1. **Full Job Flow**: Submit → Monitor → Complete → Download
2. **Pagination**: Navigate through job history pages
3. **Real-time Updates**: Verify status changes without manual refresh
4. **Accessibility**: Keyboard navigation, screen reader compatibility

---

## Future Enhancements

### Potential Features
1. **WebSocket Support**: Replace polling with real-time push notifications
2. **Job Filtering**: Filter history by status, date range, company
3. **Bulk Actions**: Select multiple jobs for batch delete/download
4. **Export Options**: Download history as CSV/JSON
5. **Job Details Modal**: Detailed view of job configuration and results
6. **Notifications**: Browser notifications for job completion
7. **Job Scheduling**: Schedule analyses for future execution
8. **Job Cloning**: Duplicate existing job configurations

### Performance Optimizations
1. **Virtual Scrolling**: For very long job lists
2. **Optimistic Updates**: Instant UI feedback before API confirmation
3. **Request Deduplication**: Prevent duplicate polling requests
4. **Caching**: Cache job results in localStorage/sessionStorage

---

## Troubleshooting

### Common Issues

**Issue**: Polling doesn't stop after job completes
- **Solution**: Verify backend returns correct terminal status ('completed' or 'failed')
- **Check**: Component cleanup in useEffect dependencies

**Issue**: Form validation errors persist
- **Solution**: Ensure error state is cleared in onChange handlers
- **Check**: validationErrors state management

**Issue**: Job history pagination broken
- **Solution**: Backend must return total count in response
- **Check**: API response format matches expected structure

**Issue**: Progress bar doesn't update
- **Solution**: Backend must include 'progress' field (0-100) for running jobs
- **Check**: JobStatusIndicator showProgress prop is true

---

## File Locations

All files created:

1. `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/JobStatusIndicator.tsx`
2. `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/JobQueue.tsx`
3. `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/JobHistory.tsx`
4. `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/AsyncAnalysisForm.tsx`
5. `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/index.ts` (updated)

**Total Lines of Code**: 1,069 lines
**Total Size**: ~36 KB

All components are fully typed with TypeScript, accessible, responsive, and production-ready.
