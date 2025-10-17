# 📊 TubeDB UI - Quality Assurance Dashboard
## Implementation Plan

---

## 🎯 **PROJECT GOALS**

Based on AI-Workspace objectives and YouTube Vault best practices:

### **Primary Purpose**
Build a **Quality Assurance & Data Inspection UI** for the TubeDB system to:
1. ✅ **Verify Transcript Quality** - Check AI-verified segments for accuracy
2. 📊 **Inspect QC Reports** - Review quality scores, topics, and summaries
3. 🔍 **Search & Filter** - Find specific videos, topics, or segments quickly
4. 📈 **Track Processing** - Monitor batch jobs and identify issues
5. 🎬 **Compare Videos** - Side-by-side analysis of similar content

### **Core Difference from YouTube Vault**
- **Not a public product** (no pricing, auth, marketing pages)
- **Internal tool** for data quality checks and insights
- **Read-only interface** (no video processing controls)
- **Focused on inspection** rather than content creation

---

## 🎨 **DESIGN SYSTEM** (From YouTube Vault)

### **Visual Style**
- **Dark Theme**: Slate-900 background with blue-900 accents
- **Glassmorphism**: Subtle glass effects with backdrop-blur
- **Gradients**: Blue-to-cyan for primary actions
- **Motion**: Framer Motion for smooth transitions
- **Icons**: Lucide React icon set

### **Color Palette**
```css
Background: #0f172a (slate-900)
Surface: #1e293b (slate-800)
Border: #334155 (slate-700)
Primary: #3b82f6 → #06b6d4 (blue-cyan gradient)
Success: #10b981 (green-500)
Warning: #f59e0b (yellow-500)
Error: #ef4444 (red-500)
```

### **Components** (shadcn/ui + Custom)
```typescript
// From YouTube Vault
- Card with glass effect
- Stat cards with gradients
- Progress bars with animated fills
- Tab navigation
- Search with filters
- Modal/drawer for details

// New for TubeDB
- Transcript viewer with timestamps
- QC score badges
- Batch status indicators
- Segment explorer
- Topic tag cloud
```

---

## 📐 **UI STRUCTURE**### **Page Layout**

```
┌─────────────────────────────────────────────────┐
│  Header: Logo | Navigation | Search              │
├─────────────────────────────────────────────────┤
│                                                   │
│  Main Content Area (Tab-Based)                   │
│                                                   │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐               │
│  │ All │ │ QC  │ │Stats│ │ Raw │               │
│  └─────┘ └─────┘ └─────┘ └─────┘               │
│                                                   │
│  [Dynamic Content Based on Active Tab]           │
│                                                   │
└─────────────────────────────────────────────────┘
```

### **Tab Structure**

#### **1. Overview Tab** (Default View)
```
┌──────────────────────────────────────┐
│ 📊 System Stats                      │
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│ │ 5   │ │4,117│ │ 85% │ │36s  │   │
│ │Vids │ │Segs │ │ QC  │ │Time │   │
│ └─────┘ └─────┘ └─────┘ └─────┘   │
│                                      │
│ 📋 Recent Batches                   │
│ • batch_20251015_193743 (5 videos) │
│   Status: ✅ Complete | QC: 85%    │
│                                      │
│ 🎬 Video List (Grid or Table)      │
│ [Video cards with QC badges]        │
└──────────────────────────────────────┘
```

#### **2. Quality Control Tab**
```
┌──────────────────────────────────────┐
│ 🔍 QC Verification Dashboard        │
│                                      │
│ Filters:                             │
│ [Score: All ▼] [Topics ▼] [Date ▼]│
│                                      │
│ Video List with QC Details:          │
│ ┌────────────────────────────────┐ │
│ │ 1. Dan Koe AI Workflow         │ │
│ │    Score: 0.85/1.0 ⭐          │ │
│ │    Topics: AI, Content, LLMs   │ │
│ │    [View Details]              │ │
│ └────────────────────────────────┘ │
│                                      │
│ ┌────────────────────────────────┐ │
│ │ 2. 300M Views Video            │ │
│ │    Score: 0.75/1.0             │ │
│ │    Topics: Video, AI, Sora     │ │
│ │    [View Details]              │ │
│ └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

#### **3. Analytics Tab**
```
┌──────────────────────────────────────┐
│ 📈 Data Analytics                   │
│                                      │
│ ┌────────────┐ ┌────────────────┐  │
│ │ Topic Dist │ │ Quality Trends │  │
│ │ [Chart]    │ │ [Line Graph]   │  │
│ └────────────┘ └────────────────┘  │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Processing Performance          │  │
│ │ • Avg Time: 7.35s per video    │  │
│ │ • Success Rate: 100%            │  │
│ │ • Total Segments: 4,117         │  │
│ └────────────────────────────────┘  │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Word Cloud: Most Common Topics │  │
│ │ [Interactive Word Cloud]        │  │
│ └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

