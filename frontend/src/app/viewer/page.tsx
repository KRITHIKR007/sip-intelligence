'use client';

import React, { useState, useEffect } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Layers,
  Tag,
  Download,
  CheckCircle2,
  Eye,
  Sliders,
  ChevronDown,
} from 'lucide-react';

interface SIPEntity {
  id: string;
  label: string;
  type: string;
  conf: string;
  confidence_raw: number;
  x: number;
  y: number;
  width: number;
  height: number;
  xyxy: number[];
}

interface DrawingSheet {
  filename: string;
  url: string;
  title: string;
  station: string;
  zone: string;
  description: string;
  entities: SIPEntity[];
}

const REAL_DRAWINGS: DrawingSheet[] = [
  {
    filename: 'AMARDA_SIP_tile_023.png',
    url: '/drawings/AMARDA_SIP_tile_023.png',
    title: 'Amarda Station Interlocking Plan — Sheet 23',
    station: 'Amarda (AMRD)',
    zone: 'South Eastern Railway (Kharagpur Division)',
    description: 'Passenger platform line with starter signal aspects and siding connections.',
    entities: [
      { id: 'amrd_1', label: 'Platform 1', type: 'Platform', conf: '78.0%', confidence_raw: 0.78, x: 0, y: 34, width: 371, height: 43, xyxy: [0, 34, 371, 77] },
      { id: 'amrd_2', label: 'Platform 2 Island', type: 'Platform', conf: '61.4%', confidence_raw: 0.61, x: 0, y: 0, width: 383, height: 37, xyxy: [0, 0, 383, 37] },
      { id: 'amrd_3', label: 'Starter Signal 12', type: 'Running_Signal', conf: '42.6%', confidence_raw: 0.43, x: 376, y: 527, width: 56, height: 51, xyxy: [376, 527, 432, 578] },
      { id: 'amrd_4', label: 'Advance Starter 14', type: 'Running_Signal', conf: '37.3%', confidence_raw: 0.37, x: 1115, y: 555, width: 40, height: 45, xyxy: [1115, 555, 1155, 600] },
      { id: 'amrd_5', label: 'Shunt Signal 4', type: 'Running_Signal', conf: '35.2%', confidence_raw: 0.35, x: 749, y: 678, width: 46, height: 41, xyxy: [749, 678, 795, 719] },
      { id: 'amrd_6', label: 'Calling-On C2', type: 'Running_Signal', conf: '35.0%', confidence_raw: 0.35, x: 405, y: 712, width: 45, height: 44, xyxy: [405, 712, 450, 756] },
    ],
  },
  {
    filename: '5-4192_2B_ASARVA_SIP_VPP__tile_003.png',
    url: '/drawings/5-4192_2B_ASARVA_SIP_VPP__tile_003.png',
    title: 'Asarva Junction SIP — Sheet 03 (Turnouts & Home Signals)',
    station: 'Asarva (ASV)',
    zone: 'Western Railway (Ahmedabad Division)',
    description: 'Up & Down main crossover with multi-aspect color light home signal gantry.',
    entities: [
      { id: 'asv3_1', label: 'Home Signal S1', type: 'Running_Signal', conf: '66.8%', confidence_raw: 0.67, x: 1124, y: 74, width: 47, height: 284, xyxy: [1124, 74, 1171, 358] },
      { id: 'asv3_2', label: 'Routing Home S2', type: 'Running_Signal', conf: '51.7%', confidence_raw: 0.52, x: 848, y: 76, width: 49, height: 273, xyxy: [848, 76, 897, 349] },
      { id: 'asv3_3', label: 'Point 101A (Facing)', type: 'Point_Turnout', conf: '46.2%', confidence_raw: 0.46, x: 1248, y: 675, width: 32, height: 31, xyxy: [1248, 675, 1280, 706] },
      { id: 'asv3_4', label: 'Point 101B (Trailing)', type: 'Point_Turnout', conf: '45.2%', confidence_raw: 0.45, x: 1252, y: 701, width: 28, height: 33, xyxy: [1252, 701, 1280, 734] },
      { id: 'asv3_5', label: 'Loop Starter S3', type: 'Running_Signal', conf: '43.3%', confidence_raw: 0.43, x: 833, y: 425, width: 58, height: 62, xyxy: [833, 425, 891, 487] },
    ],
  },
  {
    filename: '5-4192_2B_ASARVA_SIP_VPP__tile_013.png',
    url: '/drawings/5-4192_2B_ASARVA_SIP_VPP__tile_013.png',
    title: 'Asarva Junction SIP — Sheet 13 (Through Signals)',
    station: 'Asarva (ASV)',
    zone: 'Western Railway (Ahmedabad Division)',
    description: 'Intermediate block section and automatic signals along main lines.',
    entities: [
      { id: 'asv13_1', label: 'Auto Signal A10', type: 'Running_Signal', conf: '59.2%', confidence_raw: 0.59, x: 878, y: 70, width: 51, height: 390, xyxy: [878, 70, 929, 460] },
      { id: 'asv13_2', label: 'Auto Signal A12', type: 'Running_Signal', conf: '56.9%', confidence_raw: 0.57, x: 286, y: 73, width: 51, height: 381, xyxy: [286, 73, 337, 454] },
      { id: 'asv13_3', label: 'Repeater Signal R1', type: 'Running_Signal', conf: '55.4%', confidence_raw: 0.55, x: 646, y: 78, width: 48, height: 375, xyxy: [646, 78, 694, 453] },
      { id: 'asv13_4', label: 'Auto Signal A14', type: 'Running_Signal', conf: '50.3%', confidence_raw: 0.50, x: 159, y: 69, width: 47, height: 390, xyxy: [159, 69, 206, 459] },
      { id: 'asv13_5', label: 'Auto Signal A16', type: 'Running_Signal', conf: '48.2%', confidence_raw: 0.48, x: 350, y: 73, width: 44, height: 386, xyxy: [350, 73, 394, 459] },
    ],
  },
  {
    filename: '5-4192_2B_ASARVA_SIP_VPP__tile_024.png',
    url: '/drawings/5-4192_2B_ASARVA_SIP_VPP__tile_024.png',
    title: 'Asarva Junction SIP — Sheet 24 (Facing Point Lock Switches)',
    station: 'Asarva (ASV)',
    zone: 'Western Railway (Ahmedabad Division)',
    description: 'Motor operated point machines with Facing Point Lock (FPL) and track isolation.',
    entities: [
      { id: 'asv24_1', label: 'Point Turnout 104', type: 'Point_Turnout', conf: '58.3%', confidence_raw: 0.58, x: 1248, y: 675, width: 32, height: 31, xyxy: [1248, 675, 1280, 706] },
      { id: 'asv24_2', label: 'Point Turnout 106', type: 'Point_Turnout', conf: '37.5%', confidence_raw: 0.38, x: 920, y: 710, width: 45, height: 38, xyxy: [920, 710, 965, 748] },
      { id: 'asv24_3', label: 'Trap Point T1', type: 'Point_Turnout', conf: '31.8%', confidence_raw: 0.32, x: 610, y: 690, width: 38, height: 35, xyxy: [610, 690, 648, 725] },
      { id: 'asv24_4', label: 'Calling-On C4', type: 'Running_Signal', conf: '28.6%', confidence_raw: 0.29, x: 740, y: 430, width: 42, height: 50, xyxy: [740, 430, 782, 480] },
    ],
  },
];

