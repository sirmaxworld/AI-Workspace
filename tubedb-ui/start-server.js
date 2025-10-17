#!/usr/bin/env node

/**
 * Simple script to start TubeDB UI on port 9000
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting TubeDB UI on port 9000...\n');

// Set environment variables
const env = {
  ...process.env,
  PORT: '9000',
  NODE_ENV: 'development'
};

// Start the Next.js development server
const server = spawn('npm', ['run', 'dev'], {
  cwd: path.join(__dirname),
  env: env,
  stdio: 'inherit',
  shell: true
});

server.on('error', (err) => {
  console.error('❌ Failed to start server:', err);
  process.exit(1);
});

server.on('close', (code) => {
  if (code !== 0) {
    console.error(`❌ Server exited with code ${code}`);
    process.exit(code);
  }
});

// Handle termination signals
process.on('SIGINT', () => {
  console.log('\n🛑 Stopping server...');
  server.kill('SIGINT');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Stopping server...');
  server.kill('SIGTERM');
  process.exit(0);
});

console.log('✅ Server starting on http://localhost:9000');
console.log('   Press Ctrl+C to stop\n');