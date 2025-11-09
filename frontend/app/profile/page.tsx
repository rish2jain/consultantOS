'use client';

import { useState, useEffect } from 'react';
import {
  ProfileSettings,
  NotificationSettings,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  Alert,
  Badge,
  Modal,
  Input
} from '@/app/components';
import { api } from '@/lib/api';
import { getApiKey, setApiKey, clearApiKey } from '@/lib/auth';
import {
  User,
  Bell,
  Key,
  BarChart,
  Copy,
  RefreshCw,
  Trash2,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface UserProfile {
  email: string;
  full_name: string;
  company?: string;
  job_title?: string;
  created_at: string;
  api_key?: string;
}

interface NotificationPreferences {
  new_comments: boolean;
  comment_replies: boolean;
  report_shared: boolean;
  new_versions: boolean;
  analysis_complete: boolean;
  email_enabled: boolean;
  frequency: 'instant' | 'daily' | 'weekly';
}

interface UsageStats {
  reports_created: number;
  api_calls_made: number;
  storage_used: number;
  plan: string;
  monthly_limit: number;
}

interface ApiKeyData {
  key: string;
  created_at: string;
  last_used?: string;
  usage_count: number;
}

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState(0);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [notificationSettings, setNotificationSettings] = useState<NotificationPreferences | null>(null);
  const [apiKeyData, setApiKeyData] = useState<ApiKeyData | null>(null);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [showApiKey, setShowApiKey] = useState(false);
  const [showGenerateKeyModal, setShowGenerateKeyModal] = useState(false);
  const [showDeleteKeyModal, setShowDeleteKeyModal] = useState(false);
  const [generatingKey, setGeneratingKey] = useState(false);
  const [deletingKey, setDeletingKey] = useState(false);

  // Get API key from in-memory storage (not localStorage for security)
  const apiKey = getApiKey();

  // Load profile data
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    if (!apiKey) {
      // Check if user data exists in localStorage (user might have refreshed page)
      const userData = typeof window !== 'undefined' ? localStorage.getItem('user') : null;
      if (userData) {
        setError('Session expired. Please log in again to view your profile.');
      } else {
        setError('API key required. Please log in.');
      }
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');

      // Load profile
      const profileData = await api.users.getProfile();
      setProfile(profileData);

      // Load notification settings
      const notifSettings = await api.notifications.getSettings();
      setNotificationSettings(notifSettings);

      // Mock API key data (replace with actual endpoint when available)
      setApiKeyData({
        key: apiKey,
        created_at: new Date().toISOString(),
        usage_count: 0
      });

      // Mock usage stats (replace with actual endpoint when available)
      setUsageStats({
        reports_created: 0,
        api_calls_made: 0,
        storage_used: 0,
        plan: 'Free',
        monthly_limit: 10
      });

    } catch (err) {
      console.error('Error loading profile:', err);
      setError('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = () => {
    setSuccess('Profile updated successfully');
    loadProfile();
    setTimeout(() => setSuccess(''), 3000);
  };

  const handleAccountDelete = () => {
    // Clear API key from memory
    clearApiKey();
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  const handleNotificationUpdate = async (settings: NotificationPreferences) => {
    setSuccess('Notification settings updated successfully');
    setTimeout(() => setSuccess(''), 3000);
  };

  const handleCopyApiKey = async () => {
    if (!apiKeyData?.key) return;

    try {
      await navigator.clipboard.writeText(apiKeyData.key);
      setSuccess('API key copied to clipboard');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to copy API key');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleGenerateApiKey = async () => {
    setGeneratingKey(true);
    setError('');

    try {
      // Call backend API to generate a cryptographically secure key
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/auth/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate API key');
      }

      const data = await response.json();
      const newKey = data.api_key;

      setApiKeyData({
        key: newKey,
        created_at: new Date().toISOString(),
        usage_count: 0
      });

      // Store new API key in memory (not localStorage for security)
      setApiKey(newKey);

      setSuccess('New API key generated successfully');
      setShowGenerateKeyModal(false);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to generate API key');
    } finally {
      setGeneratingKey(false);
    }
  };

  const handleDeleteApiKey = async () => {
    setDeletingKey(true);
    setError('');

    try {
      // This would call an actual API endpoint to delete the key
      await new Promise(resolve => setTimeout(resolve, 1000));

      setApiKeyData(null);

      // Clear API key from memory
      clearApiKey();

      setSuccess('API key deleted successfully');
      setShowDeleteKeyModal(false);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete API key');
    } finally {
      setDeletingKey(false);
    }
  };

  const maskApiKey = (key: string) => {
    if (key.length <= 8) return key;
    return key.substring(0, 7) + '•'.repeat(20) + key.substring(key.length - 4);
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              Loading profile...
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile & Settings</h1>
          {profile && (
            <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
              <span className="flex items-center gap-2">
                <User className="w-4 h-4" />
                {profile.full_name}
              </span>
              <span className="flex items-center gap-2">
                <Badge variant="secondary">
                  Member since {new Date(profile.created_at).toLocaleDateString()}
                </Badge>
              </span>
            </div>
          )}
        </div>

        {/* Global Alerts */}
        {success && (
          <Alert
            variant="success"
            title="Success"
            description={success}
            dismissible
            onClose={() => setSuccess('')}
            className="mb-6"
          />
        )}

        {error && (
          <Alert
            variant="error"
            title="Error"
            description={error}
            dismissible
            onClose={() => setError('')}
            className="mb-6"
          />
        )}

        {/* Tabbed Interface */}
        <Tabs activeIndex={activeTab} onChange={setActiveTab}>
          <TabList className="border-b border-gray-200 mb-6">
            <Tab>
              <User className="w-4 h-4 mr-2" />
              Profile
            </Tab>
            <Tab>
              <Bell className="w-4 h-4 mr-2" />
              Notifications
            </Tab>
            <Tab>
              <Key className="w-4 h-4 mr-2" />
              API Keys
            </Tab>
            <Tab>
              <BarChart className="w-4 h-4 mr-2" />
              Usage & Billing
            </Tab>
          </TabList>

          <TabPanels>
            {/* Profile Tab */}
            <TabPanel>
              <ProfileSettings
                apiKey={apiKey || undefined}
                onProfileUpdate={handleProfileUpdate}
                onAccountDelete={handleAccountDelete}
              />
            </TabPanel>

            {/* Notifications Tab */}
            <TabPanel>
              {notificationSettings && (
                <NotificationSettings
                  userId={profile?.email || ''}
                  currentSettings={notificationSettings}
                  onUpdate={handleNotificationUpdate}
                />
              )}
            </TabPanel>

            {/* API Keys Tab */}
            <TabPanel>
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>API Key Management</CardTitle>
                    <CardDescription>
                      Manage your API keys for programmatic access to ConsultantOS
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {apiKeyData ? (
                      <>
                        {/* Current API Key */}
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Current API Key
                            </label>
                            <div className="flex gap-2">
                              <Input
                                type={showApiKey ? 'text' : 'password'}
                                value={showApiKey ? apiKeyData.key : maskApiKey(apiKeyData.key)}
                                readOnly
                                fullWidth
                                className="font-mono text-sm"
                              />
                              <Button
                                variant="outline"
                                onClick={() => setShowApiKey(!showApiKey)}
                              >
                                {showApiKey ? 'Hide' : 'Show'}
                              </Button>
                              <Button
                                variant="outline"
                                onClick={handleCopyApiKey}
                                leftIcon={<Copy className="w-4 h-4" />}
                              >
                                Copy
                              </Button>
                            </div>
                          </div>

                          {/* Key Info */}
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Created:</span>
                              <p className="font-medium text-gray-900">
                                {new Date(apiKeyData.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div>
                              <span className="text-gray-600">Usage:</span>
                              <p className="font-medium text-gray-900">
                                {apiKeyData.usage_count.toLocaleString()} calls
                              </p>
                            </div>
                            {apiKeyData.last_used && (
                              <div>
                                <span className="text-gray-600">Last used:</span>
                                <p className="font-medium text-gray-900">
                                  {new Date(apiKeyData.last_used).toLocaleDateString()}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3 pt-4 border-t border-gray-200">
                          <Button
                            variant="outline"
                            onClick={() => setShowGenerateKeyModal(true)}
                            leftIcon={<RefreshCw className="w-4 h-4" />}
                          >
                            Regenerate Key
                          </Button>
                          <Button
                            variant="danger"
                            onClick={() => setShowDeleteKeyModal(true)}
                            leftIcon={<Trash2 className="w-4 h-4" />}
                          >
                            Delete Key
                          </Button>
                        </div>

                        {/* Warning */}
                        <Alert
                          variant="warning"
                          title="Keep your API key secure"
                          description="Never share your API key or commit it to version control. Regenerating your key will invalidate the old one."
                        />
                      </>
                    ) : (
                      <div className="text-center py-12">
                        <Key className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                          No API Key
                        </h3>
                        <p className="text-sm text-gray-600 mb-6">
                          Generate an API key to access ConsultantOS programmatically
                        </p>
                        <Button
                          onClick={() => setShowGenerateKeyModal(true)}
                          leftIcon={<Key className="w-4 h-4" />}
                        >
                          Generate API Key
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* API Documentation */}
                <Card>
                  <CardHeader>
                    <CardTitle>API Documentation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 mb-4">
                      Use your API key to authenticate requests to the ConsultantOS API.
                    </p>
                    <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
                      <code>
                        curl -X POST https://api.consultantos.com/analyze \<br />
                        &nbsp;&nbsp;-H "X-API-Key: YOUR_API_KEY" \<br />
                        &nbsp;&nbsp;-H "Content-Type: application/json" \<br />
                        &nbsp;&nbsp;-d '{`{"company": "Tesla", "industry": "Automotive"}`}'
                      </code>
                    </div>
                    <div className="mt-4">
                      <a
                        href="/docs"
                        className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                      >
                        View full API documentation →
                      </a>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabPanel>

            {/* Usage & Billing Tab */}
            <TabPanel>
              {usageStats && (
                <div className="space-y-6">
                  {/* Current Plan */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle>Current Plan</CardTitle>
                          <CardDescription>Your subscription and usage details</CardDescription>
                        </div>
                        <Badge variant="primary" className="text-lg px-4 py-2">
                          {usageStats.plan}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Reports Created */}
                        <div className="bg-blue-50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-blue-900">
                              Reports Created
                            </span>
                            <CheckCircle className="w-5 h-5 text-blue-600" />
                          </div>
                          <p className="text-2xl font-bold text-blue-900">
                            {usageStats.reports_created}
                          </p>
                          <p className="text-xs text-blue-700 mt-1">
                            of {usageStats.monthly_limit} this month
                          </p>
                        </div>

                        {/* API Calls */}
                        <div className="bg-green-50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-green-900">
                              API Calls
                            </span>
                            <BarChart className="w-5 h-5 text-green-600" />
                          </div>
                          <p className="text-2xl font-bold text-green-900">
                            {usageStats.api_calls_made.toLocaleString()}
                          </p>
                          <p className="text-xs text-green-700 mt-1">
                            this month
                          </p>
                        </div>

                        {/* Storage Used */}
                        <div className="bg-purple-50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-purple-900">
                              Storage Used
                            </span>
                            <BarChart className="w-5 h-5 text-purple-600" />
                          </div>
                          <p className="text-2xl font-bold text-purple-900">
                            {formatBytes(usageStats.storage_used)}
                          </p>
                          <p className="text-xs text-purple-700 mt-1">
                            of 1 GB available
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Upgrade Section */}
                  {usageStats.plan === 'Free' && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Upgrade Your Plan</CardTitle>
                        <CardDescription>
                          Unlock more features and higher limits
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Pro Plan */}
                          <div className="border-2 border-primary-200 rounded-lg p-6">
                            <h3 className="text-xl font-bold text-gray-900 mb-2">
                              Pro
                            </h3>
                            <p className="text-3xl font-bold text-primary-600 mb-4">
                              $49<span className="text-lg text-gray-600">/month</span>
                            </p>
                            <ul className="space-y-2 mb-6">
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                50 reports per month
                              </li>
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                Unlimited API calls
                              </li>
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                10 GB storage
                              </li>
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                Priority support
                              </li>
                            </ul>
                            <Button fullWidth>
                              Upgrade to Pro
                            </Button>
                          </div>

                          {/* Enterprise Plan */}
                          <div className="border-2 border-gray-200 rounded-lg p-6">
                            <h3 className="text-xl font-bold text-gray-900 mb-2">
                              Enterprise
                            </h3>
                            <p className="text-3xl font-bold text-gray-900 mb-4">
                              Custom
                            </p>
                            <ul className="space-y-2 mb-6">
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                Unlimited reports
                              </li>
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                Unlimited API calls
                              </li>
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                Unlimited storage
                              </li>
                              <li className="flex items-center text-sm text-gray-700">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                Dedicated support
                              </li>
                            </ul>
                            <Button variant="outline" fullWidth>
                              Contact Sales
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>

        {/* Generate API Key Modal */}
        <Modal
          isOpen={showGenerateKeyModal}
          onClose={() => !generatingKey && setShowGenerateKeyModal(false)}
          title={apiKeyData ? "Regenerate API Key" : "Generate API Key"}
        >
          <div className="space-y-4">
            <Alert
              variant="warning"
              title="Warning"
              description={
                apiKeyData
                  ? "Regenerating your API key will invalidate the old one. Any applications using the old key will stop working."
                  : "Your API key will only be displayed once. Make sure to save it securely."
              }
            />

            <p className="text-sm text-gray-700">
              {apiKeyData
                ? "Are you sure you want to regenerate your API key?"
                : "Generate a new API key to access the ConsultantOS API programmatically."}
            </p>

            <div className="flex gap-3 justify-end pt-4">
              <Button
                variant="outline"
                onClick={() => setShowGenerateKeyModal(false)}
                disabled={generatingKey}
              >
                Cancel
              </Button>
              <Button
                onClick={handleGenerateApiKey}
                isLoading={generatingKey}
                disabled={generatingKey}
              >
                {apiKeyData ? "Regenerate Key" : "Generate Key"}
              </Button>
            </div>
          </div>
        </Modal>

        {/* Delete API Key Modal */}
        <Modal
          isOpen={showDeleteKeyModal}
          onClose={() => !deletingKey && setShowDeleteKeyModal(false)}
          title="Delete API Key"
        >
          <div className="space-y-4">
            <Alert
              variant="error"
              title="This action cannot be undone"
              description="Deleting your API key will immediately revoke access for all applications using it."
            />

            <p className="text-sm text-gray-700">
              Are you sure you want to delete your API key?
            </p>

            <div className="flex gap-3 justify-end pt-4">
              <Button
                variant="outline"
                onClick={() => setShowDeleteKeyModal(false)}
                disabled={deletingKey}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDeleteApiKey}
                isLoading={deletingKey}
                disabled={deletingKey}
              >
                Yes, Delete Key
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  );
}