#### **4. Raw Data Tab**
```
┌──────────────────────────────────────┐
│ 💾 Raw JSON Inspector               │
│                                      │
│ Select Batch:                        │
│ [batch_20251015_193743 ▼]          │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ {                               │  │
│ │   "video_id": "HhspudqFSvU",  │  │
│ │   "title": "Dan Koe...",       │  │
│ │   "transcript": {              │  │
│ │     "segments": [...]          │  │
│ │   },                           │  │
│ │   "qc_verification": {...}     │  │
│ │ }                              │  │
│ └────────────────────────────────┘  │
│                                      │
│ [Copy JSON] [Download] [Format]     │
└──────────────────────────────────────┘
```

---

## 🎬 **VIDEO DETAIL VIEW** (Modal/Drawer)

When clicking on a video card:

```
┌────────────────────────────────────────────┐
│ ✕ Close                                    │
│                                             │
│ 🎬 I Watched Dan Koe Break Down His...    │
│ Video ID: HhspudqFSvU                      │
│ Duration: ~50 minutes | 1,186 segments     │
│                                             │
│ ┌──────────┬──────────┬──────────┐        │
│ │Overview  │Transcript│  QC      │        │
│ └──────────┴──────────┴──────────┘        │
│                                             │
│ [OVERVIEW TAB ACTIVE]                      │
│                                             │
│ 📊 Quality Score: 0.85/1.0 ⭐              │
│ Progress: ▓▓▓▓▓▓▓▓░░ 85%                  │
│                                             │
│ 🎯 Key Topics:                             │
│ [AI] [LLMs] [Content Creation]            │
│ [Prompts] [Social Media]                   │
│                                             │
│ 📝 AI Summary:                             │
│ Dan Koe shares his playbook for using     │
│ AI and LLMs to create viral content...    │
│                                             │
│ [TRANSCRIPT TAB]                           │
│ ┌─────────────────────────────────────┐   │
│ │ [00:00] If you've been on the...   │   │
│ │ [00:01] seen Danco. He's got...    │   │
│ │ [00:03] followers and I've seen... │   │
│ │                                     │   │
│ │ [Search in transcript...]          │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ [QC TAB]                                   │
│ QC Verification Details:                   │
│ • Method: Claude Sonnet 4.5               │
│ • Processing Time: 8.2 seconds            │
│ • Confidence: High                         │
│ • Issues: None detected                    │
└────────────────────────────────────────────┘
```

---

## 🔧 **TECHNICAL STACK**

### **Frontend**
```json
{
  "framework": "Next.js 14 (App Router)",
  "styling": "Tailwind CSS + shadcn/ui",
  "animations": "Framer Motion",
  "icons": "Lucide React",
  "charts": "Recharts",
  "state": "React useState + Context",
  "data-fetching": "Native fetch with SWR"
}
```

### **Backend API** (Keep existing Python)```python
# FastAPI microservice (optional)
# OR use filesystem-based API (read JSON files directly)

from fastapi import FastAPI
from pathlib import Path
import json

app = FastAPI()

@app.get("/api/batches")
def list_batches():
    """List all transcript batches"""
    batches_dir = Path("/Users/yourox/AI-Workspace/data/transcripts")
    batches = []
    for batch_file in batches_dir.glob("batch_*.json"):
        with open(batch_file) as f:
            data = json.load(f)
            batches.append({
                "filename": batch_file.name,
                "video_count": len(data),
                "timestamp": batch_file.stem.split("_")[1]
            })
    return batches

@app.get("/api/batch/{batch_id}")
def get_batch(batch_id: str):
    """Get full batch data"""
    batch_path = Path(f"/Users/yourox/AI-Workspace/data/transcripts/batch_{batch_id}.json")
    with open(batch_path) as f:
        return json.load(f)

@app.get("/api/video/{video_id}")
def get_video(video_id: str):
    """Get single video from all batches"""
    # Search all batches for video_id
    pass

@app.get("/api/stats")
def get_stats():
    """Get aggregate statistics"""
    # Calculate from all batch files
    pass
