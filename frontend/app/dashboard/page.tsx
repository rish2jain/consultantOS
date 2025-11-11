'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { getApiKey } from '@/lib/auth';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Types matching backend models
interface MonitoringConfig {
  frequency: 'hourly' | 'daily' | 'weekly' | 'monthly';
  frameworks: string[];
  alert_threshold: number;
  notification_channels: string[];
  keywords?: string[];
  competitors?: string[];
}

interface Monitor {
  id: string;
  user_id: string;
  company: string;
  industry: string;
  config: MonitoringConfig;
  status: 'active' | 'paused' | 'deleted' | 'error';
  created_at: string;
  last_check?: string;
  next_check?: string;
  last_alert_id?: string;
  total_alerts: number;
  error_count: number;
  last_error?: string;
}

interface Change {
  change_type: string;
  title: string;
  description: string;
  confidence: number;
  source_urls?: string[];
  detected_at: string;
  previous_value?: string;
  current_value?: string;
}

interface Alert {
  id: string;
  monitor_id: string;
  title: string;
  summary: string;
  confidence: number;
  changes_detected: Change[];
  created_at: string;
  read: boolean;
  read_at?: string;
  user_feedback?: string;
  action_taken?: string;
}

interface MonitoringStats {
  total_monitors: number;
  active_monitors: number;
  paused_monitors: number;
  total_alerts_24h: number;
  unread_alerts: number;
  avg_alert_confidence: number;
  top_change_types: [string, number][];
}

interface AnalyticsData {
  productivity: {
    reports_per_day: number;
    avg_processing_time: number;
    success_rate: number;
    total_reports: number;
    reports_this_month: number;
    reports_last_month: number;
  };
  business: {
    total_frameworks_used: number;
    framework_distribution: Record<string, number>;
    avg_confidence_score: number;
    high_confidence_reports: number;
    industry_distribution: Record<string, number>;
    company_distribution: Record<string, number>;
  };
  dashboard: {
    report_status_pipeline: Record<string, number>;
    confidence_distribution: number[];
    framework_effectiveness: Record<string, number>;
    job_queue_metrics: Record<string, number>;
    user_activity: Record<string, number>;
  };
}

interface Report {
  report_id: string;
  company: string;
  industry?: string;
  frameworks: string[];
  status: string;
  confidence_score?: number;
  created_at: string;
  updated_at?: string;
}

interface Job {
  id: string;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  error?: string;
  result?: any;
}

