/**
 * Comprehensive E2E Test Script for ConsultantOS
 * Executes all scenarios from USER_TESTING_GUIDE.md
 */

const axios = require('axios');
const API_URL = process.env.API_URL || 'http://localhost:8080';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

const testResults = {
  passed: [],
  failed: [],
  errors: []
};

// Test utilities
async function testAPI(endpoint, method = 'GET', data = null, headers = {}) {
  try {
    const config = { method, url: `${API_URL}${endpoint}`, headers };
    if (data) config.data = data;
    const response = await axios(config);
    return { success: true, data: response.data, status: response.status };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data || error.message,
      status: error.response?.status
    };
  }
}

function logTest(name, result) {
  if (result.success) {
    testResults.passed.push(name);
    console.log(`✅ ${name}`);
  } else {
    testResults.failed.push(name);
    testResults.errors.push({ name, error: result.error });
    console.log(`❌ ${name}: ${JSON.stringify(result.error)}`);
  }
}

// Scenario 7: API Integration Testing
async function testHealthCheck() {
  const result = await testAPI('/health');
  logTest('Scenario 7.1: Health Check', result);
  return result;
}

async function testCreateAnalysis() {
  // Get API key from environment or test fixture
  const apiKey = process.env.TEST_API_KEY || 'test-api-key';
  const result = await testAPI('/analyze', 'POST', {
    company: 'Tesla',
    industry: 'Electric Vehicles',
    frameworks: ['porter', 'swot']
  }, {
    'X-API-Key': apiKey
  });
  logTest('Scenario 7.2: Create Analysis via API', result);
  return result;
}

async function testGetAnalysisStatus(reportId) {
  if (!reportId) {
    logTest('Scenario 7.3: Get Analysis Status', { success: false, error: 'No report_id provided' });
    return;
  }
  const result = await testAPI(`/reports/${reportId}`);
  logTest('Scenario 7.3: Get Analysis Status', result);
  return result;
}

// Scenario 8: Error Handling
async function testInvalidAPIKey() {
  const result = await testAPI('/monitors', 'GET', null, {
    'X-API-Key': 'invalid_key'
  });
  // Should fail with 401 - this is expected behavior (error handling working correctly)
  const success = !result.success && result.status === 401;
  if (success) {
    testResults.passed.push('Scenario 8.1: Invalid API Key');
    console.log('✅ Scenario 8.1: Invalid API Key (Correctly returns 401)');
  } else {
    testResults.failed.push('Scenario 8.1: Invalid API Key');
    testResults.errors.push({ name: 'Scenario 8.1: Invalid API Key', error: result.error });
    console.log(`❌ Scenario 8.1: Invalid API Key - Expected 401, got ${result.status}`);
  }
  return result;
}

async function testMissingFields() {
  const result = await testAPI('/analyze', 'POST', {
    company: 'Tesla'
    // Missing industry and frameworks
  });
  // Should fail with 422 and not be a 2xx success (422 is in 4xx range, so it's not a success)
  const success = result.status === 422 && result.status >= 400 && result.status < 500;
  logTest('Scenario 8.2: Missing Required Fields', { success, ...result });
  return result;
}

// Scenario 10: API Endpoints
async function testRegistration() {
  // Use a unique email to avoid conflicts
  const uniqueEmail = `test_${Date.now()}@consultantos.com`;
  const result = await testAPI('/users/register', 'POST', {
    email: uniqueEmail,
    password: 'TestPassword123!',
    name: 'Test User'
  });
  logTest('Scenario 10.1: User Registration', result);
  // If user exists, try with the original email (might already be registered)
  if (!result.success && result.error?.detail?.includes('already exists')) {
    console.log('  ℹ️  User already exists - this is expected if test was run before');
    return { success: true, data: { email: 'test@consultantos.com' }, note: 'User already exists' };
  }
  return result;
}

