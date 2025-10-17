import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const META_INTELLIGENCE_PATH = '/Users/yourox/AI-Workspace/data/meta_intelligence/meta_intelligence_report.json';

export async function GET() {
  try {
    const content = await fs.readFile(META_INTELLIGENCE_PATH, 'utf-8');
    const data = JSON.parse(content);

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error loading meta-intelligence:', error);
    return NextResponse.json(
      { error: 'Failed to load meta-intelligence data' },
      { status: 500 }
    );
  }
}
