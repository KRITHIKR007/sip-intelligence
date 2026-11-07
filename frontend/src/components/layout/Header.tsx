'use client';

import React, { useState, useEffect } from 'react';
import { Search, Shield, BookOpen, Sparkles, HelpCircle } from 'lucide-react';
import { TutorialModal } from './TutorialModal';

export function Header() {
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);

  useEffect(() => {
    // Check if new visitor
    const viewed = localStorage.getItem('sip_tutorial_completed');
    if (!viewed) {
      setIsTutorialOpen(true);
      localStorage.setItem('sip_tutorial_completed', 'true');
    }
  }, []);

  return (
    <>
      <header className="h-16 border-b border-slate-200 bg-white px-8 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4 flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search plans, signals, IRS standards..."
              className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Open Access Model Badge - No Sign Up Needed */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-[11px] font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            Open Model Mode — No Sign-Up Needed
          </div>

          {/* Airgapped Private Deployment Badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 border border-emerald-200 rounded-full text-emerald-700 text-[11px] font-medium">
            <Shield className="w-3.5 h-3.5 text-emerald-600" />
            CUDA GPU Active
          </div>

          {/* Interactive Tutorial Button */}
          <button
            onClick={() => setIsTutorialOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors border border-slate-200 shadow-sm"
          >
            <HelpCircle className="w-3.5 h-3.5 text-blue-600" />
            Platform Tutorial
          </button>
        </div>
      </header>

      <TutorialModal
        isOpen={isTutorialOpen}
        onClose={() => setIsTutorialOpen(false)}
      />
    </>
  );
}
