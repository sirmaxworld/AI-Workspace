// PM2 Configuration for TubeDB UI
// Ensures the server always runs on port 9000 with auto-restart

module.exports = {
  apps: [
    {
      name: 'tubedb-ui',
      script: 'npm',
      args: 'run start',
      cwd: '/Users/yourox/AI-Workspace/tubedb-ui',

      // Environment variables
      env: {
        NODE_ENV: 'production',
        PORT: 9000,
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 9000,
      },

      // Process management
      instances: 1,
      exec_mode: 'fork',

      // Auto-restart configuration
      autorestart: true,
      watch: false, // Set to true if you want to restart on file changes
      max_memory_restart: '1G',

      // Logging
      log_file: './logs/combined.log',
      error_file: './logs/error.log',
      out_file: './logs/output.log',
      time: true,

      // Advanced features
      min_uptime: '10s', // Minimum uptime to consider app as started
      max_restarts: 10, // Maximum restarts within min_uptime

      // Port management
      kill_timeout: 3000,
      wait_ready: true,

      // Ensure port 9000
      node_args: '--max_old_space_size=2048',

      // Pre and post hooks
      post_update: ['npm install'],
    },

    // Development mode configuration
    {
      name: 'tubedb-ui-dev',
      script: 'npm',
      args: 'run dev',
      cwd: '/Users/yourox/AI-Workspace/tubedb-ui',

      env: {
        NODE_ENV: 'development',
        PORT: 9000,
      },

      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: true,
      watch_delay: 1000,
      ignore_watch: [
        'node_modules',
        '.next',
        'logs',
        '.git',
        '*.log'
      ],

      log_file: './logs/dev-combined.log',
      error_file: './logs/dev-error.log',
      out_file: './logs/dev-output.log',
      time: true,
    }
  ]
};