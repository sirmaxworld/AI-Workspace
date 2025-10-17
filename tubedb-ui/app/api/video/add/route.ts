import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import { config } from '@/lib/config';
import { Video } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url } = body;

    if (!url) {
      return NextResponse.json(
        { error: 'YouTube URL is required' },
        { status: 400 }
      );
    }

    // Extract video ID from URL
    const videoId = extractVideoId(url);
    if (!videoId) {
      return NextResponse.json(
        { error: 'Invalid YouTube URL' },
        { status: 400 }
      );
    }

    // Load existing batch data
    const fileContent = await fs.readFile(config.dataPath, 'utf-8');
    const videos: Video[] = JSON.parse(fileContent);

    // Check if video already exists
    const existingVideo = videos.find(v => v.video_id === videoId);
    if (existingVideo) {
      return NextResponse.json(
        { error: 'Video already exists in database', video: existingVideo },
        { status: 409 }
      );
    }

    // Return video ID and instruction for manual processing
    return NextResponse.json({
      message: 'Video ID extracted. Please use external tools to extract transcript.',
      videoId,
      instructions: {
        step1: 'Use yt-dlp or similar tool to extract transcript',
        step2: 'Process transcript with your analysis pipeline',
        step3: 'Add the processed video data to the batch file',
      },
      nextSteps: {
        command: `yt-dlp --write-auto-sub --skip-download --sub-format json3 https://www.youtube.com/watch?v=${videoId}`,
        dataPath: config.dataPath,
      }
    });
  } catch (error) {
    console.error('Error adding video:', error);
    return NextResponse.json(
      { error: 'Failed to process video request' },
      { status: 500 }
    );
  }
}

function extractVideoId(url: string): string | null {
  try {
    // Handle various YouTube URL formats
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /^([a-zA-Z0-9_-]{11})$/, // Direct video ID
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }

    return null;
  } catch {
    return null;
  }
}
