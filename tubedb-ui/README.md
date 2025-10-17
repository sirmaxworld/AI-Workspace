# 🎨 TubeDB UI

Internal Quality Assurance dashboard for video transcript analysis.

## 📍 Quick Links

- **📖 START HERE**: [CURSOR_BUILD_GUIDE.md](./CURSOR_BUILD_GUIDE.md)
- **🎨 Visual Mockups**: [docs/UI_VISUAL_MOCKUPS.md](./docs/UI_VISUAL_MOCKUPS.md)
- **🏗️ Technical Specs**: [docs/UI_IMPLEMENTATION_PLAN.md](./docs/UI_IMPLEMENTATION_PLAN.md)
- **🎯 Design System**: [docs/UI_DESIGN_COMPARISON.md](./docs/UI_DESIGN_COMPARISON.md)

## 🚀 Getting Started in Cursor.ai

1. Open this folder in Cursor:
   ```bash
   cd /Users/yourox/AI-Workspace/tubedb-ui
   cursor .
   ```

2. Read `CURSOR_BUILD_GUIDE.md` - It has EVERYTHING you need

3. Copy the "CHECKLIST FOR CURSOR.AI" into your first Cursor chat

4. Start building phase by phase!

## 📊 What This Does

Quality assurance dashboard for 5 Greg Isenberg videos:
- **Overview**: System stats, video grid, batch info
- **QC Tab**: Quality scores, filtering, verification
- **Analytics**: Charts, trends, performance metrics  
- **Raw Data**: JSON inspector, export tools

## 🎨 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + shadcn/ui
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Language**: TypeScript
- **Data**: File-based (JSON)

## 📁 Data Location

```
/Users/yourox/AI-Workspace/data/transcripts/batch_20251015_193743.json
```

5 videos, 4,117 segments, fully processed and ready!

## 📋 Build Phases

1. **Setup** (30 min) - Project structure, dependencies
2. **Layout** (1 hour) - Header, tabs, navigation
3. **Data Layer** (1 hour) - JSON reading, types
4. **Overview Tab** (2 hours) - Stats, video grid
5. **Video Modal** (2 hours) - Detail view, transcript
6. **QC Tab** (2 hours) - Quality verification
7. **Analytics** (2 hours) - Charts and metrics
8. **Raw Data** (1 hour) - JSON inspector
9. **Polish** (2 hours) - Animations, responsive

**Total**: ~13 hours for MVP, ~20 hours for full version

## ✅ Success Criteria

- [ ] All 5 videos visible in grid
- [ ] QC scores display correctly  
- [ ] Transcript searchable and readable
- [ ] Topics filterable
- [ ] Dark theme polished
- [ ] Animations smooth
- [ ] Load time < 2 seconds

## 🎯 Design Inspiration

Based on YouTube Vault's modern design:
- Dark theme with glassmorphism
- Blue-to-cyan gradients
- Smooth Framer Motion animations
- Professional, polished UI

Adapted for internal QA workflows.

## 📖 Documentation

All planning docs in `docs/`:
- `UI_README.md` - Overview
- `UI_EXECUTIVE_SUMMARY.md` - High-level summary
- `UI_IMPLEMENTATION_PLAN.md` - Complete technical specs
- `UI_DESIGN_COMPARISON.md` - Design decisions
- `UI_VISUAL_MOCKUPS.md` - ASCII mockups of every screen

## 🔧 Development

```bash
# Install dependencies (after creating package.json)
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 💡 Tips

- Reference `CURSOR_BUILD_GUIDE.md` for phase-by-phase instructions
- Check `.cursorrules` for coding standards
- Look at mockups in `docs/UI_VISUAL_MOCKUPS.md` when building
- Use types from the guide's `lib/types.ts` section
- Copy color constants from the guide

## 🆘 Need Help?

1. Check `CURSOR_BUILD_GUIDE.md`
2. Review relevant docs in `docs/`
3. Verify data structure in JSON file
4. Ask Cursor.ai specific questions with context

---

**Built with ❤️ for quality assurance**

Project created: October 15, 2025