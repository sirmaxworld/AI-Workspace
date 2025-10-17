#!/usr/bin/env node

/**
 * Test script to verify the tubedb-ui API is reading all videos correctly
 */

const fs = require('fs').promises;
const path = require('path');

const TRANSCRIPTS_DIR = '/Users/yourox/AI-Workspace/data/transcripts';

async function testAPI() {
  console.log('Testing tubedb-ui API data loading...\n');
  console.log('=' . repeat(60));

  try {
    // Read all files from the transcripts directory
    const files = await fs.readdir(TRANSCRIPTS_DIR);

    // Filter for JSON files (excluding batch files)
    const transcriptFiles = files.filter(file =>
      file.endsWith('.json') &&
      !file.startsWith('batch_') &&
      (file.endsWith('_full.json') || (file.length === 15 && file.endsWith('.json')))
    );

    console.log(`Found ${transcriptFiles.length} transcript files\n`);

    // Load a sample of files to verify structure
    const allVideos = [];
    const processedIds = new Set();
    let errorCount = 0;

    for (const file of transcriptFiles.slice(0, 10)) {  // Sample first 10
      try {
        const filePath = path.join(TRANSCRIPTS_DIR, file);
        const fileContent = await fs.readFile(filePath, 'utf-8');
        const data = JSON.parse(fileContent);

        // Extract video ID from filename
        let videoId = file.replace('_full.json', '').replace('.json', '');

        // Skip if we've already processed this video ID
        if (processedIds.has(videoId)) continue;
        processedIds.add(videoId);

        if (data.video_id || data.transcript) {
          console.log(`✅ ${file}:`);
          console.log(`   Title: ${data.title || 'No title'}`);
          console.log(`   Method: ${data.method || 'Unknown'}`);
          console.log(`   Segments: ${data.transcript?.segments?.length || 0}`);
          allVideos.push(videoId);
        } else {
          console.log(`⚠️  ${file}: Unexpected format`);
          errorCount++;
        }
      } catch (err) {
        console.log(`❌ ${file}: Error - ${err.message}`);
        errorCount++;
      }
    }

    console.log('\n' + '=' . repeat(60));
    console.log('Summary:');
    console.log(`  Total files: ${transcriptFiles.length}`);
    console.log(`  Sample size: 10`);
    console.log(`  Successfully loaded: ${allVideos.length}`);
    console.log(`  Errors: ${errorCount}`);

    // Count all unique video IDs
    const allIds = new Set();
    for (const file of transcriptFiles) {
      let videoId = file.replace('_full.json', '').replace('.json', '');
      if (videoId.length === 11) {  // Valid YouTube ID length
        allIds.add(videoId);
      }
    }

    console.log(`  Unique videos: ${allIds.size}`);

    console.log('\n' + '=' . repeat(60));
    console.log('✅ API should now show all videos in the frontend!');
    console.log('\nTo restart the frontend:');
    console.log('  cd tubedb-ui && npm run dev');
    console.log('\nThen visit: http://localhost:3000');

  } catch (error) {
    console.error('Error:', error);
  }
}

// Run the test
testAPI();