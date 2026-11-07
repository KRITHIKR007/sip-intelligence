'use client';

import React from 'react';
import { BookOpen, Download, ShieldCheck, FileText, CheckCircle2 } from 'lucide-react';

const REAL_STANDARDS = [
  {
    title: '2.pdf — Kavach & Electronic Interlocking (SIP Symbol Register)',
    revision: 'Version 2.0 (RDSO & S&T Standards Directorate)',
    authority: 'Indian Railways / Ministry of Railways',
    description: 'Comprehensive Symbol Register for Signalling and Interlocking Plans (SIP). Covers 48 Electronic Interlocking notations, 20 Kavach RFID Tag / Track Identification Number (TIN) specifications, and full plate appendices.',
    downloadUrl: '/reference/2.pdf',
    pages: '48 pages',
    size: '1.2 MB',
    status: 'INGESTED & GROUNDED',
  },
  {
    title: 'IRISET Signalling & Telecommunication Drawing Standards (Plates 99 to 105)',
    revision: 'Official S&T Plates',
    authority: 'Indian Railways Institute of Signal Engineering and Telecommunications (IRISET)',
    description: 'Authoritative graphical plates establishing standard symbols for Multi-Aspect Colour Light Signals (Home, Distant, Starter, Auto), Shunt Signals, Interlocked Level Crossing Gates, Axle Counters, and Facing Point Locks.',
    downloadUrl: '/reference/IRISET_SnT_Drawings_Pages_99_to_105.pdf',
    pages: '7 plates',
    size: '233 KB',
    status: 'INGESTED & GROUNDED',
  },
  {
    title: 'Indian Railways Signal Engineering Manual (SEM Part II)',
    revision: 'Latest Codified Edition (Chapter VII & VIII)',
    authority: 'Railway Board / S&T Directorate',
    description: 'Mandatory technical regulations governing Signal Overlap (minimum 180m for 2-aspect, 120m for MACLS), Block Overlap (400m / 180m), Passenger Line Isolation via Sand Humps or Trap Points, and Calling-On signal timer interlocks.',
    downloadUrl: null,
    pages: 'Chapter VII & VIII',
    size: 'Codified Rulebase',
    status: 'ACTIVE RULEBASE',
  },
  {
    title: 'RDSO/SPN/196 — Kavach (TCAS) System Specification',
    revision: 'Specification SPN/196 Revision 4.0',
    authority: 'Research Designs and Standards Organisation (RDSO)',
    description: 'Technical requirements for Kavach Automatic Train Protection (ATP). Dictates RFID tag placement tolerances (50m ± 5m from signals), Track Identification Numbering, speed profile curves, and radio communication boundaries.',
    downloadUrl: null,
    pages: 'Technical Specification',
    size: 'Codified Rulebase',
    status: 'ACTIVE RULEBASE',
  },
];

export default function KnowledgePage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Real Standards Knowledge Base</h1>
          <p className="text-xs text-slate-500 mt-0.5">Authoritative Indian Railways manuals, specifications, and drawing plates governing the platform.</p>
        </div>
        <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full self-start">
          Authoritative Standards Grounded
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {REAL_STANDARDS.map((s, idx) => (
          <div key={idx} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] font-bold rounded-full uppercase border border-emerald-200">
                  {s.status}
                </span>
                <span className="text-[11px] text-slate-400 font-mono font-semibold">{s.pages}</span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 leading-snug">{s.title}</h3>
              <p className="text-[11px] font-semibold text-slate-500 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-600" /> {s.authority}
              </p>
              <p className="text-xs text-slate-600 leading-relaxed pt-1">{s.description}</p>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono text-[11px]">{s.size}</span>
              {s.downloadUrl ? (
                <a
                  href={s.downloadUrl}
                  download
                  className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-bold bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg border border-blue-200 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Download Standard PDF
                </a>
              ) : (
                <span className="text-slate-500 font-medium text-[11px]">Codified in Rule Engine</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
