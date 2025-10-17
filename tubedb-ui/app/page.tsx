import Header from '@/components/common/header';
import DashboardTabs from '@/components/dashboard/dashboard-tabs';

export default function Home() {
  return (
    <main className="min-h-screen relative">
      {/* Subtle pattern overlay */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYgMi42ODYgNiA2cy0yLjY4NiA2LTYgNi02LTIuNjg2LTYtNiAyLjY4Ni02IDYtNiIgc3Ryb2tlPSJyZ2JhKDU5LCAxMzAsIDE0NiwgMC4wNSkiLz48L2c+PC9zdmc+')] opacity-30 pointer-events-none"></div>

      <div className="relative">
        <Header />
        <DashboardTabs />
      </div>
    </main>
  );
}
