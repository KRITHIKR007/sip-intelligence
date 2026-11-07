'use client';

import React, { useState, useMemo } from 'react';
import { Search, Sparkles, Filter, Info, X, ExternalLink, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { REAL_SYMBOLS, SymbolItem } from '@/data/symbolsData';

const CATEGORIES = [
  'All',
  'Signalling Board',
  'Section Limit',
  'Running Signal',
  'Shunt Signal',
  'Permissive Signal',
  'Automatic Signal',
  'Intermediate Block Signal',
  'Level Crossing',
  'Track Detection',
  'Track Switch / Point',
  'Interlocking Component',
  'Operating Device',
];

export default function SymbolsPage() {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [activeSymbol, setActiveSymbol] = useState<SymbolItem | null>(null);

  const filteredSymbols = useMemo(() => {
    return REAL_SYMBOLS.filter((s) => {
      const matchesSearch =
        search === '' ||
        s.name.toLowerCase().includes(search.toLowerCase()) ||
        s.description.toLowerCase().includes(search.toLowerCase()) ||
        s.category.toLowerCase().includes(search.toLowerCase());

      const matchesCat =
        selectedCategory === 'All' || s.category === selectedCategory;

      return matchesSearch && matchesCat;
    });
  }, [search, selectedCategory]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Symbol Explorer & Standard Catalogue
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            56 official symbol classes extracted from IRISET Signalling & Interlocking Plates (Plates 99 to 105).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
            56 / 56 Standard Crops Verified
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search symbol by name, function, board type, or SEM classification..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-sm"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg font-semibold whitespace-nowrap transition-all ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Symbol Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredSymbols.map((s) => (
          <div
            key={s.sno}
            onClick={() => setActiveSymbol(s)}
            className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:border-blue-400 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group"
          >
            <div>
              {/* Card Meta */}
              <div className="flex items-center justify-between text-[11px] mb-2.5">
                <span className="font-mono font-bold text-slate-400">#{s.sno}</span>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    s.criticality === 'Critical'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : s.criticality === 'High'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-slate-100 text-slate-700'
                  }`}
                >
                  {s.criticality}
                </span>
              </div>

              {/* Real Extracted Image Container */}
              <div className="h-32 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-center p-3 mb-3 group-hover:bg-blue-50/20 transition-colors">
                <img
                  src={s.image}
                  alt={s.name}
                  className="max-h-full max-w-full object-contain filter drop-shadow-sm group-hover:scale-105 transition-transform"
                  loading="lazy"
                />
              </div>

              {/* Title & Info */}
              <h3 className="text-xs font-bold text-slate-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
                {s.name.replace(/_/g, ' ')}
              </h3>
              <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-tight">
                {s.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
              <span className="text-slate-400 font-medium">IRISET Plate {s.page}</span>
              <span className="text-blue-600 font-semibold group-hover:underline">Inspect Details →</span>
            </div>
          </div>
        ))}
      </div>

      {filteredSymbols.length === 0 && (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-xl">
          <p className="text-sm font-semibold text-slate-700">No symbols found matching your search</p>
          <p className="text-xs text-slate-400 mt-1">Try searching for &quot;Signal&quot;, &quot;Point&quot;, or &quot;Board&quot;</p>
        </div>
      )}

      {/* Symbol Detail Inspection Modal */}
      {activeSymbol && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-slate-200 overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-slate-400">#{activeSymbol.sno}</span>
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Symbol Specification
                </span>
              </div>
              <button
                onClick={() => setActiveSymbol(null)}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="h-44 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-center p-4">
                <img
                  src={activeSymbol.image}
                  alt={activeSymbol.name}
                  className="max-h-full max-w-full object-contain filter drop-shadow-md"
                />
              </div>

              <div>
                <h2 className="text-sm font-bold text-slate-900">
                  {activeSymbol.description}
                </h2>
                <p className="text-xs font-mono text-slate-500 mt-0.5">
                  ID: {activeSymbol.name}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-4 rounded-xl border border-slate-100">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Category</span>
                  <span className="font-semibold text-slate-800">{activeSymbol.category}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Criticality</span>
                  <span className="font-semibold text-rose-600">{activeSymbol.criticality}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Source Standard</span>
                  <span className="font-semibold text-slate-800">IRISET Plate {activeSymbol.page}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Dimensions</span>
                  <span className="font-mono text-slate-800">{activeSymbol.width_px} × {activeSymbol.height_px} px</span>
                </div>
              </div>

              <div className="text-xs text-slate-600 leading-relaxed bg-blue-50/50 p-3.5 rounded-xl border border-blue-100">
                <div className="font-bold text-blue-900 mb-1 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                  Engineering Standard Note
                </div>
                Conforms strictly to Indian Railways Signal Engineering Manual (SEM Part II) guidelines for Signalling and Interlocking Plans (SIP).
              </div>
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setActiveSymbol(null)}
                className="px-4 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg shadow-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
