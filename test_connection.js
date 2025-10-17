#!/usr/bin/env node

/**
 * Test script to verify the API connection and data retrieval
 */

const http = require('http');

// Test the Next.js API endpoint
const options = {
  hostname: 'localhost',
  port: 3000,
  path: '/api/batch',
  method: 'GET',
};

console.log('Testing API connection to http://localhost:3000/api/batch...\n');

const req = http.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    try {
      const jsonData = JSON.parse(data);

      console.log('✅ API Connection successful!');
      console.log('=====================================\n');

      if (jsonData.videos) {
        console.log(`📊 Found ${jsonData.videos.length} videos with insights\n`);

        // Show first 3 videos
        console.log('Sample Videos:');
        console.log('--------------');
        jsonData.videos.slice(0, 3).forEach((video, idx) => {
          console.log(`\n${idx + 1}. ${video.title}`);
          console.log(`   Video ID: ${video.video_id}`);

          if (video.insights) {
            const totalInsights = Object.values(video.insights).reduce((a, b) => a + b, 0);
            console.log(`   Total Insights: ${totalInsights}`);
            console.log(`   - Products: ${video.insights.products || 0}`);
            console.log(`   - Ideas: ${video.insights.ideas || 0}`);
            console.log(`   - Trends: ${video.insights.trends || 0}`);
          }

          if (video.featured_products && video.featured_products.length > 0) {
            console.log(`   Featured Products:`);
            video.featured_products.slice(0, 2).forEach(product => {
              console.log(`     • ${product.name}`);
            });
          }
        });

        console.log('\n=====================================');
        console.log('📈 Statistics:');
        console.log(`   - Total Videos: ${jsonData.stats.totalVideos}`);
        console.log(`   - Total Insights: ${jsonData.stats.totalSegments}`);
        console.log(`   - Data Quality: ${(jsonData.stats.avgQualityScore * 100).toFixed(0)}%`);
        console.log(`   - Avg Insights/Video: ${jsonData.stats.processingTime}`);

      } else {
        console.log('⚠️  No video data found in response');
      }

    } catch (error) {
      console.error('❌ Error parsing response:', error.message);
      console.log('Response:', data.substring(0, 500));
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Connection failed:', error.message);
  console.log('\nMake sure the Next.js dev server is running:');
  console.log('  cd tubedb-ui && npm run dev');
});

req.end();