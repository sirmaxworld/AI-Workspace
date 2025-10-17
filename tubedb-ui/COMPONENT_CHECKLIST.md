# 📋 TubeDB UI - Component Checklist

Track your build progress here!

## ✅ Setup Phase

- [ ] Create Next.js 14 project with TypeScript
- [ ] Install Tailwind CSS
- [ ] Setup shadcn/ui with dark theme
- [ ] Install Framer Motion
- [ ] Install Lucide React icons
- [ ] Install Recharts
- [ ] Create folder structure
- [ ] Setup TypeScript types (lib/types.ts)
- [ ] Setup constants (lib/constants.ts)
- [ ] Create .cursorrules file (already done!)

## 📁 Core Files

- [ ] `lib/types.ts` - TypeScript interfaces
- [ ] `lib/constants.ts` - Colors, gradients
- [ ] `lib/utils.ts` - Helper functions
- [ ] `lib/api.ts` - Data fetching

## 🎨 UI Components (shadcn/ui)

- [ ] button
- [ ] card
- [ ] dialog
- [ ] input
- [ ] tabs
- [ ] select

## 🏠 Layout Components

- [ ] `app/layout.tsx` - Root layout
- [ ] `app/page.tsx` - Main dashboard page
- [ ] `components/common/header.tsx` - Top header with search
- [ ] `components/common/search-bar.tsx` - Search input
- [ ] `components/layout/main-layout.tsx` - Page wrapper

## 📊 Dashboard Components

### Common Components
- [ ] `components/common/stat-card.tsx` - Stat display with icon
- [ ] `components/common/batch-selector.tsx` - Dropdown for batches
- [ ] `components/video/quality-badge.tsx` - QC score indicator

### Overview Tab
- [ ] `components/dashboard/overview-tab.tsx` - Main overview
- [ ] `components/video/video-card.tsx` - Grid item for videos
- [ ] System stats section (4 stat cards)
- [ ] Batch info section
- [ ] Video grid layout

### QC Tab
- [ ] `components/dashboard/qc-tab.tsx` - Quality control view
- [ ] Filter controls (score, topics, date)
- [ ] Sortable video list
- [ ] Detailed QC display

### Analytics Tab
- [ ] `components/dashboard/analytics-tab.tsx` - Analytics view
- [ ] Topic distribution chart (Recharts)
- [ ] Quality trends graph
- [ ] Performance metrics cards
- [ ] Word cloud component

### Raw Data Tab
- [ ] `components/dashboard/raw-data-tab.tsx` - JSON viewer
- [ ] Batch selector
- [ ] JSON formatter
- [ ] Copy/download buttons

## 🎬 Video Components

- [ ] `components/video/video-modal.tsx` - Detail modal
- [ ] `components/video/transcript-viewer.tsx` - Transcript display
- [ ] Overview tab in modal
- [ ] Transcript tab in modal
- [ ] QC tab in modal

## 🎨 Styling Features

- [ ] Dark theme (slate-900 background)
- [ ] Glass effect on cards (backdrop-blur-md)
- [ ] Gradient backgrounds for stat cards
- [ ] Quality score color coding
- [ ] Hover effects on cards
- [ ] Responsive design (mobile-friendly)

## ✨ Animations

- [ ] Tab switching animations
- [ ] Modal open/close animations
- [ ] Card hover animations
- [ ] Quality score fill animations
- [ ] Page transition animations

## 🔍 Functionality

### Data Layer
- [ ] Read batch JSON file
- [ ] Parse video data
- [ ] Calculate system stats
- [ ] Filter videos by quality
- [ ] Filter videos by topic
- [ ] Search transcripts

### Features
- [ ] Tab navigation works
- [ ] Video cards clickable
- [ ] Modal opens/closes
- [ ] Transcript searchable
- [ ] Filters functional
- [ ] Sort options work
- [ ] Copy JSON to clipboard
- [ ] Download JSON file
- [ ] Export functionality

## 🐛 Testing

- [ ] All 5 videos display correctly
- [ ] QC scores show proper values (0.85, 0.75, etc.)
- [ ] Timestamps formatted correctly
- [ ] Topics displayed properly
- [ ] Search returns results
- [ ] Filters update view
- [ ] No console errors
- [ ] Responsive on mobile
- [ ] Performance acceptable (< 2s load)

## 🎯 Polish

- [ ] Loading states added
- [ ] Error handling implemented
- [ ] Empty states designed
- [ ] Tooltips where helpful
- [ ] Keyboard shortcuts (optional)
- [ ] Accessibility reviewed
- [ ] Cross-browser tested

## 📦 Deployment Prep

- [ ] Build succeeds without errors
- [ ] TypeScript compiles cleanly
- [ ] No unused dependencies
- [ ] Environment variables configured
- [ ] README updated with setup steps
- [ ] Documentation complete

---

## 📊 Progress Tracking

**Completed**: __ / 85 items

**Current Phase**: Setup

**Next Up**: Create project structure

---

## 💡 Quick Tips

- Check off items as you complete them
- Reference `CURSOR_BUILD_GUIDE.md` for detailed instructions
- Look at mockups in `docs/UI_VISUAL_MOCKUPS.md` when building
- Use this checklist in Cursor chats to track progress

---

**Last Updated**: October 15, 2025