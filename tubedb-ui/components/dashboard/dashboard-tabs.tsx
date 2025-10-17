'use client';

import { useState } from 'react';
import { LayoutDashboard, CheckCircle, BarChart3, FileJson, Lightbulb, Brain } from 'lucide-react';
import OverviewTab from './overview-tab';
import QCTab from './qc-tab';
import AnalyticsTab from './analytics-tab';
import RawDataTab from './raw-data-tab';
import InsightsTab from './insights-tab';
import AdvancedAnalyticsTab from './advanced-analytics-tab';

const tabs = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'qc', label: 'Quality Control', icon: CheckCircle },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'insights', label: 'Insights', icon: Lightbulb },
  { id: 'advanced', label: 'Advanced Analytics', icon: Brain },
  { id: 'raw', label: 'Raw Data', icon: FileJson },
];

export default function DashboardTabs() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="container mx-auto px-6 py-6">
      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 bg-white border border-gray-200 p-2 rounded-xl w-fit shadow-sm">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all font-semibold ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-slate-700 to-slate-800 text-white shadow-md'
                  : 'text-gray-600 hover:text-slate-800 hover:bg-gray-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'qc' && <QCTab />}
        {activeTab === 'analytics' && <AnalyticsTab />}
        {activeTab === 'insights' && <InsightsTab />}
        {activeTab === 'advanced' && <AdvancedAnalyticsTab />}
        {activeTab === 'raw' && <RawDataTab />}
      </div>
    </div>
  );
}
