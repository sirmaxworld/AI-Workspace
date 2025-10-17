# YouTube Vault - Code Examples & Patterns

This document provides code snippets and patterns from the YouTube Vault project that can be directly adopted for TubeDB UI.

---

## 1. COMPONENT PATTERNS

### CVA (Class Variance Authority) Pattern - Button Component

```typescript
// /components/ui/button.tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';
export { Button, buttonVariants };
```

**Usage:**
```typescript
<Button variant="default" size="lg">Click me</Button>
<Button variant="outline" size="sm">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Delete</Button>
```

---

### Composite Component Pattern - Card

```typescript
// /components/ui/card.tsx
import { cn } from '@/lib/utils';

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('rounded-lg border bg-card text-card-foreground shadow-sm', className)}
      {...props}
    />
  )
);
Card.displayName = 'Card';

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />
  )
);
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn('text-2xl font-semibold leading-none tracking-tight', className)}
      {...props}
    />
  )
);
CardTitle.displayName = 'CardTitle';

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
  )
);
CardContent.displayName = 'CardContent';

export { Card, CardHeader, CardTitle, CardContent };
```

**Usage:**
```typescript
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content goes here
  </CardContent>
</Card>
```

---

## 2. UTILITY FUNCTIONS

### Class Name Merger - `cn()`

```typescript
// /lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage:
cn('px-4', 'px-8') // Result: 'px-8' (correctly merges)
cn('text-red-500', condition && 'text-blue-500') // Conditional classes
```

### Formatting Functions

```typescript
// /lib/utils.ts
export function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}
// 1500 => "1.5K", 2500000 => "2.5M"

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}
// 3665 => "1:01:05", 125 => "2:05"

export function formatRelativeTime(date: string): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}
// "2024-01-15" => "2 days ago"
```

---

## 3. REAL-WORLD COMPONENT EXAMPLES

### VideoCard Component - Grid & List Views

```typescript
// /components/video-card.tsx
'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';
import { Eye, Clock, Play } from 'lucide-react';
import { Video } from '@/lib/types';

interface VideoCardProps {
  video: Video;
  viewMode?: 'grid' | 'list';
}

export function VideoCard({ video, viewMode = 'grid' }: VideoCardProps) {
  const [thumbnailError, setThumbnailError] = useState(false);

  const getThumbnailUrl = () => {
    if (thumbnailError) return '/placeholder-video.jpg';
    return video.thumbnail_url || '/placeholder-video.jpg';
  };

  if (viewMode === 'list') {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-all"
      >
        <Link href={`/videos/${video.video_id}`}>
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0 w-40 h-24 bg-gray-200 rounded-lg relative">
              <Image
                src={getThumbnailUrl()}
                alt={video.title}
                fill
                className="object-cover rounded-lg"
                onError={() => setThumbnailError(true)}
              />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-gray-900 truncate mb-1">{video.title}</h3>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <Eye className="w-3 h-3" /> {formatNumber(video.views)}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {formatDuration(video.duration)}
                </span>
              </div>
            </div>
          </div>
        </Link>
      </motion.div>
    );
  }

  // Grid view
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all"
    >
      <Link href={`/videos/${video.video_id}`}>
        <div className="relative aspect-video bg-gray-100">
          <Image
            src={getThumbnailUrl()}
            alt={video.title}
            fill
            className="object-cover"
            onError={() => setThumbnailError(true)}
          />
          <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all flex items-center justify-center group">
            <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <Play className="w-6 h-6 text-white ml-1" />
            </div>
          </div>
          <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
            {formatDuration(video.duration)}
          </div>
        </div>
      </Link>

      <div className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-2">{video.title}</h3>
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <div className="flex items-center space-x-3">
            <div className="flex items-center">
              <Eye className="w-3 h-3 mr-1" />
              {formatNumber(video.views)}
            </div>
          </div>
          <div className="flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            {formatRelativeTime(video.published_at)}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
```

---

### TranscriptSegments Component - Complex Filtering

