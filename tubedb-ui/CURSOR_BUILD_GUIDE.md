# 🚀 TubeDB UI - Cursor.ai Build Guide

## 📍 YOU ARE HERE
`/Users/yourox/AI-Workspace/tubedb-ui/`

This is your **complete reference package** for building TubeDB UI in Cursor.ai.

---

## 🎯 QUICK START FOR CURSOR.AI

### **Step 1: Read These Docs (In Order)**

1. **START HERE** → `docs/UI_README.md` (5 min)
   - Overview of the entire project
   - What you're building and why
   
2. **DESIGN MOCKUPS** → `docs/UI_VISUAL_MOCKUPS.md` (15 min)
   - See every screen laid out visually
   - Understand the UX flow
   - Reference during development

3. **TECHNICAL SPECS** → `docs/UI_IMPLEMENTATION_PLAN.md` (20 min)
   - Component structure
   - Data flow
   - Technical decisions
   - Phase-by-phase breakdown

4. **DESIGN SYSTEM** → `docs/UI_DESIGN_COMPARISON.md` (10 min)
   - Color palette
   - Component patterns from YouTube Vault
   - What to copy, what to adapt

---

## 📋 CHECKLIST FOR CURSOR.AI

Copy this into your first Cursor chat:

```markdown
I'm building TubeDB UI based on these specs:

PROJECT CONTEXT:
- Internal QA dashboard for transcript quality assurance
- 5 videos, 4,117 segments already processed
- Data location: /Users/yourox/AI-Workspace/data/transcripts/batch_20251015_193743.json
- Design inspiration: YouTube Vault (dark theme, glassmorphism)
- Tech stack: Next.js 14, Tailwind, shadcn/ui, TypeScript, Framer Motion

REFERENCE DOCS:
- Full specs: /Users/yourox/AI-Workspace/tubedb-ui/docs/UI_IMPLEMENTATION_PLAN.md
- Visual mockups: /Users/yourox/AI-Workspace/tubedb-ui/docs/UI_VISUAL_MOCKUPS.md
- Design system: /Users/yourox/AI-Workspace/tubedb-ui/docs/UI_DESIGN_COMPARISON.md

WHAT TO BUILD:
Phase 1: Project setup + Overview tab
Phase 2: QC tab + Video modal
Phase 3: Analytics tab
Phase 4: Raw data tab
Phase 5: Polish

Please help me build this step by step.
```

---

## 🏗️ PROJECT STRUCTURE TO CREATE

```
tubedb-ui/
├── app/
│   ├── layout.tsx           # Root layout with header
│   ├── page.tsx             # Main dashboard (4 tabs)
│   ├── globals.css          # Tailwind imports
│   └── api/                 # Optional: API routes for data
│       └── batch/
│           └── route.ts     # GET /api/batch - return JSON data
│
├── components/
│   ├── ui/                  # shadcn/ui components (auto-generated)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   └── tabs.tsx
│   │
│   ├── dashboard/           # Main dashboard components
│   │   ├── overview-tab.tsx
│   │   ├── qc-tab.tsx
│   │   ├── analytics-tab.tsx
│   │   └── raw-data-tab.tsx
│   │
│   ├── video/               # Video-specific components
│   │   ├── video-card.tsx
│   │   ├── video-modal.tsx
│   │   ├── transcript-viewer.tsx
│   │   └── quality-badge.tsx
│   │
│   ├── common/              # Reusable components
│   │   ├── stat-card.tsx
│   │   ├── batch-selector.tsx
│   │   ├── header.tsx
│   │   └── search-bar.tsx
│   │
│   └── layout/
│       └── main-layout.tsx  # Wrapper for all pages
│
├── lib/
│   ├── api.ts               # Data fetching functions
│   ├── types.ts             # TypeScript interfaces
│   ├── utils.ts             # Helper functions
│   └── constants.ts         # Colors, gradients, etc.
│
├── public/
│   └── (static assets)
│
├── docs/                    # ✅ Already here!
│   ├── UI_README.md
│   ├── UI_EXECUTIVE_SUMMARY.md
│   ├── UI_IMPLEMENTATION_PLAN.md
│   ├── UI_DESIGN_COMPARISON.md
│   └── UI_VISUAL_MOCKUPS.md
│
├── .cursorrules            # → Create this (see below)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md               # Project-specific readme
```

---

## 📝 CRITICAL FILES FOR CURSOR

### **1. Create `.cursorrules`**

Put this in `/Users/yourox/AI-Workspace/tubedb-ui/.cursorrules`:

