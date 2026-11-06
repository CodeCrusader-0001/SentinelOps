import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScrollText,
  AlertTriangle,
  Sparkles,
  BookOpen,
  CheckCircle2,
  FileCheck2,
  Settings
} from 'lucide-react';

const navItems = [
  { name: 'Overview', path: '/', icon: LayoutDashboard },
  { name: 'Live Logs', path: '/logs', icon: ScrollText },
  { name: 'Incidents', path: '/incidents', icon: AlertTriangle },
  { name: 'AI Investigation', path: '/investigation', icon: Sparkles },
  { name: 'Knowledge Base', path: '/knowledge', icon: BookOpen },
  { name: 'Remediation', path: '/remediation', icon: CheckCircle2 },
  { name: 'Audit Logs', path: '/audit', icon: FileCheck2 },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-[#111118] border-r border-[#242436] flex flex-col justify-between py-6">
      <div className="space-y-1 px-3">
        <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 px-3 pb-2">
          Operations & Control
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-[#151521]'
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </div>

      <div className="px-6 py-4 mx-3 rounded-lg bg-[#151521] border border-[#242436] text-xs">
        <div className="text-gray-400 font-medium">DeepLog LSTM Engine</div>
        <div className="text-emerald-400 text-[11px] font-mono mt-1 flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block" />
          <span>F1 Score: 90.32%</span>
        </div>
        <div className="text-[10px] text-gray-500 mt-2 font-mono">Model: gemini-3.8-flash</div>
      </div>
    </aside>
  );
};

