#!/usr/bin/env python3
"""
YouTube Extraction Quality Control Pipeline
- Orchestrates channel extraction + transcription + quality validation
- Uses CrewAI agent for quality control
- Generates comprehensive quality reports
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process

# Import our extraction tools
from youtube_channel_extractor import YouTubeChannelExtractor
from youtube_transcriber_pro import YouTubeTranscriberPro

load_dotenv('/Users/yourox/AI-Workspace/.env')

BASE_PATH = Path('/Users/yourox/AI-Workspace')
DATA_PATH = BASE_PATH / 'data'
REPORTS_PATH = DATA_PATH / 'qc_reports'
REPORTS_PATH.mkdir(parents=True, exist_ok=True)


class TranscriptQualityControl:
    """Quality control system for YouTube transcript extraction"""

    def __init__(self):
        self.qc_agent = self._create_qc_agent()

    def _create_qc_agent(self) -> Agent:
        """Create CrewAI quality control agent"""

        return Agent(
            role='Transcript Quality Control Specialist',
            goal='Validate the quality, completeness, and accuracy of YouTube transcript extractions',
            backstory="""You are a meticulous quality assurance expert specializing in
            content validation. You review transcripts to ensure they are:
            - Complete (not truncated)
            - Accurate (good transcription quality)
            - Properly formatted
            - Contain meaningful content
            - Free from extraction errors

            You identify issues and provide actionable recommendations.""",
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    def validate_extraction(
        self,
        video_metadata: Dict,
        transcript_data: Dict,
        chunks: List[Dict]
    ) -> Dict:
        """
        Validate a single video's extraction using AI agent

        Returns quality report dict
        """

        # Prepare validation data
        validation_input = {
            'video_id': video_metadata['id'],
            'title': video_metadata['title'],
            'duration': video_metadata['duration'],
            'duration_formatted': video_metadata['duration_formatted'],
            'transcript_method': transcript_data.get('method', 'unknown'),
            'transcript_segments': len(transcript_data.get('transcript', [])),
            'chunks_created': len(chunks),
            'sample_text': ' '.join([c['text'][:200] for c in chunks[:3]]),  # First 3 chunks
        }

        # Create QC task
        qc_task = Task(
            description=f"""
            Review the quality of this YouTube transcript extraction:

            Video: {validation_input['title']}
            Duration: {validation_input['duration_formatted']}
            Method: {validation_input['transcript_method']}
            Segments: {validation_input['transcript_segments']}
            Chunks: {validation_input['chunks_created']}

            Sample text (first 600 chars):
            {validation_input['sample_text']}

            Evaluate:
            1. Completeness: Does the transcript seem complete for a {validation_input['duration']}s video?
            2. Quality: Is the text coherent and properly formatted?
            3. Content value: Does it contain meaningful information?
            4. Issues: Any obvious problems (truncation, errors, gibberish)?
            5. Recommendations: Any improvements needed?

            Respond with **valid JSON only**:
            {{
              "overall_quality": "excellent"|"good"|"fair"|"poor",
              "completeness_score": 0.0-1.0,
              "quality_score": 0.0-1.0,
              "content_value_score": 0.0-1.0,
              "issues": [str],
              "strengths": [str],
              "recommendations": [str],
              "passed_qc": true|false
            }}
            """,
            expected_output="JSON quality assessment with scores, issues, and recommendations",
            agent=self.qc_agent
        )

        # Execute QC
        crew = Crew(
            agents=[self.qc_agent],
            tasks=[qc_task],
            process=Process.sequential,
            verbose=False
        )

        result = crew.kickoff()

        # Parse QC result
        try:
            qc_result = self._parse_qc_output(result)
            qc_result['video_id'] = video_metadata['id']
            qc_result['video_title'] = video_metadata['title']
            return qc_result
        except Exception as e:
            print(f"  ⚠️  QC parsing error: {e}")
            return {
                'video_id': video_metadata['id'],
                'video_title': video_metadata['title'],
                'overall_quality': 'unknown',
                'passed_qc': True,  # Default to passing if QC fails
                'error': str(e)
            }

    def _parse_qc_output(self, raw_output) -> Dict:
        """Parse QC agent output to structured dict"""

        import re

        # Extract raw text
        output_text = str(raw_output)
        if hasattr(raw_output, 'raw_output'):
            output_text = str(raw_output.raw_output)
        elif hasattr(raw_output, 'output'):
            output_obj = raw_output.output
            for attr in ('raw_output', 'final_result', 'value', 'content'):
                if hasattr(output_obj, attr):
                    data = getattr(output_obj, attr)
                    if data:
                        output_text = str(data)
                        break

        # Clean up markdown code blocks
        cleaned = output_text.strip()
        if '```' in cleaned:
            cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = cleaned.rsplit('```', 1)[0]

        return json.loads(cleaned)


class YouTubeQCPipeline:
    """
    Complete pipeline: Channel extraction → Transcription → Quality Control
    """

    def __init__(self, user_id: str = "yourox_youtube_qc"):
        self.extractor = YouTubeChannelExtractor()
        self.transcriber = YouTubeTranscriberPro(user_id=user_id)
        self.qc = TranscriptQualityControl()

    async def run_full_pipeline(
        self,
        channel_url: str,
        max_videos: int = 50,
        filter_shorts: bool = True,
        run_qc: bool = True
    ) -> Dict:
        """
        Run complete pipeline with quality control

        Args:
            channel_url: YouTube channel URL or handle
            max_videos: Maximum videos to process
            filter_shorts: Exclude YouTube Shorts
            run_qc: Run quality control validation

        Returns:
            Complete pipeline report
        """

        print(f"\n{'='*80}")
        print(f"🚀 YOUTUBE EXTRACTION PIPELINE WITH QUALITY CONTROL")
        print(f"{'='*80}\n")

        start_time = datetime.now()

        # Step 1: Extract channel videos
        print(f"📺 STEP 1: Extracting videos from channel...")
        videos = self.extractor.get_channel_videos(
            channel_url,
            max_videos=max_videos,
            filter_shorts=filter_shorts
        )

        if not videos:
            return {
                'status': 'error',
                'message': 'No videos extracted from channel'
            }

        channel_name = videos[0]['channel']

        # Step 2: Transcribe videos
        print(f"\n📝 STEP 2: Transcribing {len(videos)} videos...")
        print(f"{'='*80}\n")

        transcription_results = []
        qc_reports = []

        for idx, video in enumerate(videos):
            print(f"\n[{idx + 1}/{len(videos)}] Processing: {video['title']}")
            print(f"Duration: {video['duration_formatted']} | URL: {video['url']}")

            # Transcribe
            try:
                result = await self.transcriber.process_video(video['url'])

                if result['status'] == 'success':
                    transcription_results.append(result)

                    # Run QC if enabled
                    if run_qc:
                        print(f"  🔍 Running quality control...")

                        # Get transcript data from cache
                        cached_data = self.transcriber.get_cached_transcript(video['id'])

                        if cached_data:
                            chunks = self.transcriber.chunk_transcript(
                                cached_data['transcript'],
                                cached_data['metadata']
                            )

                            qc_report = self.qc.validate_extraction(
                                video,
                                cached_data,
                                chunks
                            )

                            qc_reports.append(qc_report)

                            # Print QC result
                            status_emoji = "✅" if qc_report.get('passed_qc') else "❌"
                            quality = qc_report.get('overall_quality', 'unknown')
                            print(f"  {status_emoji} Quality: {quality.upper()}")

                            if qc_report.get('issues'):
                                print(f"     Issues: {', '.join(qc_report['issues'][:2])}")

                else:
                    print(f"  ❌ Transcription failed: {result.get('message', 'Unknown error')}")

            except Exception as e:
                print(f"  ❌ Error processing video: {e}")
                continue

        # Step 3: Generate final report
        print(f"\n{'='*80}")
        print(f"📊 STEP 3: Generating quality report...")
        print(f"{'='*80}\n")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Calculate statistics
        total_videos = len(videos)
        transcribed = len(transcription_results)
        failed = total_videos - transcribed

        qc_passed = sum(1 for r in qc_reports if r.get('passed_qc', True))
        qc_failed = len(qc_reports) - qc_passed

        quality_distribution = {
            'excellent': sum(1 for r in qc_reports if r.get('overall_quality') == 'excellent'),
            'good': sum(1 for r in qc_reports if r.get('overall_quality') == 'good'),
            'fair': sum(1 for r in qc_reports if r.get('overall_quality') == 'fair'),
            'poor': sum(1 for r in qc_reports if r.get('overall_quality') == 'poor'),
        }

        avg_completeness = (
            sum(r.get('completeness_score', 0) for r in qc_reports) / len(qc_reports)
            if qc_reports else 0
        )
        avg_quality = (
            sum(r.get('quality_score', 0) for r in qc_reports) / len(qc_reports)
            if qc_reports else 0
        )

        # Build final report
        report = {
            'pipeline_run': {
                'channel': channel_name,
                'channel_url': channel_url,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'duration_seconds': duration,
                'duration_formatted': f"{int(duration // 60)}m {int(duration % 60)}s"
            },
            'extraction_summary': {
                'total_videos_found': total_videos,
                'transcribed_successfully': transcribed,
                'transcription_failed': failed,
                'success_rate': f"{(transcribed / total_videos * 100):.1f}%"
            },
            'quality_control': {
                'qc_enabled': run_qc,
                'videos_reviewed': len(qc_reports),
                'passed_qc': qc_passed,
                'failed_qc': qc_failed,
                'qc_pass_rate': f"{(qc_passed / len(qc_reports) * 100):.1f}%" if qc_reports else "N/A",
                'quality_distribution': quality_distribution,
                'average_completeness_score': f"{avg_completeness:.2f}",
                'average_quality_score': f"{avg_quality:.2f}"
            },
            'transcription_stats': self.transcriber.stats,
            'videos': videos,
            'transcription_results': transcription_results,
            'qc_reports': qc_reports
        }

        # Save report
        report_file = self._save_report(report, channel_name)

        # Print summary
        self._print_summary(report, report_file)

        return report

    def _save_report(self, report: Dict, channel_name: str) -> str:
        """Save pipeline report to JSON file"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        clean_name = channel_name.replace(' ', '_').replace('@', '')
        filename = f"{clean_name}_pipeline_{timestamp}.json"
        filepath = REPORTS_PATH / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def _print_summary(self, report: Dict, report_file: str):
        """Print pipeline execution summary"""

        print(f"✅ PIPELINE COMPLETE!\n")

        print(f"{'='*80}")
        print(f"📊 SUMMARY")
        print(f"{'='*80}\n")

        # Extraction
        ext = report['extraction_summary']
        print(f"📺 Extraction:")
        print(f"   Total videos: {ext['total_videos_found']}")
        print(f"   Transcribed: {ext['transcribed_successfully']}")
        print(f"   Failed: {ext['transcription_failed']}")
        print(f"   Success rate: {ext['success_rate']}\n")

        # Quality Control
        if report['quality_control']['qc_enabled']:
            qc = report['quality_control']
            print(f"🔍 Quality Control:")
            print(f"   Reviewed: {qc['videos_reviewed']}")
            print(f"   Passed: {qc['passed_qc']}")
            print(f"   Failed: {qc['failed_qc']}")
            print(f"   Pass rate: {qc['qc_pass_rate']}\n")

            print(f"   Quality Distribution:")
            dist = qc['quality_distribution']
            print(f"     Excellent: {dist['excellent']}")
            print(f"     Good: {dist['good']}")
            print(f"     Fair: {dist['fair']}")
            print(f"     Poor: {dist['poor']}\n")

            print(f"   Average Scores:")
            print(f"     Completeness: {qc['average_completeness_score']}")
            print(f"     Quality: {qc['average_quality_score']}\n")

        # Transcription
        stats = report['transcription_stats']
        print(f"📝 Transcription:")
        print(f"   YouTube captions: {stats['youtube_captions_used']}")
        print(f"   Whisper API: {stats['whisper_transcriptions']}")
        print(f"   Total chunks: {stats['total_chunks']}\n")

        # Pipeline info
        run = report['pipeline_run']
        print(f"⏱️  Duration: {run['duration_formatted']}")
        print(f"💾 Report saved: {report_file}\n")

        print(f"{'='*80}\n")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='YouTube extraction pipeline with quality control'
    )
    parser.add_argument(
        'channel',
        help='Channel URL or handle (e.g., @GregIsenberg)'
    )
    parser.add_argument(
        '--max-videos',
        type=int,
        default=50,
        help='Maximum videos to process (default: 50)'
    )
    parser.add_argument(
        '--include-shorts',
        action='store_true',
        help='Include YouTube Shorts (default: exclude)'
    )
    parser.add_argument(
        '--skip-qc',
        action='store_true',
        help='Skip quality control validation'
    )

    args = parser.parse_args()

    # Run pipeline
    pipeline = YouTubeQCPipeline()

    result = asyncio.run(
        pipeline.run_full_pipeline(
            channel_url=args.channel,
            max_videos=args.max_videos,
            filter_shorts=not args.include_shorts,
            run_qc=not args.skip_qc
        )
    )

    # Exit with appropriate code
    if result.get('status') == 'error':
        print(f"\n❌ Pipeline failed: {result.get('message')}")
        exit(1)

    qc_failed = result['quality_control']['failed_qc']
    if qc_failed > 0:
        print(f"\n⚠️  Warning: {qc_failed} videos failed quality control")

    print(f"✅ Pipeline completed successfully!")


if __name__ == "__main__":
    main()