```
# TubeDB UI Development Rules

## Project Context
This is an internal Quality Assurance dashboard for video transcript analysis.
- Framework: Next.js 14 (App Router)
- Styling: Tailwind CSS + shadcn/ui
- Animation: Framer Motion
- Language: TypeScript (strict mode)

## Design System
- Dark theme: bg-slate-900, surface-slate-800
- Primary gradient: from-blue-600 to-cyan-500
- Glass effect: backdrop-blur-md with alpha transparency
- Icons: Lucide React only
- Fonts: System fonts (no custom fonts)

## Data Source
Read from: /Users/yourox/AI-Workspace/data/transcripts/batch_20251015_193743.json
Structure: Array of video objects with transcript segments and QC verification

## Component Patterns
- Use server components by default
- Client components only when needed (use 'use client')
- All components are functional (no classes)
- Props are TypeScript interfaces
- Use composition over props drilling

## File Organization
- One component per file
- Co-locate types with components
- Group by feature, not type
- Max 200 lines per file

## Code Style
- Use const for all declarations
- Destructure props
- Early returns for guards
- Meaningful variable names
- Comments only when necessary

## Reference Documentation
- Specs: /Users/yourox/AI-Workspace/tubedb-ui/docs/UI_IMPLEMENTATION_PLAN.md
- Mockups: /Users/yourox/AI-Workspace/tubedb-ui/docs/UI_VISUAL_MOCKUPS.md
- Design: /Users/yourox/AI-Workspace/tubedb-ui/docs/UI_DESIGN_COMPARISON.md

## Do NOT
- Add authentication
- Create backend APIs (read files directly for now)
- Use external CSS files (Tailwind only)
- Install extra animation libraries (Framer Motion only)
- Overcomplicate - keep it simple
```

---

## 🎨 COLOR PALETTE (Copy This)

Save in `lib/constants.ts`:

```typescript
export const COLORS = {
  background: {
    primary: '#0f172a',    // slate-900
    secondary: '#1e293b',  // slate-800
    surface: '#334155',    // slate-700
  },
  border: {
    default: '#475569',    // slate-600
    hover: '#64748b',      // slate-500
  },
  gradient: {
    primary: 'from-blue-600 to-cyan-500',
    purple: 'from-purple-500 to-pink-500',
    green: 'from-green-500 to-emerald-500',
    orange: 'from-orange-500 to-red-500',
  },
  quality: {
    excellent: '#10b981',  // green-500 (0.9-1.0)
    good: '#f59e0b',       // yellow-500 (0.75-0.89)
    fair: '#f97316',       // orange-500 (0.50-0.74)
    poor: '#ef4444',       // red-500 (0.0-0.49)
  },
  text: {
    primary: '#ffffff',
    secondary: '#cbd5e1',  // slate-300
    tertiary: '#94a3b8',   // slate-400
  }
};

export const GRADIENTS = {
  statCard: {
    videos: 'from-blue-500 to-cyan-500',
    segments: 'from-purple-500 to-pink-500',
    quality: 'from-green-500 to-emerald-500',
    time: 'from-orange-500 to-red-500',
  }
};
```

---

## 🔧 TYPESCRIPT INTERFACES (Copy This)

Save in `lib/types.ts`:

```typescript
export interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
}

export interface Transcript {
  language: string;
  segments: TranscriptSegment[];
  segment_count: number;
}

export interface QCVerification {
  quality_score: number;
  key_topics: string[];
  summary: string;
  verifier?: string;
}

export interface Video {
  video_id: string;
  title: string;
  agent_id: number;
  method: string;
  transcript: Transcript;
  qc_verification?: QCVerification;
}

export interface BatchData {
  filename: string;
  videos: Video[];
  video_count: number;
  timestamp: string;
}

export interface SystemStats {
  totalVideos: number;
  totalSegments: number;
  avgQualityScore: number;
  processingTime: number;
}
```

---

## 📦 DEPENDENCIES TO INSTALL

Copy this `package.json` content:

```json
{
  "name": "tubedb-ui",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "framer-motion": "^10.0.0",
    "lucide-react": "^0.300.0",
    "recharts": "^2.10.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "@radix-ui/react-dialog": "^1.0.0",
    "@radix-ui/react-tabs": "^1.0.0",
    "@radix-ui/react-select": "^2.0.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0"
  }
}
```

---

## 🚀 BUILD PHASES FOR CURSOR

### **Phase 1: Setup (30 min)**
Tell Cursor:
```
Create Next.js 14 project with TypeScript and Tailwind.
Setup shadcn/ui with dark theme.
Create folder structure from CURSOR_BUILD_GUIDE.md.
Install all dependencies from package.json.
```

### **Phase 2: Layout & Header (1 hour)**
Tell Cursor:
```
Build main layout with:
- Dark slate-900 background
- Header with logo and search
- Tab navigation (Overview, QC, Analytics, Raw Data)
- Reference: docs/UI_VISUAL_MOCKUPS.md - Main Dashboard View
```

### **Phase 3: Data Layer (1 hour)**
Tell Cursor:
```
Create lib/api.ts to read JSON from:
/Users/yourox/AI-Workspace/data/transcripts/batch_20251015_193743.json

Functions needed:
- loadBatchData()
- getBatchStats()
- getVideoById()
- searchTranscripts()

Use types from lib/types.ts
```

### **Phase 4: Overview Tab (2 hours)**
Tell Cursor:
```
Build Overview tab with:
- 4 stat cards (videos, segments, quality, time)
- Batch selector
- Video grid with cards
- Reference: docs/UI_VISUAL_MOCKUPS.md - Main Dashboard View
- Use components: StatCard, VideoCard
```

