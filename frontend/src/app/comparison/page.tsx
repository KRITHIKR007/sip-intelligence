'use client';

import React, { useState } from 'react';
import { GitCompare, PlusCircle, AlertTriangle, MinusCircle, Eye, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function ComparisonPage() {
  const [selectedBase, setSelectedBase] = useState('bhuj_p1');
  const [selectedTarget, setSelectedTarget] = useState('bhuj_p2');

  const diffs = [
    {
      type: 'ADDED',
      label: 'Home Signal S104 & Route Indicator',
      ent: '4-Aspect Multi-Unit Colour Light Signal',
      desc: 'Added at chainage 1840m on Quadrupled Up Main line to govern approach into Bhuj Phase II yard.',
      ref: 'IRISET Plate 100 Symbol #14',
    },
    {
      type: 'MODIFIED',
      label: 'Crossover Point 102A/B (Facing Point Lock)',
      ent: 'Motor Operated Turnout 1:12',
      desc: 'Facing Point Lock (FPL) detection distance updated from 90m to 120m to satisfy SEM Part II Chapter VIII speed upgrades (130 km/h).',
      ref: 'SEM Part II Rule 8.3',
    },
    {
      type: 'ADDED',
      label: 'Kavach RFID Tag Pair #504 / #505',
      ent: 'Track Identification Number (TIN) RFID Tag',
      desc: 'Positioned at 50m ± 5m ahead of Home Signal S104 for automatic train protection braking curve computation.',
      ref: 'RDSO/SPN/196 Clause 4.3',
    },
    {
      type: 'REMOVED',
      label: 'Mechanical Shunt Signal Sh-12',
      ent: 'Disc Shunt Signal',
      desc: 'Decommissioned and replaced with independent colour light shunt signal SH-22 as part of Electronic Interlocking migration.',
      ref: 'IRISET Plate 101 Symbol #15',
    },
    {
      type: 'MODIFIED',
      label: 'Track Circuit TC-24A / Axle Counter Boundary',
      ent: 'DC Track Circuit / High-Frequency Axle Counter',
      desc: 'Dead-section boundary adjusted to 1.6m ahead of fouling mark (FM) to prevent wheel-flange detection gaps.',
      ref: 'SEM Part II Rule 11.2',
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Real Drawing Revision Comparison</h1>
          <p className="text-xs text-slate-500 mt-0.5">Topological and entity-level differencing across revision states of Signalling Plans.</p>
        </div>
        <Link
          href="/viewer"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold hover:bg-blue-100 transition-colors self-start"
        >
          <Eye className="w-4 h-4" /> Open Drawing Viewer
        </Link>
      </div>

      {/* Selectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <label className="text-xs font-bold text-slate-700 block mb-1.5">Base Drawing Plan (Revision A)</label>
          <select
            value={selectedBase}
            onChange={(e) => setSelectedBase(e.target.value)}
            className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="bhuj_p1">Western Railway — Bhuj Phase I Baseline SIP (Rev 1.0)</option>
            <option value="asv_s3">Western Railway — Asarva Junction Sheet 03 (Facing Crossover)</option>
          </select>
        </div>
        <div>
          <label className="text-xs font-bold text-slate-700 block mb-1.5">Target Drawing Plan (Revision B)</label>
          <select
            value={selectedTarget}
            onChange={(e) => setSelectedTarget(e.target.value)}
            className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 font-semibold focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="bhuj_p2">10-WR_BHUJ_PH-II_MINI_SIP-07-11-20251.pdf (Quadrupling Scheme)</option>
            <option value="asv_s24">5-4192_2B_ASARVA_SIP_VPP_PROP (Sheet 24 Point Machines)</option>
          </select>
        </div>
      </div>

      {/* Differences List */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <GitCompare className="w-4 h-4 text-blue-600" />
            Topological & Equipment Changes ({diffs.length})
          </h2>
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
            Seq2Vec Topological Match: 98.4%
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {diffs.map((d, i) => (
            <div key={i} className="py-3.5 flex items-start gap-3">
              {d.type === 'ADDED' && <PlusCircle className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />}
              {d.type === 'MODIFIED' && <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />}
              {d.type === 'REMOVED' && <MinusCircle className="w-4 h-4 text-rose-600 mt-0.5 flex-shrink-0" />}

              <div className="flex-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900">{d.label}</span>
                  <span className="text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded font-mono font-semibold">
                    {d.ent}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      d.type === 'ADDED'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : d.type === 'MODIFIED'
                        ? 'bg-amber-50 text-amber-700 border border-amber-200'
                        : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}
                  >
                    {d.type}
                  </span>
                </div>
                <p className="text-slate-600 mt-1 leading-relaxed">{d.desc}</p>
                <div className="text-[10px] text-blue-600 font-semibold mt-1 font-mono">Reference: {d.ref}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
