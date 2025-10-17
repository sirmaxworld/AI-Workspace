import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  gradient: string;
}

export default function StatCard({ label, value, icon: Icon, gradient }: StatCardProps) {
  // Map gradients to icon colors for the light theme
  const iconColorMap: Record<string, string> = {
    'from-blue-500 to-cyan-500': 'text-slate-600',
    'from-purple-500 to-pink-500': 'text-blue-700',
    'from-green-500 to-emerald-500': 'text-blue-800',
    'from-orange-500 to-red-500': 'text-slate-700'
  };

  return (
    <div className="glass-card p-4">
      <div className="flex items-center space-x-2">
        <Icon className={`w-5 h-5 ${iconColorMap[gradient] || 'text-slate-600'}`} />
        <div>
          <p className="text-2xl font-bold text-slate-800">{value}</p>
          <p className="text-xs text-gray-600">{label}</p>
        </div>
      </div>
    </div>
  );
}
