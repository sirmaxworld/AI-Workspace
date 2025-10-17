# 🚀 TubeDB UI - YouTube Vault Design Migration & Build Plan

**Date**: October 15, 2025
**Status**: In Progress
**Server**: http://localhost:4000

---

## ✅ Completed

### Phase 1: Design System Migration
- ✅ Copied 53 UI components from YouTube Vault
- ✅ Updated globals.css with YouTube Vault design system
- ✅ Dark theme CSS variables configured
- ✅ Glass morphism utility classes ready

### Phase 2: Project Setup
- ✅ Next.js 14 with TypeScript
- ✅ Tailwind CSS + all dependencies
- ✅ Folder structure created
- ✅ API route working (GET /api/batch 200)
- ✅ Data loading from JSON file

---

## 🎯 Current Build Plan

### **Phase 3: Rebuild Core Components** (NEXT)

Using YouTube Vault patterns + TubeDB data structure:

#### 1. **Update Header Component**
```tsx
// Use YouTube Vault's header pattern
components/common/header.tsx
- Clean, minimal design
- Search with proper state management
- System status indicator
- Logo with gradient
```

#### 2. **Rebuild Video Card**
```tsx
// Use YouTube Vault's card pattern with CVA
components/video/video-card.tsx
- Card component from ui/card.tsx
- Badge component for quality score
- Hover effects
- Click handler for modal
```

#### 3. **Create Video Modal (Priority!)**
```tsx
// Use Dialog component from YouTube Vault
components/video/video-modal.tsx
- Dialog from ui/dialog.tsx
- Tabs from ui/tabs.tsx
- TranscriptViewer component
- Search functionality
- Virtual scrolling for 1000+ segments
```

---

## 📊 Enhanced Features (TubeDB Specific)

### **New Tab: Research & Papers**

Add a 5th tab for scientific research integration:

```
[Overview] [QC] [Analytics] [Raw Data] [📚 Research]
```

**Features**:
1. **Arxiv Integration**
   - Search papers by topics from transcripts
   - Show related research
   - Link to full papers

2. **Research Notes**
   - Annotate videos with research citations
   - Link transcript segments to papers
   - Export research notes

3. **Topic Analysis**
   - Extract key research topics
   - Find similar academic work
   - Build knowledge graph

**Data Structure**:
```typescript
interface ResearchPaper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  arxiv_id: string;
  pdf_url: string;
  published_date: string;
  topics: string[];
  relevance_score: number;
}

interface VideoResearch {
  video_id: string;
  related_papers: ResearchPaper[];
  annotations: Annotation[];
  knowledge_graph: GraphNode[];
}
```

---

## 🔨 Implementation Steps

### **Step 1: Fix Current Issues** (15 min)
- [ ] Verify all UI components work
- [ ] Test data loading
- [ ] Ensure page renders correctly

### **Step 2: Build Video Modal** (1 hour)
- [ ] Create VideoModal component
- [ ] Add Dialog from ui/dialog.tsx
- [ ] Build TranscriptViewer
- [ ] Add search functionality
- [ ] Test with 1000+ segments

### **Step 3: Enhance Video Cards** (30 min)
- [ ] Update VideoCard with YouTube Vault design
- [ ] Add click handlers
- [ ] Improve hover states
- [ ] Add quality badges

### **Step 4: Build QC Tab** (45 min)
- [ ] Create filtering UI
- [ ] Add sorting options
- [ ] Quality score visualization
- [ ] Detailed video list

### **Step 5: Build Analytics Tab** (1 hour)
- [ ] Topic distribution chart
- [ ] Quality trends
- [ ] Performance metrics
- [ ] Use Recharts

### **Step 6: Build Raw Data Tab** (30 min)
- [ ] JSON viewer
- [ ] Syntax highlighting
- [ ] Copy/download functionality

### **Step 7: Build Research Tab** (2 hours) 🆕
- [ ] Arxiv API integration
- [ ] Paper search UI
- [ ] Relevance scoring
- [ ] Annotation system
- [ ] Knowledge graph visualization

### **Step 8: Polish & Optimize** (1 hour)
- [ ] Add Framer Motion animations
- [ ] Loading states
- [ ] Error handling
- [ ] Responsive design
- [ ] Performance optimization

---

## 🎨 Design Patterns from YouTube Vault

### **Component Composition**
```tsx
// Card Pattern
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    {/* Actions */}
  </CardFooter>
</Card>
```

### **CVA for Variants**
```tsx
// Button variants
const buttonVariants = cva(
  "base classes",
  {
    variants: {
      variant: {
        default: "bg-primary",
        destructive: "bg-destructive",
        outline: "border border-input",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3",
        lg: "h-11 px-8",
      },
    },
  }
)
```

### **Composite Dialogs**
```tsx
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    {/* Content */}
    <DialogFooter>
      {/* Actions */}
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

## 📡 API Integration

### **Current Endpoint**
```
GET /api/batch
Returns: { videos: Video[], stats: SystemStats }
```

### **New Endpoints Needed**

```typescript
// Research integration
GET /api/research/papers?topics=ai,ml
POST /api/research/annotate
GET /api/research/knowledge-graph/:videoId

// Video details
GET /api/video/:id
GET /api/video/:id/transcript
POST /api/video/:id/search

// QC operations
GET /api/qc/summary
POST /api/qc/update/:videoId
```

---

## 🔬 Research Integration Architecture

### **Arxiv API Integration**
```typescript
// lib/research/arxiv.ts
export async function searchPapers(topics: string[]) {
  const query = topics.join(' OR ');
  const response = await fetch(
    `http://export.arxiv.org/api/query?search_query=${query}`
  );
  return parsePapers(response);
}
```

### **Relevance Scoring**
```typescript
// lib/research/scoring.ts
export function calculateRelevance(
  paper: ResearchPaper,
  transcript: Transcript
): number {
  // TF-IDF similarity
  // Topic overlap
  // Citation count
  // Recency weight
  return score;
}
```

### **Knowledge Graph**
```typescript
// lib/research/graph.ts
export function buildKnowledgeGraph(
  videos: Video[],
  papers: ResearchPaper[]
): GraphNode[] {
  // Extract entities
  // Find relationships
  // Build graph structure
  return nodes;
}
```

---

## 📈 Progress Tracking

- [x] Phase 1: Design System Migration (100%)
- [x] Phase 2: Project Setup (100%)
- [ ] Phase 3: Core Components (0%)
- [ ] Phase 4: Video Modal (0%)
- [ ] Phase 5: Enhanced Tabs (0%)
- [ ] Phase 6: Research Integration (0%)
- [ ] Phase 7: Polish & Deploy (0%)

**Estimated Time**: 8-10 hours total
**Current Time Spent**: 2 hours
**Remaining**: 6-8 hours

---

## 🎯 Success Metrics

- ✅ All 5 videos display correctly
- ✅ Quality scores visible and accurate
- ✅ Modal opens with full transcript
- ✅ Search works across all segments
- ✅ Research papers link correctly
- ✅ Annotations save properly
- ✅ All animations smooth
- ✅ Responsive on mobile
- ✅ No console errors
- ✅ Fast load times (<2s)

---

## 📝 Next Actions

1. **Immediate**: Test current setup at http://localhost:4000
2. **Next 30 min**: Build VideoModal with Dialog
3. **Next 1 hour**: Complete all tab implementations
4. **Next 2 hours**: Add Research integration
5. **Final**: Polish and deploy

---

**Ready to continue building!** 🚀
