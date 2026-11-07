'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  FolderKanban,
  FileText,
  Activity,
  AlertCircle,
  Database,
  Cpu,
  ArrowUpRight,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  Eye,
  HelpCircle,
  Play,
} from 'lucide-react';
import { TutorialModal } from '@/components/layout/TutorialModal';

export default function DashboardPage() {
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);

  const stats = [
    { label: 'Standard Symbols', value: '56', icon: Sparkles, change: '100% extracted from IRISET plates' },
    { label: 'Real SIP Drawing Tiles', value: '66', icon: Eye, change: 'Asarva, Amarda, Bhuj Yards' },
    { label: 'Detected Equipment Instances', value: '2,986', icon: Database, change: 'YOLO11 fine-tuned (800px)' },
    { label: 'SEM Safety Rules', value: '14', icon: ShieldCheck, change: 'Indian Railways SEM & Kavach' },
  ];

  const realDrawings = [
    {
      id: '1',
      name: 'AMARDA_SIP_tile_023.png',
      station: 'Amarda Station Yard',
      zone: 'South Eastern Railway (Kharagpur Division)',
      detections: '6 entities (Platform: 78.0%, Running Signal: 42.6%)',
      status: 'Live Detected',
    },
    {
      id: '2',
      name: '5-4192_2B_ASARVA_SIP_VPP__tile_003.png',
      station: 'Asarva Junction (Sheet 03)',
      zone: 'Western Railway (Ahmedabad Division)',
      detections: '18 entities (Running Signal: 66.8%, Point Turnout: 46.2%)',
      status: 'Live Detected',
    },
    {
      id: '3',
      name: '5-4192_2B_ASARVA_SIP_VPP__tile_013.png',
      station: 'Asarva Junction (Sheet 13)',
      zone: 'Western Railway (Through Lines)',
      detections: '13 entities (Running Signals: 59.2%, 56.9%, 55.4%)',
      status: 'Live Detected',
    },
    {
      id: '4',
      name: '5-4192_2B_ASARVA_SIP_VPP__tile_024.png',
      station: 'Asarva Junction (Sheet 24)',
      zone: 'Western Railway (Facing Point Machines)',
      detections: '8 entities (Point Turnouts: 58.3%, 37.5%)',
      status: 'Live Detected',
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Welcome Banner with Tutorial Trigger */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-950 rounded-2xl p-6 sm:p-8 text-white shadow-lg relative overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/30 text-blue-200 border border-blue-400/30">
            <Sparkles className="w-3.5 h-3.5 text-blue-300" />
            Open Model Platform — Direct Access (No Registration Needed)
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Multimodal Railway Signalling Plan Intelligence Platform
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Real Indian Railways SIP drawing comprehension, symbol detection, and standards validation powered by fine-tuned YOLO11, Seq2Vec, and R-GCN running locally on private hardware.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Link
              href="/viewer"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold shadow-md transition-all flex items-center gap-2"
            >
              <Eye className="w-4 h-4" /> Open Drawing Viewer
            </Link>
            <Link
              href="/symbols"
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-lg text-xs font-semibold transition-all flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-amber-300" /> 56-Symbol Catalogue
            </Link>
            <button
              onClick={() => setIsTutorialOpen(true)}
              className="px-4 py-2 bg-white text-slate-900 hover:bg-slate-100 rounded-lg text-xs font-bold shadow-md transition-all flex items-center gap-2"
            >
              <HelpCircle className="w-4 h-4 text-blue-600" /> Take Platform Tour
            </button>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div key={idx} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">{s.label}</span>
                <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-2xl font-extrabold text-slate-900 tracking-tight">{s.value}</div>
                <div className="text-[11px] font-semibold text-emerald-600 mt-1">{s.change}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real Ingested Drawings and Model Registry */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model Registry Status */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-600" />
              Trained Model Status (GPU)
            </h2>
            <span className="text-[10px] px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-full font-bold">
              CUDA Active
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <div className="flex justify-between items-center font-bold text-slate-900">
                <span>YOLO11n Symbol Detector</span>
                <span className="text-emerald-600 text-[11px]">800px Mode</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Fine-tuned on 290 tiles (Platform: 78.0%, Signals: 66.8%)
              </p>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <div className="flex justify-between items-center font-bold text-slate-900">
                <span>Seq2Vec Structural BiLSTM</span>
                <span className="text-emerald-600 text-[11px]">256d L2</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Trained on entity sequences along track chainage ($X$-axis)
              </p>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <div className="flex justify-between items-center font-bold text-slate-900">
                <span>Railway R-GCN Graph Model</span>
                <span className="text-emerald-600 text-[11px]">256d Pooled</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Topological interlocking adjacency & route cross-locking
              </p>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <div className="flex justify-between items-center font-bold text-slate-900">
                <span>Grounded Documentation</span>
                <span className="text-blue-600 text-[11px]">2.pdf / IRISET</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                48 EI notations, 20 Kavach RFID tags, Plates 99-105
              </p>
            </div>
          </div>
        </div>

        {/* Real Ingested Drawing Sheets */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Eye className="w-4 h-4 text-blue-600" />
              Live Ingested Railway SIP Drawings
            </h2>
            <Link href="/viewer" className="text-xs text-blue-600 font-bold hover:underline flex items-center gap-1">
              View All in Canvas <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {realDrawings.map((d) => (
              <div key={d.id} className="p-3.5 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/20 transition-all text-xs flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{d.station}</span>
                    <span className="text-[10px] bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-bold">
                      {d.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 font-mono mt-0.5">{d.name} • {d.zone}</p>
                  <p className="text-[11px] text-slate-600 mt-1 font-semibold">{d.detections}</p>
                </div>
                <Link
                  href="/viewer"
                  className="px-3 py-1.5 bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-700 rounded-lg text-xs font-bold transition-colors whitespace-nowrap"
                >
                  Inspect Drawing
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>

      <TutorialModal
        isOpen={isTutorialOpen}
        onClose={() => setIsTutorialOpen(false)}
      />
    </div>
  );
}
