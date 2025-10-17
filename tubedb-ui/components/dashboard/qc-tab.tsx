'use client';

import { useEffect, useState } from 'react';
import { Video } from '@/lib/types';
import { getLowQualityVideos } from '@/lib/chart-utils';
import { AlertCircle, TrendingDown, CheckCircle } from 'lucide-react';

export default function QCTab() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [threshold, setThreshold] = useState(20);

  useEffect(() => {
    fetch('/api/batch')
      .then(res => res.json())
      .then(data => {
        setVideos(data.videos || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading data:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading quality control data...</div>
      </div>
    );
  }

  const lowQualityVideos = getLowQualityVideos(videos, threshold);
  const enrichedCount = videos.filter(v => v.enrichment).length;
  const highQualityCount = videos.filter(v => v.enrichment && v.enrichment.avgActionability >= 60).length;
  const avgQuality = videos.filter(v => v.enrichment).reduce((sum, v) => sum + (v.enrichment?.avgActionability || 0), 0) / enrichedCount;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Quality Control</h2>
        <p className="text-gray-600">Monitor and improve data quality across your video library</p>
      </div>

      {/* Quality Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-green-100">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">High Quality Videos</p>
              <p className="text-2xl font-bold text-slate-800">{highQualityCount}</p>
              <p className="text-xs text-gray-500">Actionability ≥ 60%</p>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-amber-100">
              <TrendingDown className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Low Quality Videos</p>
              <p className="text-2xl font-bold text-slate-800">{lowQualityVideos.length}</p>
              <p className="text-xs text-gray-500">Actionability &lt; {threshold}%</p>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-blue-100">
              <AlertCircle className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Average Quality</p>
              <p className="text-2xl font-bold text-slate-800">{Math.round(avgQuality)}%</p>
              <p className="text-xs text-gray-500">Across all videos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Threshold Control */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Quality Threshold</h3>
            <p className="text-sm text-gray-600">Adjust the threshold for low-quality alerts</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Threshold:</span>
            <input
              type="range"
              min="10"
              max="50"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-32"
            />
            <span className="text-lg font-semibold text-slate-800 w-12">{threshold}%</span>
          </div>
        </div>
      </div>

      {/* Low Quality Videos Table */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">
          Low Quality Videos ({lowQualityVideos.length})
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Videos with actionability scores below {threshold}% that may need review or re-processing
        </p>

        {lowQualityVideos.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
            <p>No low-quality videos found!</p>
            <p className="text-sm">All videos meet the quality threshold of {threshold}%</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Video Title</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Actionability</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Specificity</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Evidence</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Insights</th>
                </tr>
              </thead>
              <tbody>
                {lowQualityVideos.map((video, idx) => (
                  <tr key={video.videoId} className={`border-b border-gray-100 ${idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}>
                    <td className="py-3 px-4 text-sm text-gray-800">{video.title}</td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                        video.actionability < 10 ? 'bg-red-100 text-red-700' :
                        video.actionability < 15 ? 'bg-orange-100 text-orange-700' :
                        'bg-amber-100 text-amber-700'
                      }`}>
                        {video.actionability}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-gray-600">{video.specificity}%</td>
                    <td className="py-3 px-4 text-center text-sm text-gray-600">{video.evidence}%</td>
                    <td className="py-3 px-4 text-center text-sm text-gray-600">{video.insights}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quality Improvement Recommendations */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Quality Improvement Tips</h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-blue-900">Low Actionability Scores</p>
              <p className="text-sm text-blue-700">Videos with low actionability may contain vague or theoretical insights. Consider re-enriching with updated prompts.</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-green-900">Good Practice</p>
              <p className="text-sm text-green-700">Videos with high evidence and specificity scores typically yield better business insights.</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
            <TrendingDown className="w-5 h-5 text-amber-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-amber-900">Low Insight Count</p>
              <p className="text-sm text-amber-700">Videos with fewer than 10 insights may benefit from transcript quality review or re-extraction.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
