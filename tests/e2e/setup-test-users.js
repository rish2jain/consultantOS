/**
 * Setup script to create test users before running E2E tests
 * Run this before executing the test suite: node tests/e2e/setup-test-users.js
 */

const axios = require('axios');
const config = require('./puppeteer.config');

const BACKEND_URL = config.backendUrl || 'http://localhost:8080';

async function createTestUser(email, password, name) {
  try {
    console.log(`Creating test user: ${email}...`);
    const response = await axios.post(`${BACKEND_URL}/users/register`, {
      email,
      password,
      name
    }, {
      validateStatus: (status) => status < 500 // Don't throw on 4xx errors
    });
    
    if (response.status === 200 || response.status === 201) {
      console.log(`✅ User created: ${email}`);
      return { success: true, user_id: response.data.user_id };
    } else if (response.status === 409) {
      console.log(`ℹ️  User already exists: ${email}`);
      return { success: true, exists: true };
    } else {
      console.error(`❌ Failed to create user: ${response.status}`, response.data);
      return { success: false, error: response.data };
    }
  } catch (error) {
    if (error.response?.status === 409) {
      console.log(`ℹ️  User already exists: ${email}`);
      return { success: true, exists: true };
    }
    console.error(`❌ Error creating user ${email}:`, error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
    return { success: false, error: error.message };
  }
}

async function verifyLogin(email, password) {
  try {
    console.log(`Verifying login for: ${email}...`);
    const response = await axios.post(`${BACKEND_URL}/users/login`, {
      email,
      password
    }, {
      validateStatus: (status) => status < 500
    });
    
    if (response.status === 200) {
      const token = response.data.access_token || response.data.api_key;
      if (token) {
        console.log(`✅ Login successful for: ${email}`);
        return { success: true, token };
      } else {
        console.log(`⚠️  Login response missing token for: ${email}`);
        return { success: false, error: 'No token in response' };
      }
    } else {
      console.error(`❌ Login failed for ${email}: ${response.status}`, response.data);
      return { success: false, error: response.data };
    }
  } catch (error) {
    console.error(`❌ Login error for ${email}:`, error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
    return { success: false, error: error.message };
  }
}

async function setupTestUsers() {
  console.log('🚀 Setting up test users...\n');
  
  // Create a fixed test user that tests can use
  const fixedTestUser = {
    email: 'testuser@example.com',
    password: 'TestPassword123!',
    name: 'Test User'
  };
  
  // Also create a user with the dynamic email pattern used by tests
  const timestamp = Date.now();
  const dynamicTestUser = {
    email: `test-${timestamp}@example.com`,
    password: 'TestPassword123!',
    name: 'Test User'
  };
  
  const results = [];
  
  // Create fixed test user
  const fixedResult = await createTestUser(
    fixedTestUser.email,
    fixedTestUser.password,
    fixedTestUser.name
  );
  results.push({ user: fixedTestUser.email, ...fixedResult });
  
  // Wait a bit between requests
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Create dynamic test user
  const dynamicResult = await createTestUser(
    dynamicTestUser.email,
    dynamicTestUser.password,
    dynamicTestUser.name
  );
  results.push({ user: dynamicTestUser.email, ...dynamicResult });
  
  console.log('\n📋 Verifying login...\n');
  
  // Verify login for fixed user
  await new Promise(resolve => setTimeout(resolve, 1000));
  const loginResult = await verifyLogin(fixedTestUser.email, fixedTestUser.password);
  
  console.log('\n📊 Summary:');
  console.log(`  Fixed user (${fixedTestUser.email}): ${fixedResult.success ? '✅ Created' : '❌ Failed'}`);
  console.log(`  Dynamic user (${dynamicTestUser.email}): ${dynamicResult.success ? '✅ Created' : '❌ Failed'}`);
  console.log(`  Login verification: ${loginResult.success ? '✅ Working' : '❌ Failed'}`);
  
  if (loginResult.success) {
    console.log('\n✅ Test users setup complete!');
    console.log(`\n📝 Use these credentials in tests:`);
    console.log(`   Email: ${fixedTestUser.email}`);
    console.log(`   Password: ${fixedTestUser.password}`);
    process.exit(0);
  } else {
    console.log('\n⚠️  Test users created but login verification failed.');
    console.log('   This might be due to email verification requirements.');
    console.log('   Tests may still work if they handle login failures gracefully.');
    process.exit(1);
  }
}

// Run setup
setupTestUsers().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});