export default function DashboardPage() {
  // Enable demo mode with mock data (set to true for video recording)
  const DEMO_MODE = false;

  // Mock data for demo video recording
  const mockMonitors: Monitor[] = [
    {
      id: "mon_tesla_ev",
      user_id: "demo_user",
      company: "Tesla",
      industry: "Electric Vehicles & Autonomous Driving",
      config: {
        frequency: "daily",
        frameworks: ["porter", "swot", "blue_ocean"],
        alert_threshold: 0.7,
        notification_channels: ["email", "dashboard"]
      },
      status: "active",
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
      last_check: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      next_check: new Date(Date.now() + 22 * 60 * 60 * 1000).toISOString(), // 22 hours from now
      total_alerts: 8,
      error_count: 0
    },
    {
      id: "mon_openai_ai",
      user_id: "demo_user",
      company: "OpenAI",
      industry: "Artificial Intelligence & LLMs",
      config: {
        frequency: "hourly",
        frameworks: ["porter", "pestel", "disruption"],
        alert_threshold: 0.8,
        notification_channels: ["email", "dashboard", "slack"]
      },
      status: "active",
      created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days ago
      last_check: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 min ago
      next_check: new Date(Date.now() + 30 * 60 * 1000).toISOString(), // 30 min from now
      total_alerts: 12,
      error_count: 0
    },
    {
      id: "mon_rivian_ev",
      user_id: "demo_user",
      company: "Rivian",
      industry: "Electric Vehicles",
      config: {
        frequency: "weekly",
        frameworks: ["porter", "swot"],
        alert_threshold: 0.6,
        notification_channels: ["dashboard"]
      },
      status: "active",
      created_at: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(), // 21 days ago
      last_check: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
      next_check: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days from now
      total_alerts: 3,
      error_count: 0
    },
    {
      id: "mon_anthropic_ai",
      user_id: "demo_user",
      company: "Anthropic",
      industry: "AI Safety & Large Language Models",
      config: {
        frequency: "daily",
        frameworks: ["porter", "pestel", "blue_ocean"],
        alert_threshold: 0.75,
        notification_channels: ["email"]
      },
      status: "paused",
      created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), // 10 days ago
      last_check: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
      total_alerts: 1,
      error_count: 0
    }
  ];

  const mockAlerts: Alert[] = [
    {
      id: "alert_1",
      monitor_id: "mon_openai_ai",
      title: "GPT-5 Launch Announcement",
      summary: "Major product launch: GPT-5 announced with 10x performance improvement and native multimodal capabilities",
      confidence: 0.92,
      changes_detected: [
        {
          change_type: "product_launch",
          title: "GPT-5 Release",
          description: "Next-generation model with breakthrough capabilities",
          confidence: 0.92,
          detected_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          source_urls: ["https://openai.com/gpt5"]
        }
      ],
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      read: false
    },
    {
      id: "alert_2",
      monitor_id: "mon_tesla_ev",
      title: "Competitive Threat: New EV Entrant",
      summary: "Competitive threat: New EV competitor announced $3B funding round and partnership with major automotive manufacturer",
      confidence: 0.85,
      changes_detected: [
        {
          change_type: "competitive_threat",
          title: "New Market Entrant",
          description: "Well-funded competitor entering EV market",
          confidence: 0.85,
          detected_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
        }
      ],
      created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
      read: false
    },
    {
      id: "alert_3",
      monitor_id: "mon_openai_ai",
      title: "Microsoft Strategic Investment",
      summary: "Strategic partnership: Microsoft increases investment by $5B, expands Azure AI integration",
      confidence: 0.88,
      changes_detected: [
        {
          change_type: "partnership",
          title: "Microsoft Investment",
          description: "Major strategic investment and partnership expansion",
          confidence: 0.88,
          detected_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString()
        }
      ],
      created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8 hours ago
      read: true
    },
    {
      id: "alert_4",
      monitor_id: "mon_rivian_ev",
      title: "Q4 Production Milestone",
      summary: "Operational milestone: Q4 production exceeds targets by 15%, stock price up 12%",
      confidence: 0.79,
      changes_detected: [
        {
          change_type: "operational",
          title: "Production Milestone",
          description: "Exceeded quarterly production targets",
          confidence: 0.79,
          detected_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
        }
      ],
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
      read: true
    },
    {
      id: "alert_5",
      monitor_id: "mon_tesla_ev",
      title: "EU Regulatory Advantage",
      summary: "Market dynamics: New regulatory framework in EU favors sustainable manufacturing, potential 8% margin improvement",
      confidence: 0.73,
      changes_detected: [
        {
          change_type: "regulatory",
          title: "EU Regulation Update",
          description: "Favorable regulatory changes in European market",
          confidence: 0.73,
          detected_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
        }
      ],
      created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
      read: true
    },
    {
      id: "alert_6",
      monitor_id: "mon_openai_ai",
      title: "Google DeepMind Competition",
      summary: "Competitive positioning: Google DeepMind releases competing model, initial benchmarks show 95% parity",
      confidence: 0.81,
      changes_detected: [
        {
          change_type: "competitive_move",
          title: "DeepMind Model Release",
          description: "Major competitor launches comparable model",
          confidence: 0.81,
          detected_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
        }
      ],
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
      read: true
    },
    {
      id: "alert_7",
      monitor_id: "mon_rivian_ev",
      title: "Supply Chain Breakthrough",
      summary: "Supply chain development: Secured lithium supply agreement, reduces battery costs by 18%",
      confidence: 0.76,
      changes_detected: [
        {
          change_type: "supply_chain",
          title: "Lithium Supply Agreement",
          description: "Major cost reduction through supply chain optimization",
          confidence: 0.76,
          detected_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString()
        }
      ],
      created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(), // 4 days ago
      read: true
    }
  ];

  const mockStats: MonitoringStats = {
    total_monitors: 4,
    active_monitors: 3,
    paused_monitors: 1,
    total_alerts_24h: 7,
    unread_alerts: 2,
    avg_alert_confidence: 0.82,
    top_change_types: [
      ["product_launch", 3],
      ["competitive_threat", 5],
      ["partnership", 4],
      ["regulatory", 2]
    ]
  };

  const mockAnalytics: AnalyticsData = {
    productivity: {
      reports_per_day: 12.3,
      avg_processing_time: 42.5,
      success_rate: 96.8,
      total_reports: 127,
      reports_this_month: 89,
      reports_last_month: 73
    },
    business: {
      total_frameworks_used: 4,
      framework_distribution: {
        "porter": 45,
        "swot": 38,
        "pestel": 28,
        "blue_ocean": 16
      },
      avg_confidence_score: 0.82,
      high_confidence_reports: 98,
      industry_distribution: {
        "Artificial Intelligence": 42,
        "Electric Vehicles": 35,
        "Autonomous Driving": 28,
        "Cloud Computing": 22
      },
      company_distribution: {
        "OpenAI": 42,
        "Tesla": 35,
        "Rivian": 28,
        "Anthropic": 22
      }
    },
    dashboard: {
      report_status_pipeline: {
        "completed": 118,
        "processing": 5,
        "pending": 3,
        "failed": 1
      },
      confidence_distribution: [0.65, 0.72, 0.78, 0.82, 0.88, 0.91, 0.85],
      framework_effectiveness: {
        "porter": 0.86,
        "swot": 0.84,
        "pestel": 0.79,
        "blue_ocean": 0.81
      },
      job_queue_metrics: {
        "running": 2,
        "pending": 3,
        "completed": 122
      },
      user_activity: {
        "active_users": 15,
        "total_analyses": 127
      }
    }
  };

  const mockReports: Report[] = [
    {
      report_id: "rep_001",
      company: "OpenAI",
      industry: "Artificial Intelligence & LLMs",
      frameworks: ["porter", "pestel", "disruption"],
      status: "completed",
      confidence_score: 0.89,
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    },
    {
      report_id: "rep_002",
      company: "Tesla",
      industry: "Electric Vehicles & Autonomous Driving",
      frameworks: ["porter", "swot", "blue_ocean"],
      status: "completed",
      confidence_score: 0.85,
      created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
    },
    {
      report_id: "rep_003",
      company: "Rivian",
      industry: "Electric Vehicles",
      frameworks: ["porter", "swot"],
      status: "completed",
      confidence_score: 0.78,
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
    },
    {
      report_id: "rep_004",
      company: "Anthropic",
      industry: "AI Safety & Large Language Models",
      frameworks: ["porter", "pestel"],
      status: "completed",
      confidence_score: 0.82,
      created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      report_id: "rep_005",
      company: "Google DeepMind",
      industry: "Artificial Intelligence Research",
      frameworks: ["porter", "swot", "pestel"],
      status: "completed",
      confidence_score: 0.87,
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      report_id: "rep_006",
      company: "Microsoft AI",
      industry: "Enterprise AI Solutions",
      frameworks: ["porter", "blue_ocean"],
      status: "completed",
      confidence_score: 0.91,
      created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      report_id: "rep_007",
      company: "Lucid Motors",
      industry: "Electric Vehicles",
      frameworks: ["porter", "swot"],
      status: "completed",
      confidence_score: 0.76,
      created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      report_id: "rep_008",
      company: "Waymo",
      industry: "Autonomous Driving",
      frameworks: ["porter", "pestel", "disruption"],
      status: "completed",
      confidence_score: 0.84,
      created_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString()
    }
  ];

  const mockJobs: Job[] = [
    {
      id: "job_001",
      status: "running",
      progress: 65,
      created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(), // 15 min ago
      updated_at: new Date(Date.now() - 2 * 60 * 1000).toISOString() // 2 min ago
    },
    {
      id: "job_002",
      status: "pending",
      progress: 0,
      created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 min ago
      updated_at: new Date(Date.now() - 5 * 60 * 1000).toISOString()
    },
    {
      id: "job_003",
      status: "completed",
      progress: 100,
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000 + 60 * 1000).toISOString(),
      completed_at: new Date(Date.now() - 2 * 60 * 60 * 1000 + 90 * 1000).toISOString(),
      result: { report_id: "rep_003", confidence: 0.78 }
    }
  ];

  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<MonitoringStats | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonitor, setSelectedMonitor] = useState<Monitor | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'reports' | 'jobs'>('overview');
  const router = useRouter();

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  // Load dashboard data
  useEffect(() => {
    // Demo mode: Use mock data instead of API calls
    if (DEMO_MODE) {
      setMonitors(mockMonitors);
      setRecentAlerts(mockAlerts);
      setStats(mockStats);
      setAnalytics(mockAnalytics);
      setReports(mockReports);
      setJobs(mockJobs);
      setLoading(false);
      setError(null);
      return; // Skip API calls and interval setup
    }

    // Production mode: Load from API
    loadDashboardData();
    loadAnalytics();
    loadReports();
    loadJobs();

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      loadDashboardData();
      if (activeTab === 'analytics') loadAnalytics();
      if (activeTab === 'reports') loadReports();
      if (activeTab === 'jobs') loadJobs();
    }, 30000);
    return () => clearInterval(interval);
  }, [activeTab]);

  async function loadDashboardData() {
    try {
      setLoading(true);
      setError(null);

      // Get API key from in-memory storage (consistent with auth system)
      const apiKey = getApiKey() || '';

      // Use consolidated dashboard overview endpoint (replaces 5+ sequential calls)
      const overviewRes = await fetch(`${API_URL}/dashboard/overview?alert_limit=10&report_limit=5`, {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!overviewRes.ok) {
        throw new Error('Failed to load dashboard overview');
      }

      const overview = await overviewRes.json();

      // Set all dashboard data from single response
      setMonitors(overview.monitors || []);
      setStats(overview.stats || null);
      setRecentAlerts(overview.recent_alerts || []);

      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load dashboard';
      setError(errorMessage);
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadAnalytics() {
    try {
      const apiKey = getApiKey() || '';
      const analyticsRes = await fetch(`${API_URL}/dashboard/analytics?days=30`, {
        headers: { 'X-API-Key': apiKey },
      });

      if (analyticsRes.ok) {
        const analyticsData = await analyticsRes.json();
        setAnalytics(analyticsData);
      }
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  }

  async function loadReports() {
    try {
      const apiKey = getApiKey() || '';
      const reportsRes = await fetch(`${API_URL}/dashboard/reports?action=list&page=1&page_size=10`, {
        headers: { 'X-API-Key': apiKey },
      });

      if (reportsRes.ok) {
        const reportsData = await reportsRes.json();
        setReports(reportsData.reports || []);
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
    }
  }

  async function loadJobs() {
    try {
      const apiKey = getApiKey() || '';
      const jobsRes = await fetch(`${API_URL}/dashboard/jobs?action=list&status=pending,running&limit=20`, {
        headers: { 'X-API-Key': apiKey },
      });

      if (jobsRes.ok) {
        const jobsData = await jobsRes.json();
        setJobs(jobsData.jobs || []);
      }
    } catch (err) {
      console.error('Failed to load jobs:', err);
    }
  }

  // Debounced search function
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const debouncedSearchReports = useCallback((query: string) => {
    // Clear existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Set new timeout
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const apiKey = getApiKey() || '';
        const url = query
          ? `${API_URL}/dashboard/reports?action=search&search_query=${encodeURIComponent(query)}&page=1&page_size=10`
          : `${API_URL}/dashboard/reports?action=list&page=1&page_size=10`;
        const res = await fetch(url, {
          headers: { 'X-API-Key': apiKey },
        });
        if (res.ok) {
          const data = await res.json();
          setReports(data.reports || []);
        }
      } catch (err) {
        console.error('Search failed:', err);
      }
    }, 300); // 300ms debounce delay
  }, [API_URL]);

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  async function handleManualCheck(monitorId: string) {
    try {
      const apiKey = getApiKey() || '';
      
      const res = await fetch(`${API_URL}/monitors/${monitorId}/check`, {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!res.ok) {
        throw new Error('Failed to trigger check');
      }

      // Refresh dashboard
      await loadDashboardData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to check monitor');
    }
  }

  async function handleMarkAlertRead(alertId: string) {
    try {
      const apiKey = getApiKey() || '';
      
      const res = await fetch(`${API_URL}/monitors/alerts/${alertId}/read`, {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!res.ok) {
        throw new Error('Failed to mark as read');
      }

      // Update local state
      setRecentAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, read: true } : a))
      );
    } catch (err) {
      console.error('Failed to mark alert as read:', err);
    }
  }

  async function handlePauseMonitor(monitorId: string) {
    try {
      const apiKey = getApiKey() || '';
      
      const res = await fetch(`${API_URL}/monitors/${monitorId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({ status: 'paused' }),
      });

      if (!res.ok) {
        throw new Error('Failed to pause monitor');
      }

      await loadDashboardData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to pause monitor');
    }
  }

  async function handleResumeMonitor(monitorId: string) {
    try {
      const apiKey = getApiKey() || '';
      
      const res = await fetch(`${API_URL}/monitors/${monitorId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({ status: 'active' }),
      });

      if (!res.ok) {
        throw new Error('Failed to resume monitor');
      }

      await loadDashboardData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to resume monitor');
    }
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  }

  if (loading && monitors.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Error Display */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
              <div className="ml-auto">
                <button
                  onClick={loadDashboardData}
                  className="text-sm text-red-600 hover:text-red-800 underline"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              Intelligence Dashboard
            </h1>
            <button
              onClick={() => router.push('/monitors/new')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              + New Monitor
            </button>
          </div>
          
          {/* Tabs */}
          <div className="mt-6 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`${
                  activeTab === 'analytics'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Analytics
              </button>
              <button
                onClick={() => setActiveTab('reports')}
                className={`${
                  activeTab === 'reports'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Reports
              </button>
              <button
                onClick={() => setActiveTab('jobs')}
                className={`${
                  activeTab === 'jobs'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Jobs
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Total Monitors</div>
              <div className="text-3xl font-bold text-gray-900 mt-2">
                {stats.total_monitors || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Active Monitors</div>
              <div className="text-3xl font-bold text-green-600 mt-2">
                {stats.active_monitors || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Total Analyses</div>
              <div className="text-3xl font-bold text-blue-600 mt-2">
                {analytics?.productivity.total_reports || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Total Alerts</div>
              <div className="text-3xl font-bold text-orange-600 mt-2">
                {stats.total_alerts_24h || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Avg Confidence</div>
              <div className="text-3xl font-bold text-purple-600 mt-2">
                {stats.avg_alert_confidence ? (stats.avg_alert_confidence * 100).toFixed(0) : 0}%
              </div>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Active Monitors */}
            <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">
                  Active Monitors
                </h2>
              </div>

              <div className="divide-y divide-gray-200">
                {monitors.length === 0 ? (
                  <div className="px-6 py-12 text-center">
                    <p className="text-gray-500">
                      No monitors yet. Create your first monitor to start
                      tracking companies.
                    </p>
                    <button
                      onClick={() => router.push('/monitors/new')}
                      className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Create Monitor
                    </button>
                  </div>
                ) : (
                  monitors.map((monitor) => (
                    <div key={monitor.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <h3 className="text-lg font-medium text-gray-900">
                              {monitor.company}
                            </h3>
                            <span
                              className={`px-2 py-1 text-xs rounded-full ${
                                monitor.status === 'active'
                                  ? 'bg-green-100 text-green-800'
                                  : monitor.status === 'paused'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {monitor.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">
                            {monitor.industry}
                          </p>

                          <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                            <span>
                              {monitor.config.frequency} checks
                            </span>
                            <span>
                              {monitor.total_alerts} alerts
                            </span>
                            {monitor.last_check && (
                              <span>
                                Last check: {formatDate(monitor.last_check)}
                              </span>
                            )}
                          </div>

                          {monitor.error_count > 0 && monitor.last_error && (
                            <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                              {monitor.last_error}
                            </div>
                          )}
                        </div>

                        <div className="flex gap-2 ml-4">
                          <button
                            onClick={() => handleManualCheck(monitor.id)}
                            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                          >
                            Check Now
                          </button>

                          {monitor.status === 'active' ? (
                            <button
                              onClick={() => handlePauseMonitor(monitor.id)}
                              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                            >
                              Pause
                            </button>
                          ) : (
                            <button
                              onClick={() => handleResumeMonitor(monitor.id)}
                              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                            >
                              Resume
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Recent Alerts */}
          <div>
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">
                  Recent Alerts
                </h2>
              </div>

              <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {recentAlerts.length === 0 ? (
                  <div className="px-6 py-8 text-center text-gray-500">
                    No alerts yet
                  </div>
                ) : (
                  recentAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`px-6 py-4 hover:bg-gray-50 cursor-pointer ${
                        !alert.read ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => handleMarkAlertRead(alert.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900">
                            {alert.title}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {alert.summary}
                          </p>

                          <div className="mt-2 flex items-center gap-3">
                            <span className="text-xs text-gray-500">
                              {formatDate(alert.created_at)}
                            </span>
                            <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {(alert.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        </div>

                        {!alert.read && (
                          <div className="w-2 h-2 bg-blue-600 rounded-full ml-2"></div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {analytics ? (
              <>
                {/* Productivity Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="text-sm text-gray-500">Reports per Day</div>
                    <div className="text-3xl font-bold text-gray-900 mt-2">
                      {analytics.productivity.reports_per_day.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="text-sm text-gray-500">Avg Processing Time</div>
                    <div className="text-3xl font-bold text-gray-900 mt-2">
                      {analytics.productivity.avg_processing_time.toFixed(1)}s
                    </div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="text-sm text-gray-500">Success Rate</div>
                    <div className="text-3xl font-bold text-green-600 mt-2">
                      {analytics.productivity.success_rate.toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Framework Distribution Chart */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Framework Distribution</h3>
                    {Object.keys(analytics.business.framework_distribution).length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={Object.entries(analytics.business.framework_distribution).map(([name, value]) => ({ name, value }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="value" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="text-gray-500 text-center py-8">No framework data available</p>
                    )}
                  </div>

                  {/* Report Status Pipeline Chart */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Report Status Pipeline</h3>
                    {Object.keys(analytics.dashboard.report_status_pipeline).length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={Object.entries(analytics.dashboard.report_status_pipeline).map(([name, value]) => ({ name, value }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.entries(analytics.dashboard.report_status_pipeline).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][index % 5]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="text-gray-500 text-center py-8">No status data available</p>
                    )}
                  </div>
                </div>

                {/* Additional Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Business Metrics</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Total Reports</span>
                        <span className="text-sm font-medium">{analytics.productivity.total_reports}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Avg Confidence</span>
                        <span className="text-sm font-medium">{(analytics.business.avg_confidence_score * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">High Confidence Reports</span>
                        <span className="text-sm font-medium">{analytics.business.high_confidence_reports}</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Job Queue Metrics</h3>
                    <div className="space-y-3">
                      {Object.entries(analytics.dashboard.job_queue_metrics).map(([status, count]) => (
                        <div key={status} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600 capitalize">{status}</span>
                          <span className="text-sm font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <p className="text-gray-500 text-lg mb-4">No analytics data available</p>
                <p className="text-gray-400 text-sm">Analytics will appear here once reports are generated.</p>
              </div>
            )}
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Reports</h2>
                <button
                  onClick={() => router.push('/analysis')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
                >
                  + New Analysis
                </button>
              </div>
              
              {/* Filters */}
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <input
                    type="text"
                    placeholder="Search reports..."
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    onChange={(e) => {
                      const query = e.target.value;
                      if (query.length > 2 || query.length === 0) {
                        debouncedSearchReports(query);
                      }
                    }}
                  />
                  <select
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    onChange={async (e) => {
                      const status = e.target.value;
                      if (status) {
                        try {
                          const apiKey = getApiKey() || '';
                          const res = await fetch(
                            `${API_URL}/dashboard/reports?action=filter&status=${status}&page=1&page_size=10`,
                            { headers: { 'X-API-Key': apiKey } }
                          );
                          if (res.ok) {
                            const data = await res.json();
                            setReports(data.reports || []);
                          }
                        } catch (err) {
                          console.error('Filter failed:', err);
                        }
                      } else {
                        loadReports();
                      }
                    }}
                  >
                    <option value="">All Statuses</option>
                    <option value="completed">Completed</option>
                    <option value="processing">Processing</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                  </select>
                  <button
                    onClick={loadReports}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
                  >
                    Reset Filters
                  </button>
                </div>
              </div>
              <div className="divide-y divide-gray-200">
                {reports.length === 0 ? (
                  <div className="px-6 py-12 text-center">
                    <p className="text-gray-500">No reports yet. Create your first analysis.</p>
                    <button
                      onClick={() => router.push('/analysis')}
                      className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Create Analysis
                    </button>
                  </div>
                ) : (
                  reports.map((report, index) => (
                    <div
                      key={`${report.report_id || report.company || 'report'}-${index}`}
                      className="px-6 py-4 hover:bg-gray-50"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-gray-900">{report.company}</h3>
                          <p className="text-sm text-gray-500 mt-1">{report.industry || 'N/A'}</p>
                          <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                            <span>{report.frameworks.join(', ')}</span>
                            {report.confidence_score !== undefined && report.confidence_score !== null && (
                              <span className="bg-gray-100 px-2 py-1 rounded">
                                {(report.confidence_score * 100).toFixed(0)}% confidence
                              </span>
                            )}
                            <span className="capitalize">{report.status}</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {formatDate(report.created_at)}
                          </p>
                        </div>
                        <button
                          onClick={() => router.push(`/reports/${report.report_id}`)}
                          className="ml-4 px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                        >
                          View
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Jobs Tab */}
        {activeTab === 'jobs' && (
          <div className="space-y-6">
            {/* Active Jobs */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Active Jobs</h2>
                <button
                  onClick={loadJobs}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                >
                  Refresh
                </button>
              </div>
            <div className="divide-y divide-gray-200">
              {jobs.length === 0 ? (
                <div className="px-6 py-12 text-center text-gray-500">
                  No active jobs
                </div>
              ) : (
                jobs.map((job) => (
                  <div key={job.id} className="px-6 py-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                            job.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {job.status}
                          </span>
                          <span className="text-sm text-gray-600">Job {job.id.slice(0, 8)}</span>
                        </div>
                        {job.status === 'running' && job.progress > 0 && (
                          <div className="mt-2">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${job.progress}%` }}
                              ></div>
                            </div>
                            <p className="text-xs text-gray-500 mt-1">{job.progress}% complete</p>
                          </div>
                        )}
                        {job.error && (
                          <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                            {job.error}
                          </div>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          Created: {formatDate(job.created_at)}
                        </p>
                      </div>
                      {job.status === 'running' && (
                        <button
                          onClick={async () => {
                            try {
                              const apiKey = getApiKey() || '';
                              await fetch(`${API_URL}/dashboard/jobs/${job.id}/cancel`, {
                                method: 'POST',
                                headers: { 'X-API-Key': apiKey },
                              });
                              loadJobs();
                            } catch (err) {
                              console.error('Failed to cancel job:', err);
                            }
                          }}
                          className="ml-4 px-3 py-1 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Job History */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Job History</h2>
              <button
                onClick={async () => {
                  try {
                    const apiKey = getApiKey() || '';
                    const res = await fetch(`${API_URL}/dashboard/jobs?action=history&limit=20`, {
                      headers: { 'X-API-Key': apiKey },
                    });
                    if (res.ok) {
                      const data = await res.json();
                      setJobs(data.jobs || []);
                    }
                  } catch (err) {
                    console.error('Failed to load job history:', err);
                  }
                }}
                className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
              >
                View History
              </button>
            </div>
            <div className="px-6 py-4 text-center text-gray-500 text-sm">
              Click "View History" to see completed and failed jobs
            </div>
          </div>
        </div>
        )}
      </main>
    </div>
  );
}