export default function DrawingViewerPage() {
  const [selectedDrawingIndex, setSelectedDrawingIndex] = useState(0);
  const [zoom, setZoom] = useState(100);
  const [showOverlays, setShowOverlays] = useState(true);
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);

  const currentDrawing = REAL_DRAWINGS[selectedDrawingIndex];

  // Helper color map for classes
  const getBadgeClass = (type: string) => {
    switch (type) {
      case 'Platform':
        return 'border-blue-500 bg-blue-500/20 text-blue-900 text-blue-300';
      case 'Running_Signal':
        return 'border-emerald-500 bg-emerald-500/20 text-emerald-900 text-emerald-300';
      case 'Point_Turnout':
        return 'border-amber-500 bg-amber-500/20 text-amber-900 text-amber-300';
      default:
        return 'border-purple-500 bg-purple-500/20 text-purple-900 text-purple-300';
    }
  };

  const getCardBorder = (type: string) => {
    switch (type) {
      case 'Platform':
        return 'border-blue-300 bg-blue-50/50';
      case 'Running_Signal':
        return 'border-emerald-300 bg-emerald-50/50';
      case 'Point_Turnout':
        return 'border-amber-300 bg-amber-50/50';
      default:
        return 'border-purple-300 bg-purple-50/50';
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-4 max-w-7xl mx-auto">
      {/* Top Controls Bar */}
      <div className="bg-white border border-slate-200 rounded-xl px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shadow-sm">
        {/* Drawing Selector Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-800">Real SIP Drawing:</span>
          <select
            value={selectedDrawingIndex}
            onChange={(e) => {
              setSelectedDrawingIndex(Number(e.target.value));
              setSelectedEntityId(null);
            }}
            className="text-xs font-semibold text-slate-900 bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
          >
            {REAL_DRAWINGS.map((d, idx) => (
              <option key={d.filename} value={idx}>
                {d.title} ({d.station})
              </option>
            ))}
          </select>
          <span className="text-[11px] text-slate-500 hidden md:inline">
            • {currentDrawing.zone}
          </span>
        </div>

        {/* View Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              showOverlays
                ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm'
                : 'bg-slate-50 border-slate-200 text-slate-600'
            }`}
          >
            <Tag className="w-3.5 h-3.5" />
            {showOverlays ? 'Hide AI Overlays' : 'Show AI Overlays'}
          </button>

          <div className="h-4 w-px bg-slate-200 mx-1"></div>

          <button
            onClick={() => setZoom(Math.max(50, zoom - 15))}
            className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-600 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono font-semibold text-slate-700 w-12 text-center">
            {zoom}%
          </span>
          <button
            onClick={() => setZoom(Math.min(250, zoom + 15))}
            className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-600 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(100)}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 px-2 py-1 hover:bg-slate-100 rounded"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Main Canvas Area + Inspector Sidebar */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* Canvas Display */}
        <div className="flex-1 bg-slate-900 rounded-xl overflow-auto border border-slate-800 relative flex items-center justify-center p-6 shadow-inner">
          <div
            className="relative transition-all duration-150 shadow-2xl select-none"
            style={{
              width: `${1280 * (zoom / 100)}px`,
              height: `${1280 * (zoom / 100)}px`,
            }}
          >
            {/* Real Drawing Image */}
            <img
              src={currentDrawing.url}
              alt={currentDrawing.title}
              className="w-full h-full object-contain rounded bg-white"
            />

            {/* AI Bounding Box Overlays */}
            {showOverlays &&
              currentDrawing.entities.map((ent) => {
                const isSelected = selectedEntityId === ent.id;
                // Calculate percentage relative to 1280x1280 image
                const left = (ent.x / 1280) * 100;
                const top = (ent.y / 1280) * 100;
                const width = Math.max((ent.width / 1280) * 100, 2.5);
                const height = Math.max((ent.height / 1280) * 100, 2.5);

                return (
                  <div
                    key={ent.id}
                    onClick={() => setSelectedEntityId(ent.id)}
                    className={`absolute border-2 cursor-pointer transition-all ${
                      isSelected
                        ? 'border-yellow-400 bg-yellow-400/30 ring-4 ring-yellow-400/50 z-20'
                        : ent.type === 'Platform'
                        ? 'border-blue-500 bg-blue-500/15 hover:bg-blue-500/30 z-10'
                        : ent.type === 'Point_Turnout'
                        ? 'border-amber-500 bg-amber-500/15 hover:bg-amber-500/30 z-10'
                        : 'border-emerald-500 bg-emerald-500/15 hover:bg-emerald-500/30 z-10'
                    }`}
                    style={{
                      left: `${left}%`,
                      top: `${top}%`,
                      width: `${width}%`,
                      height: `${height}%`,
                    }}
                  >
                    {/* Floating Label */}
                    <div className="absolute -top-5 left-0 whitespace-nowrap bg-slate-900/90 text-white px-1.5 py-0.5 rounded text-[9px] font-mono font-bold shadow-md flex items-center gap-1">
                      <span>{ent.label}</span>
                      <span className="text-emerald-400">({ent.conf})</span>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Entity Inspector Panel */}
        <div className="w-80 bg-white border border-slate-200 rounded-xl p-4 flex flex-col shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              Detected Equipment ({currentDrawing.entities.length})
            </h2>
            <span className="text-[10px] bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-bold">
              YOLO11 GPU
            </span>
          </div>

          <p className="text-[11px] text-slate-500 mt-2 mb-3 leading-tight">
            {currentDrawing.description}
          </p>

          <div className="space-y-2.5 flex-1 overflow-y-auto pr-1">
            {currentDrawing.entities.map((ent) => {
              const isSelected = selectedEntityId === ent.id;
              return (
                <div
                  key={ent.id}
                  onClick={() => setSelectedEntityId(ent.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all text-xs ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500 shadow-sm'
                      : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/70'
                  }`}
                >
                  <div className="flex items-center justify-between font-bold text-slate-900">
                    <span>{ent.label}</span>
                    <span className="text-emerald-600 text-[11px] font-mono bg-emerald-50 px-1.5 py-0.5 rounded">
                      {ent.conf}
                    </span>
                  </div>

                  <div className="mt-1 flex items-center justify-between text-[11px] text-slate-600">
                    <span className="font-semibold text-slate-700">{ent.type}</span>
                    <span className="font-mono text-[10px] text-slate-400">
                      [{ent.x}, {ent.y}]
                    </span>
                  </div>

                  {isSelected && (
                    <div className="mt-2 pt-2 border-t border-blue-200/60 text-[11px] text-slate-600 space-y-1 animate-in fade-in duration-100">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Bounding Box:</span>
                        <span className="font-mono text-[10px] text-slate-700">
                          {ent.width}px × {ent.height}px
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Interlocking Ref:</span>
                        <span className="font-semibold text-blue-700">IRS-S 36 Clause 4.2</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Model Meta Footer */}
          <div className="pt-3 mt-2 border-t border-slate-100 text-[10px] text-slate-400 flex items-center justify-between">
            <span>Model: yolo_sip_best.pt (800px)</span>
            <span className="font-semibold text-emerald-600">Conf: 78.0% max</span>
          </div>
        </div>
      </div>
    </div>
  );
}
