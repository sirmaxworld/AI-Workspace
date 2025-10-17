'use client';

import { useState } from 'react';
import { Video } from '@/lib/types';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search, Clock, MessageSquare, Star, Play } from 'lucide-react';
import { formatDuration, getQualityColor, getQualityLabel } from '@/lib/utils';

interface VideoModalProps {
  video: Video | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function VideoModal({ video, open, onOpenChange }: VideoModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  if (!video) return null;

  const totalDuration = video.transcript.segments.reduce((sum, seg) => sum + seg.duration, 0);
  const qualityScore = video.qc_verification?.quality_score || 0;

  // Filter segments based on search query
  const filteredSegments = searchQuery
    ? video.transcript.segments.filter(seg =>
        seg.text.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : video.transcript.segments;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] glass-card border-2 border-purple-500/30">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-foreground pr-8">
            {video.title}
          </DialogTitle>
          <DialogDescription className="flex flex-wrap gap-3 items-center mt-2">
            <span className="flex items-center gap-1 text-muted-foreground">
              <Clock className="w-4 h-4" />
              {formatDuration(totalDuration)}
            </span>
            <span className="flex items-center gap-1 text-muted-foreground">
              <MessageSquare className="w-4 h-4" />
              {video.transcript.segment_count} segments
            </span>
            <span className="flex items-center gap-1 text-muted-foreground">
              <Play className="w-4 h-4" />
              Agent {video.agent_id}
            </span>
            {video.qc_verification && (
              <Badge className={`${getQualityColor(qualityScore)} border-0`}>
                <Star className="w-3 h-3 mr-1" />
                {getQualityLabel(qualityScore)} ({(qualityScore * 100).toFixed(0)}%)
              </Badge>
            )}
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
          <TabsList className="grid w-full grid-cols-3 glass">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="transcript">Transcript</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-4">
            {video.qc_verification && (
              <>
                {/* Summary */}
                {video.qc_verification.summary && (
                  <div className="glass-card p-4 rounded-lg">
                    <h3 className="font-semibold text-foreground mb-2">Summary</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {video.qc_verification.summary}
                    </p>
                  </div>
                )}

                {/* Key Topics */}
                {video.qc_verification.key_topics && video.qc_verification.key_topics.length > 0 && (
                  <div className="glass-card p-4 rounded-lg">
                    <h3 className="font-semibold text-foreground mb-3">Key Topics</h3>
                    <div className="flex flex-wrap gap-2">
                      {video.qc_verification.key_topics.map((topic, idx) => (
                        <Badge
                          key={idx}
                          variant="secondary"
                          className="bg-blue-900/30 text-blue-300 border border-blue-500/30"
                        >
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quality Metrics */}
                <div className="glass-card p-4 rounded-lg">
                  <h3 className="font-semibold text-foreground mb-3">Quality Metrics</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Quality Score</span>
                      <span className={`font-semibold ${getQualityColor(qualityScore)}`}>
                        {(qualityScore * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Total Segments</span>
                      <span className="font-semibold text-foreground">
                        {video.transcript.segment_count}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Language</span>
                      <span className="font-semibold text-foreground uppercase">
                        {video.transcript.language}
                      </span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </TabsContent>

          <TabsContent value="transcript" className="space-y-4 mt-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search transcript..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 glass-card border-purple-500/20"
              />
            </div>

            {searchQuery && (
              <div className="text-sm text-muted-foreground">
                Found {filteredSegments.length} segment{filteredSegments.length !== 1 ? 's' : ''}
              </div>
            )}

            {/* Transcript Segments */}
            <ScrollArea className="h-[400px] glass-card rounded-lg p-4">
              <div className="space-y-3">
                {filteredSegments.map((segment, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-900/30 border border-slate-700/30 hover:border-cyan-500/30 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-cyan-400">
                        {formatDuration(segment.start)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        ({formatDuration(segment.duration)})
                      </span>
                    </div>
                    <p className="text-sm text-foreground leading-relaxed">{segment.text}</p>
                  </div>
                ))}
                {filteredSegments.length === 0 && (
                  <div className="text-center text-muted-foreground py-8">
                    No segments found matching "{searchQuery}"
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="details" className="space-y-4 mt-4">
            <div className="glass-card p-4 rounded-lg space-y-3">
              <div className="flex justify-between items-center border-b border-slate-700/30 pb-2">
                <span className="text-sm font-medium text-muted-foreground">Video ID</span>
                <span className="text-sm font-mono text-foreground">{video.video_id}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-700/30 pb-2">
                <span className="text-sm font-medium text-muted-foreground">Agent ID</span>
                <span className="text-sm text-foreground">{video.agent_id}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-700/30 pb-2">
                <span className="text-sm font-medium text-muted-foreground">Method</span>
                <span className="text-sm text-foreground">{video.method}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-700/30 pb-2">
                <span className="text-sm font-medium text-muted-foreground">Language</span>
                <span className="text-sm text-foreground uppercase">{video.transcript.language}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-muted-foreground">Verifier</span>
                <span className="text-sm text-foreground">
                  {video.qc_verification?.verifier || 'N/A'}
                </span>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