```

### **File Structure**
```
AI-Workspace/
├── tubedb-ui/                    # New UI project
│   ├── app/
│   │   ├── page.tsx             # Main dashboard
│   │   ├── layout.tsx           # Root layout
│   │   └── api/                 # API routes (if using Next.js API)
│   ├── components/
│   │   ├── ui/                  # shadcn components
│   │   ├── dashboard/
│   │   │   ├── overview.tsx
│   │   │   ├── qc-tab.tsx
│   │   │   ├── analytics.tsx
│   │   │   └── raw-data.tsx
│   │   ├── video/
│   │   │   ├── video-card.tsx
│   │   │   ├── video-modal.tsx
│   │   │   └── transcript-viewer.tsx
│   │   └── common/
│   │       ├── stat-card.tsx
│   │       ├── batch-selector.tsx
│   │       └── quality-badge.tsx
│   ├── lib/
│   │   ├── api.ts               # Data fetching
│   │   ├── types.ts             # TypeScript types
│   │   └── utils.ts             # Helper functions
│   ├── public/
│   └── package.json
├── data/                         # Existing data (unchanged)
│   └── transcripts/
│       └── batch_*.json
└── scripts/                      # Existing scripts (unchanged)
```

---

## 📋 **IMPLEMENTATION PHASES**

### **Phase 1: Foundation** (Day 1-2)
```bash
# Setup
✅ Create Next.js project
✅ Install dependencies
✅ Setup Tailwind + shadcn/ui
✅ Configure paths and types

# Core Structure
✅ Build main layout
✅ Create tab navigation
✅ Setup data fetching utilities
✅ Define TypeScript interfaces
```

### **Phase 2: Overview Tab** (Day 2-3)
```bash
✅ System stats cards
✅ Batch selector component
✅ Video grid/list view
✅ Video card component
✅ Basic filtering
```

### **Phase 3: Video Detail View** (Day 3-4)
```bash
✅ Modal/drawer component
✅ Overview section
✅ Transcript viewer with timestamps
✅ QC details display
✅ Topic tags
```

### **Phase 4: QC Tab** (Day 4-5)
```bash
✅ Quality score filters
✅ Topic-based filtering
✅ Sortable video list
✅ QC badge system
✅ Detail inspection
```

### **Phase 5: Analytics** (Day 5-6)
```bash
✅ Topic distribution chart
✅ Quality trends graph
✅ Performance metrics
✅ Word cloud visualization
✅ Export functionality
```

### **Phase 6: Raw Data Tab** (Day 6)
```bash
✅ JSON viewer component
✅ Batch selector
✅ Pretty-print formatting
✅ Copy/download functionality
✅ Search within JSON
```

### **Phase 7: Polish & Deploy** (Day 7)
```bash
✅ Responsive design
✅ Loading states
✅ Error handling
✅ Performance optimization
✅ Documentation
```

---

## 🎨 **KEY UI COMPONENTS TO BUILD**

### **1. StatCard Component**
```tsx
interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  gradient: string;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
}

// Usage
<StatCard
  label="Total Videos"
  value={5}
  icon={<Play />}
  gradient="from-blue-500 to-cyan-500"
/>
```

### **2. QualityBadge Component**
```tsx
interface QualityBadgeProps {
  score: number;
  showLabel?: boolean;
}

// Auto-colors based on score
// 0.9-1.0 = green
// 0.75-0.89 = yellow
// < 0.75 = orange
```

### **3. TranscriptViewer Component**
```tsx
interface TranscriptViewerProps {
  segments: TranscriptSegment[];
  searchQuery?: string;
  onSegmentClick?: (timestamp: number) => void;
}

// Features:
// - Highlight search terms
// - Click timestamp to jump
// - Virtualized list for performance
```

### **4. VideoCard Component**
```tsx
interface VideoCardProps {
  video: Video;
  onSelect: (id: string) => void;
  view: 'grid' | 'list';
}

// Shows:
// - Title
// - Duration
// - Segment count
// - QC score badge
// - Key topics (max 3)
```

### **5. BatchSelector Component**
```tsx
interface BatchSelectorProps {
  batches: Batch[];
  selected: string | null;
  onSelect: (batchId: string) => void;
}

// Dropdown with:
// - Batch timestamp
// - Video count
// - Average QC score
```

---

## 📊 **DATA FLOW**

### **File-Based Approach** (Simpler, no server needed)
```
┌─────────────┐
│   Next.js   │
│   Frontend  │
└─────┬───────┘
      │
      │ Read directly
      ↓
