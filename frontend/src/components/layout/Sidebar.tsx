'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FolderKanban,
  FileText,
  Eye,
  MessageSquare,
  Sparkles,
  GitCompare,
  ShieldCheck,
  BookOpen,
  Cpu,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'SIP Projects', href: '/projects', icon: FolderKanban },
  { label: 'Drawing Viewer', href: '/viewer', icon: Eye },
  { label: 'Symbol Explorer', href: '/symbols', icon: Sparkles },
  { label: 'Engineering Assistant', href: '/assistant', icon: MessageSquare },
  { label: 'Documents & Standards', href: '/documents', icon: FileText },
  { label: 'Revision Comparison', href: '/comparison', icon: GitCompare },
  { label: 'Validation Centre', href: '/validation', icon: ShieldCheck },
  { label: 'Knowledge Base', href: '/knowledge', icon: BookOpen },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-slate-200 bg-white flex flex-col h-screen sticky top-0 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-200 gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg tracking-wider shadow-sm">
          S
        </div>
        <div>
          <span className="font-semibold text-slate-900 text-sm tracking-tight block">SIP Intelligence</span>
          <span className="text-[10px] text-slate-500 font-medium tracking-wide uppercase block">Railway Engineering</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              )}
            >
              <Icon className={cn('w-4 h-4', isActive ? 'text-blue-600' : 'text-slate-400')} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Model Hardware Status (Replaces all Role-Based Login / RBL) */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/70">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shadow-xs">
            <Cpu className="w-4 h-4" />
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-xs font-bold text-slate-800 truncate">RTX 3050 GPU</p>
            <p className="text-[10px] text-emerald-700 font-semibold truncate">CUDA 12.4 • YOLO11n (800px)</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