### **Phase 5: Video Modal (2 hours)**
Tell Cursor:
```
Build VideoModal with 3 tabs:
- Overview: QC score, topics, summary
- Transcript: Searchable, timestamped
- QC: Verification details
Reference: docs/UI_VISUAL_MOCKUPS.md - Video Detail Modal
```

### **Phase 6: QC Tab (2 hours)**
Tell Cursor:
```
Build QC tab with:
- Filter by quality score
- Sort options
- Detailed video list with QC badges
- Reference: docs/UI_VISUAL_MOCKUPS.md - Quality Control Tab
```

### **Phase 7: Analytics Tab (2 hours)**
Tell Cursor:
```
Build Analytics tab with:
- Topic distribution chart (Recharts)
- Quality trends graph
- Performance metrics
- Word cloud visualization
Reference: docs/UI_VISUAL_MOCKUPS.md - Analytics Tab
```

### **Phase 8: Raw Data Tab (1 hour)**
Tell Cursor:
```
Build Raw Data tab with:
- JSON viewer
- Batch selector
- Copy/download functionality
Reference: docs/UI_VISUAL_MOCKUPS.md - Raw Data Tab
```

### **Phase 9: Polish (2 hours)**
Tell Cursor:
```
Add:
- Framer Motion animations
- Loading states
- Error handling
- Responsive design tweaks
- Glass effects on cards
```

---

## 💡 CURSOR.AI PROMPTING TIPS

### **Good Prompts:**
```
"Create a StatCard component that matches the design in UI_VISUAL_MOCKUPS.md.
It should have a gradient background, icon, label, and value."

"Build the transcript viewer with virtual scrolling for 1,186 segments.
Each segment should show [MM:SS] timestamp and text.
Highlight search terms when user searches."

"Add glassmorphism effect to all cards:
backdrop-blur-md, bg-opacity-50, border-slate-700/50"
```

### **Avoid Vague Prompts:**
```
❌ "Make it look nice"
❌ "Add some animations"
❌ "Fix the styling"

✅ "Add Framer Motion fade-in animation with 0.3s duration"
✅ "Apply the blue-to-cyan gradient from constants.ts"
✅ "Use the glass effect pattern from the design system"
```

---

## 📚 QUICK REFERENCE CHEAT SHEET

### **File Structure**
```
Video Card → components/video/video-card.tsx
Modal → components/video/video-modal.tsx
Tab → components/dashboard/overview-tab.tsx
API → lib/api.ts
Types → lib/types.ts
Colors → lib/constants.ts
```

### **Component Imports**
```typescript
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import { Play, Star, Clock } from 'lucide-react'
```

### **Common Patterns**
```typescript
// Glass card
<div className="glass rounded-xl p-6 border border-slate-700/50">

// Gradient button
<Button className="bg-gradient-to-r from-blue-600 to-cyan-500">

// Quality badge
<span className={`px-2 py-1 rounded text-xs ${
  score >= 0.9 ? 'bg-green-500/20 text-green-400' :
  score >= 0.75 ? 'bg-yellow-500/20 text-yellow-400' :
  'bg-orange-500/20 text-orange-400'
}`}>
```

---

## ✅ FINAL CHECKLIST

Before you start in Cursor.ai:

- [ ] ✅ Read UI_README.md
- [ ] ✅ Read UI_VISUAL_MOCKUPS.md (see what you're building)
- [ ] ✅ Read UI_IMPLEMENTATION_PLAN.md (understand architecture)
- [ ] ✅ Create .cursorrules file
- [ ] ✅ Copy types.ts and constants.ts templates
- [ ] ✅ Reference docs are in tubedb-ui/docs/
- [ ] ✅ Data file confirmed at: /Users/yourox/AI-Workspace/data/transcripts/batch_20251015_193743.json

---

## 🎯 SUCCESS METRICS

You'll know it's working when:
- ✅ Can see all 5 videos in grid view
- ✅ QC scores display correctly (0.85, 0.75, etc.)
- ✅ Can click video to see transcript
- ✅ Search works in transcript
- ✅ Topics are displayed and filterable
- ✅ Dark theme looks polished
- ✅ Animations are smooth

---

## 🆘 IF YOU GET STUCK

1. **Check the mockups**: `docs/UI_VISUAL_MOCKUPS.md`
2. **Review component structure**: `docs/UI_IMPLEMENTATION_PLAN.md`
3. **Verify data format**: Look at batch_20251015_193743.json
4. **Check design system**: `docs/UI_DESIGN_COMPARISON.md`

---

## 🚀 START BUILDING!

Open Cursor.ai in this folder:
```bash
cd /Users/yourox/AI-Workspace/tubedb-ui
cursor .
```

Then paste the "CHECKLIST FOR CURSOR.AI" from above into your first chat.

**You've got everything you need!** 🎨

The docs are comprehensive, the structure is clear, and the examples are detailed.

**Let's build something amazing!** 🚀