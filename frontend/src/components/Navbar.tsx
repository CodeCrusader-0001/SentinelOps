import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, Radio, User as UserIcon, LogOut } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-[#111118] border-b border-[#242436] px-6 flex items-center justify-between z-20">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Shield className="w-5 h-5 text-black stroke-[2.5]" />
        </div>
        <div>
          <span className="text-lg font-bold tracking-wider text-white">SENTINEL<span className="text-cyan-400">OPS</span></span>
          <span className="ml-2 text-xs font-mono uppercase bg-cyan-950/80 text-cyan-400 px-2 py-0.5 rounded border border-cyan-800/50">Enterprise v1.0</span>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        {/* Live System Signal Indicator */}
        <div className="flex items-center space-x-2 text-xs font-mono text-emerald-400 bg-emerald-950/40 px-3 py-1.5 rounded-full border border-emerald-800/40">
          <Radio className="w-3.5 h-3.5 animate-pulse text-emerald-400" />
          <span>SYS_TELEMETRY: ACTIVE</span>
        </div>

        {/* User Role Badge & Profile */}
        {user && (
          <div className="flex items-center space-x-4 pl-4 border-l border-[#242436]">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-[#151521] border border-[#242436] flex items-center justify-center">
                <UserIcon className="w-4 h-4 text-gray-300" />
              </div>
              <div className="text-left">
                <div className="text-xs font-medium text-gray-200">{user.full_name}</div>
                <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider">{user.role}</div>
              </div>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 text-gray-400 hover:text-rose-400 hover:bg-rose-950/30 rounded transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

