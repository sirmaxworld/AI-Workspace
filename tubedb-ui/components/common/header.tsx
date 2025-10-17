import { Database, Search, Library } from 'lucide-react';
import Link from 'next/link';

export default function Header() {
  return (
    <header className="border-b border-gray-200 backdrop-blur-sm bg-white/80 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <Link href="/">
            <div className="flex items-center gap-3 cursor-pointer group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-slate-600 to-slate-700 rounded-lg blur opacity-30"></div>
              <div className="relative bg-gradient-to-r from-slate-700 to-slate-800 p-3 rounded-lg shadow-md">
                <Database className="w-7 h-7 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-800 group-hover:text-slate-600 transition-colors">TubeDB</h1>
              <p className="text-xs text-gray-600 font-medium">Business Intelligence Hub · 332 Videos · 1,056 Opportunities</p>
            </div>
            </div>
          </Link>

          {/* Search Bar */}
          <div className="flex items-center gap-3 flex-1 max-w-md ml-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search transcripts..."
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Link href="/library">
              <button className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-800 text-white rounded-lg shadow-sm transition-colors">
                <Library className="w-4 h-4" />
                <span className="text-sm font-medium">Video Library</span>
              </button>
            </Link>
            <div className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-sm text-gray-700 font-medium">System Active</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