┌─────────────────────┐
│ /data/transcripts/  │
│ • batch_*.json      │
│ • *_full.json       │
└─────────────────────┘
```

### **API Approach** (More flexible)
```
┌─────────────┐      ┌──────────────┐
│   Next.js   │ HTTP │   FastAPI    │
│   Frontend  │─────→│   Backend    │
└─────────────┘      └──────┬───────┘
                            │
                            ↓
                    ┌─────────────────┐
                    │ JSON Files      │
                    │ + Processing    │
                    └─────────────────┘
```

---

## 🎯 **QUALITY ASSURANCE FEATURES**

### **QC Score Visualization**
- **Color-coded badges**: Green (≥0.9), Yellow (0.75-0.89), Orange (<0.75)
- **Progress bars**: Visual quality indicator
- **Trend analysis**: Quality over time

### **Topic Verification**
- **Tag cloud**: Most common topics across videos
- **Filter by topic**: Find all videos about "AI", "LLMs", etc.
- **Topic co-occurrence**: Which topics appear together

### **Segment Analysis**
- **Segment count**: How many segments per video
- **Timestamp accuracy**: Verify timing is correct
- **Text quality**: Flag potential transcription errors

### **Batch Comparison**
- **Compare batches**: Side-by-side batch statistics
- **Processing time**: Track performance improvements
- **Success rates**: Monitor extraction quality

---

## 🚀 **GETTING STARTED**

### **Quick Setup** (When ready to build)
```bash
# 1. Create Next.js project
cd /Users/yourox/AI-Workspace
npx create-next-app@latest tubedb-ui --typescript --tailwind --app

# 2. Install dependencies
cd tubedb-ui
npm install @radix-ui/react-dialog @radix-ui/react-tabs
npm install lucide-react framer-motion recharts
npm install class-variance-authority clsx tailwind-merge

# 3. Setup shadcn/ui
npx shadcn-ui@latest init

# 4. Add components
npx shadcn-ui@latest add card button input tabs dialog

# 5. Start development
npm run dev
```

### **Environment Setup**
```bash
# .env.local
DATA_DIR=/Users/yourox/AI-Workspace/data/transcripts
API_URL=http://localhost:8000  # If using FastAPI
```

---

## 💡 **DESIGN DECISIONS**

### **Why File-Based vs API?**

**File-Based (Recommended for MVP)**
✅ Simpler - no backend server needed
✅ Faster development
✅ Direct data access
✅ No API layer complexity
❌ Less flexible for complex queries
❌ All data processing in browser

**API-Based (Better for scale)**
✅ Clean separation of concerns
✅ Backend can pre-process data
✅ Easier to add features later
✅ Better for multiple clients
❌ More setup complexity
❌ Need to run backend server

**Recommendation**: Start file-based, migrate to API later if needed.

### **Why Modal vs Separate Page?**

**Modal (Recommended)**
✅ Faster navigation
✅ Context preservation
✅ Better for quick inspection
✅ Matches YouTube Vault pattern

**Separate Page**
✅ Deep linking
✅ Better for detailed analysis
✅ Shareable URLs

**Recommendation**: Use modal for quick QA, add separate page route later.

---

## 🎨 **VISUAL MOCKUPS**

### **Color Scheme Examples**
```css
/* Primary Actions */
.btn-primary {
  background: linear-gradient(to right, #3b82f6, #06b6d4);
}

/* Quality Scores */
.quality-excellent { color: #10b981; } /* 0.9-1.0 */
.quality-good      { color: #f59e0b; } /* 0.75-0.89 */
.quality-fair      { color: #ef4444; } /* <0.75 */

/* Glass Effect */
.glass {
  background: rgba(30, 41, 59, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(148, 163, 184, 0.1);
}
```

### **Stat Card Gradients**
```typescript
const statCardStyles = {
  videos: "from-blue-500 to-cyan-500",
  segments: "from-purple-500 to-pink-500",
  quality: "from-green-500 to-emerald-500",
  time: "from-orange-500 to-red-500"
}
```

---

## 🎬 **READY TO BUILD?**

Once you approve this plan, I'll:

1. ✅ Create the Next.js project structure
2. ✅ Build the core dashboard layout
3. ✅ Implement data fetching from JSON files
4. ✅ Create reusable UI components
5. ✅ Build each tab incrementally
6. ✅ Add polish and animations

**Estimated Timeline**: 5-7 days for full implementation

**MVP Timeline**: 2-3 days for core features (Overview + QC tabs)

---

## 📝 **NEXT STEPS**

1. **Review this plan** - Any changes needed?
2. **Choose approach** - File-based or API?
3. **Set priorities** - Which tabs are most important?
4. **Start building** - I'll create the project structure

Ready to proceed? 🚀