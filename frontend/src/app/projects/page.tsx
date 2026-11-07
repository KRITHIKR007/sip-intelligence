'use client';

import React from 'react';
import Link from 'next/link';
import { FolderKanban, FileText, ArrowRight, Eye, Sparkles, CheckCircle2 } from 'lucide-react';

const REAL_PROJECTS = [
  {
    id: 'proj-asv',
    code: 'WR-ASV-2025',
    name: 'Western Railway — Asarva Junction (ASV)',
    division: 'Ahmedabad Division (Western Railway)',
    file: '5-4192_2B_ASARVA_SIP_VPP_PROP_DT_09-07-2025.pdf',
    sheets: 32,
    entitiesCount: 181,
    desc: 'Signalling and Interlocking Plan (SIP) for Electronic Interlocking VPP proposal. High-density junction layout with main-line crossovers and 4-aspect multi-unit colour light signals.',
    keyFeatures: [
      'Sheet 03: Up & Down main crossover 101A/B with Home Signal S1 (66.8% conf)',
      'Sheet 13: Intermediate automatic block section signals (A10, A12, A14)',
      'Sheet 24: Facing Point Lock (FPL) switches and motor-operated turnout machines',
    ],
    status: 'ACTIVE DATASET',
    actionHref: '/viewer',
    actionLabel: 'Open in Drawing Viewer',
  },
  {
    id: 'proj-amrd',
    code: 'SER-AMRD-SIP',
    name: 'South Eastern Railway — Amarda Station Yard (AMRD)',
    division: 'Kharagpur Division (South Eastern Railway)',
    file: 'AMARDA_SIP.pdf',
    sheets: 28,
    entitiesCount: 42,
    desc: 'Complete station yard interlocking scheme covering passenger platform loops, siding protection, starter signals, and advance starters.',
    keyFeatures: [
      'Sheet 23: Platform 1 and Island Platform 2 (78.0% & 61.4% conf)',
      'Facing points with trap switch derailing protection',
      'Starter signals with calling-on subsidiary units',
    ],
    status: 'ACTIVE DATASET',
    actionHref: '/viewer',
    actionLabel: 'Open in Drawing Viewer',
  },
  {
    id: 'proj-bhuj',
    code: 'WR-BHUJ-PH2',
    name: 'Western Railway — Bhuj Section Quadrupling (BHUJ)',
    division: 'Vadodara / Ahmedabad Division (Western Railway)',
    file: '10-WR_BHUJ_PH-II_MINI_SIP-07-11-20251.pdf',
    sheets: 12,
    entitiesCount: 56,
    desc: 'Phase II quadrupling track scheme with proposed Electronic Interlocking and automatic block signalling sections between Bhuj and Samakhiali.',
    keyFeatures: [
      'Mini-SIP electronic interlocking scheme',
      'Revision diff against Phase I baseline layout',
      'Continuous track circuit detection boundaries',
    ],
    status: 'ACTIVE DATASET',
    actionHref: '/comparison',
    actionLabel: 'Compare Revision Diff',
  },
  {
    id: 'proj-magh',
    code: 'CR-MAGH-V3',
    name: 'Central Railway — Manikgarh Junction (MAGH)',
    division: 'Nagpur Division (Central Railway)',
    file: '3.SIPMANIKGARHJN-ABSIPU.1287E_V3_APPROVE_P62.pdf',
    sheets: 18,
    entitiesCount: 74,
    desc: 'Approved V3 signalling plan featuring sand hump isolation, electronic route control charts, and interlocked level crossing gate interconnections.',
    keyFeatures: [
      'Approved V3 electronic interlocking logic',
      'Sand hump isolation on goods loop lines',
      'SEM Rule 8.1.1 isolation compliance verified',
    ],
    status: 'APPROVED SCHEME',
    actionHref: '/documents',
    actionLabel: 'Inspect Plan Record',
  },
  {
    id: 'proj-kavach',
    code: 'RDSO-KAVACH-EI',
    name: 'Kavach & Electronic Interlocking Standard Project',
    division: 'RDSO & IRISET S&T Directorate',
    file: '2.pdf & IRISET_SnT_Drawings_Pages_99_to_105.pdf',
    sheets: 55,
    entitiesCount: 56,
    desc: 'Authoritative Indian Railways Signalling Reference Symbol Register covering 56 standard IRISET symbol plates, 48 Electronic Interlocking notations, and 20 Kavach RFID tag rules.',
    keyFeatures: [
      '56 standardized symbol crops extracted from plates 99 to 105',
      'Kavach RFID tag approach placement specifications (50m ± 5m)',
      'Signal Overlap (180m) and Block Overlap safety matrices',
    ],
    status: 'AUTHORITATIVE SPEC',
    actionHref: '/symbols',
    actionLabel: 'Explore 56 Symbols',
  },
];

export default function ProjectsPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Real SIP Engineering Projects</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real Indian Railways Signalling and Interlocking Plans ingested and indexed from the active dataset.
          </p>
        </div>
        <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full self-start">
          5 Real Projects Active
        </span>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {REAL_PROJECTS.map((p) => (
          <div
            key={p.id}
            className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:border-blue-400 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 bg-blue-50 text-blue-700 text-[10px] font-bold rounded-full uppercase tracking-wider border border-blue-200">
                  {p.status}
                </span>
                <span className="text-[11px] font-mono text-slate-400 font-bold">{p.code}</span>
              </div>

              <h2 className="text-sm font-bold text-slate-900">{p.name}</h2>
              <p className="text-[11px] font-semibold text-slate-500 mt-0.5">{p.division}</p>

              <p className="text-xs text-slate-600 mt-2 leading-relaxed">{p.desc}</p>

              {/* Key Features */}
              <div className="mt-3 bg-slate-50 p-2.5 rounded-lg border border-slate-100 space-y-1">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Key Features:</p>
                {p.keyFeatures.map((kf, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-[11px] text-slate-600">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>{kf}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5 text-slate-500 font-medium">
                <FileText className="w-3.5 h-3.5 text-blue-600" />
                {p.sheets} Drawing Sheets
              </span>

              <Link
                href={p.actionHref}
                className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-bold bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition-colors"
              >
                {p.actionLabel} <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