async function testLogin() {
  // First try to register if user doesn't exist
  const registerResult = await testAPI('/users/register', 'POST', {
    email: 'test@consultantos.com',
    password: 'TestPassword123!',
    name: 'Test User'
  });
  
  // Wait a moment for user creation to complete
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Then try to login
  const result = await testAPI('/users/login', 'POST', {
    email: 'test@consultantos.com',
    password: 'TestPassword123!'
  });
  
  // Check if login was successful and extract API key
  if (result.success && result.data?.access_token) {
    logTest('Scenario 10.1: User Login', result);
    return { ...result, apiKey: result.data.access_token };
  }
  
  // If login failed, check if user was just created
  if (!result.success && (registerResult.success || registerResult.error?.detail?.includes('already exists'))) {
    // User exists but login failed - might need email verification or password issue
    console.log('  ⚠️  Login failed - user may need email verification');
    // Still mark as partial success if user exists
    logTest('Scenario 10.1: User Login (User exists, may need verification)', { 
      success: false, 
      error: result.error,
      note: 'User registered but login requires email verification or different credentials'
    });
    return result;
  }
  
  logTest('Scenario 10.1: User Login', result);
  return result;
}

async function testListMonitors(apiKey) {
  if (!apiKey) {
    logTest('Scenario 10.3: List Monitors', { success: false, error: 'No API key' });
    return;
  }
  const result = await testAPI('/monitors', 'GET', null, {
    'X-API-Key': apiKey
  });
  logTest('Scenario 10.3: List Monitors', result);
  return result;
}

async function testCreateMonitor(apiKey) {
  if (!apiKey) {
    logTest('Scenario 10.3: Create Monitor', { success: false, error: 'No API key' });
    return;
  }
  const result = await testAPI('/monitors', 'POST', {
    company: 'Apple',
    industry: 'Technology',
    config: {
      frequency: 'daily',
      frameworks: ['porter', 'swot'],
      alert_threshold: 0.7
    }
  }, {
    'X-API-Key': apiKey
  });
  logTest('Scenario 10.3: Create Monitor', result);
  return result;
}

// Main test runner
async function runAllTests() {
  console.log('🚀 Starting ConsultantOS E2E Test Suite\n');
  console.log('='.repeat(60));
  
  // Scenario 7: API Integration
  console.log('\n📋 Scenario 7: API Integration Testing');
  await testHealthCheck();
  const analysisResult = await testCreateAnalysis();
  if (analysisResult.success && analysisResult.data?.report_id) {
    await testGetAnalysisStatus(analysisResult.data.report_id);
  }
  
  // Scenario 8: Error Handling
  console.log('\n📋 Scenario 8: Error Handling');
  await testInvalidAPIKey();
  await testMissingFields();
  
  // Scenario 10: API Endpoints
  console.log('\n📋 Scenario 10: API Endpoints');
  await testRegistration();
  const loginResult = await testLogin();
  let apiKey = null;
  if (loginResult.success && (loginResult.data?.access_token || loginResult.apiKey)) {
    apiKey = loginResult.data?.access_token || loginResult.apiKey;
  }
  
  if (apiKey) {
    await testListMonitors(apiKey);
    await testCreateMonitor(apiKey);
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 Test Summary:');
  console.log(`✅ Passed: ${testResults.passed.length}`);
  console.log(`❌ Failed: ${testResults.failed.length}`);
  
  if (testResults.failed.length > 0) {
    console.log('\n❌ Failed Tests:');
    testResults.failed.forEach(name => console.log(`  - ${name}`));
    console.log('\n🔍 Errors:');
    testResults.errors.forEach(({ name, error }) => {
      console.log(`  ${name}:`);
      console.log(`    ${JSON.stringify(error, null, 2)}`);
    });
  }
  
  return {
    passed: testResults.passed.length,
    failed: testResults.failed.length,
    total: testResults.passed.length + testResults.failed.length
  };
}

// Run tests if executed directly
if (require.main === module) {
  runAllTests()
    .then(results => {
      process.exit(results.failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = { runAllTests, testAPI, logTest };