```typescript
// /components/TranscriptSegments.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Clock, DollarSign } from 'lucide-react';

interface Segment {
  segment_id: number;
  segment_number: number;
  start_time: number;
  end_time: number;
  text: string;
  segment_type: string;
  importance_level: string;
  is_promotional: boolean;
}

interface TranscriptSegmentsProps {
  videoId: string;
}

export default function TranscriptSegments({ videoId }: TranscriptSegmentsProps) {
  const [segments, setSegments] = useState<Segment[]>([]);
  const [loading, setLoading] = useState(true);
  const [excludePromotional, setExcludePromotional] = useState(true);
  const [selectedImportance, setSelectedImportance] = useState<string[]>(['critical', 'high', 'medium']);

  useEffect(() => {
    fetchSegments();
  }, [videoId, excludePromotional, selectedImportance]);

  const fetchSegments = async () => {
    try {
      const params = new URLSearchParams();
      params.append('exclude_promotional', excludePromotional.toString());
      selectedImportance.forEach(level => params.append('importance_levels', level));

      const response = await fetch(
        `http://localhost:8001/api/segments/video/${videoId}?${params.toString()}`
      );
      const data = await response.json();
      setSegments(data.segments);
    } catch (err) {
      console.error('Failed to load segments', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="exclude-promotional"
              checked={excludePromotional}
              onCheckedChange={(checked) => setExcludePromotional(checked as boolean)}
            />
            <Label htmlFor="exclude-promotional">Hide promotional content</Label>
          </div>

          <div>
            <Label className="text-sm font-medium mb-2 block">Importance Level</Label>
            <div className="flex flex-wrap gap-2">
              {['critical', 'high', 'medium', 'low'].map(level => (
                <Badge
                  key={level}
                  variant={selectedImportance.includes(level) ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => {
                    setSelectedImportance(prev =>
                      prev.includes(level)
                        ? prev.filter(l => l !== level)
                        : [...prev, level]
                    );
                  }}
                >
                  {level}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Segments List */}
      <Card>
        <CardHeader>
          <CardTitle>Transcript Segments ({segments.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {segments.map((segment) => (
              <div key={segment.segment_id} className="border rounded-lg p-4 space-y-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="default">{segment.importance_level}</Badge>
                    <Badge variant="outline">{segment.segment_type}</Badge>
                    {segment.is_promotional && (
                      <Badge variant="destructive">
                        <DollarSign className="w-3 h-3 mr-1" />
                        Promotional
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
                  </div>
                </div>
                <p className="text-sm">{segment.text}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 4. ANIMATION PATTERNS

### Framer Motion Animations

```typescript
// Simple fade-in and slide
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>

// Hover effect
<motion.div
  whileHover={{ y: -4, boxShadow: '0 10px 20px rgba(0,0,0,0.1)' }}
  transition={{ type: 'spring', stiffness: 300 }}
>
  Hover me
</motion.div>

// Staggered children
<motion.div initial="hidden" animate="visible" variants={{
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}}>
  {items.map((item) => (
    <motion.div key={item.id} variants={{
      hidden: { opacity: 0, x: -20 },
      visible: { opacity: 1, x: 0 }
    }}>
      {item.name}
    </motion.div>
  ))}
</motion.div>

// Continuous animation
<motion.div
  animate={{
    scale: [1, 1.05, 1],
    opacity: [0.3, 0.5, 0.3],
  }}
  transition={{
    duration: 2,
    repeat: Infinity,
    ease: "easeInOut"
  }}
>
  Pulsing element
</motion.div>
```

---

## 5. FORM PATTERNS

### React Hook Form with Zod Validation

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';

const formSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
});

type FormData = z.infer<typeof formSchema>;

export function LoginForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: '',
      name: '',
    },
  });

  const onSubmit = async (data: FormData) => {
    console.log(data);
    // API call here
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="john@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit">Login</Button>
      </form>
    </Form>
  );
}
```

---

## 6. TYPESCRIPT INTERFACES

### Common Data Models

```typescript
// /lib/types.ts
export interface Channel {
  id: string;
  channel_id: string;
  name: string;
  subscriber_count: number;
  video_count: number;
  total_views: number;
  thumbnail_url: string;
  created_at: string;
}

export interface Video {
  id: string;
  video_id: string;
  title: string;
  description: string;
  duration: number;
  views: number;
  likes: number;
  thumbnail_url: string;
  published_at: string;
  transcript_available: boolean;
  channel_id?: string;
  short_summary?: string;
}

export interface Transcript {
  transcript_id?: number;
  video_id: string;
  full_text?: string;
  summary?: string;
  key_points?: string[];
  word_count?: number;
}

export interface SearchResult {
  video_id: string;
  channel_name: string;
  video_title: string;
  matched_text: string;
  timestamp: number;
}
```

---

## 7. TAILWIND CSS PATTERNS

### Common Classes

```css
/* Spacing */
.p-4 = padding: 1rem
.px-4 = padding-left & padding-right: 1rem
.py-2 = padding-top & padding-bottom: 0.5rem
.m-4 = margin: 1rem
.gap-4 = gap: 1rem

/* Flexbox */
.flex .items-center .justify-between
.flex .flex-col .space-y-4 /* vertical spacing between children */
.flex .flex-wrap .gap-2

/* Grid */
.grid .grid-cols-1 .md:grid-cols-3 .gap-4
.grid .grid-cols-3 .gap-6

/* Text */
.text-sm .font-semibold
.text-gray-500 .text-center
.line-clamp-2 /* ellipsis after 2 lines */
.truncate /* single line ellipsis */

/* Colors */
.bg-white .border .border-gray-200
.bg-blue-500 .text-white
.hover:bg-gray-100 .transition-colors

/* Sizing */
.w-full .h-auto
.max-w-lg
.min-w-0 /* allows flex items to shrink below content size */

/* Positioning */
.fixed .inset-0 .z-50
.absolute .bottom-2 .right-2
.relative

/* Shadows & Rounded */
.rounded-lg .shadow-sm
.rounded-full
.border-0 /* remove border */

/* Responsive */
.hidden .md:block /* hidden on mobile, visible on md+ */
.w-full .md:w-1/2 .lg:w-1/3
```

---

## 8. API CLIENT PATTERN

```typescript
// /lib/api-optimized.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Add request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiClient = {
  // Videos
  getVideos: (params?: any) => axiosInstance.get('/api/videos', { params }),
  getVideo: (id: string) => axiosInstance.get(`/api/videos/${id}`),
  
  // Channels
  getChannels: () => axiosInstance.get('/api/channels'),
  getChannel: (id: string) => axiosInstance.get(`/api/channels/${id}`),
  
  // Search
  search: (query: string) => axiosInstance.get('/api/search', { params: { q: query } }),
  
  // Error handling
  handleError: (error: any) => {
    console.error('API Error:', error);
    return error.response?.data?.message || 'An error occurred';
  }
};
```

---

## 9. CUSTOM HOOKS

```typescript
// /hooks/use-toast.tsx
import { useCallback } from 'react';
import { toast as sonnerToast } from 'sonner';

export function useToast() {
  return {
    toast: useCallback((props: {
      title?: string;
      description?: string;
      variant?: 'default' | 'destructive';
    }) => {
      sonnerToast[props.variant === 'destructive' ? 'error' : 'success'](
        props.description || props.title
      );
    }, [])
  };
}

// Usage:
const { toast } = useToast();
toast({ title: 'Success', description: 'Item saved!' });
toast({ title: 'Error', description: 'Failed to save', variant: 'destructive' });
```

---

## KEY TAKEAWAYS

1. Use **CVA** for component variants - much cleaner than conditional classes
2. Use **Composite Components** (Card, Dialog) - breaks down complexity
3. Use **Framer Motion** for animations - smooth and performant
4. Use **TypeScript Interfaces** for type safety
5. Use **Tailwind CSS** for all styling - no CSS files needed
6. Use **React Hook Form + Zod** for forms - great DX
7. Use **Lucide React** icons - 446+ options, highly consistent
8. Use **Next.js Image** - automatic optimization

