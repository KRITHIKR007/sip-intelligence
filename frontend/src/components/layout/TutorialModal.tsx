'use client';

import React, { useState, useEffect } from 'react';
import {
  X,
  ChevronRight,
  ChevronLeft,
  Eye,
  Sparkles,
  ShieldCheck,
  MessageSquare,
  GitCompare,
  Compass,
  CheckCircle2,
  FileText,
} from 'lucide-react';
import Link from 'next/link';

interface TutorialStep {
  title: string;
  badge: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  keyPoints: string[];
  actionLabel: string;
  actionHref: string;
}

const STEPS: TutorialStep[] = [
  {
    title: 'Welcome to SIP Intelligence Platform',
    badge: 'Overview',
    icon: Compass,
    description:
      'A specialized enterprise multimodal intelligence platform designed for Indian Railways Signalling & Telecommunication (S&T), Signalling and Interlocking Plans (SIP), Electronic Interlocking (EI), and Kavach automatic train protection.',
    keyPoints: [
      'Open Model Mode: Instant access without sign-up or registration barriers.',
      'Trained on real Indian Railways SIP plans and IRISET authoritative plates.',
      'Local private AI running on your dedicated hardware (NVIDIA CUDA GPU).',
    ],
    actionLabel: 'Explore Dashboard',
    actionHref: '/',
  },
  {
    title: 'Interactive SIP Drawing Viewer',
    badge: 'Drawing Viewer',
    icon: Eye,
    description:
      'Inspect high-resolution railway signalling drawings with pixel-precise AI detection overlays powered by our fine-tuned YOLO11 model.',
    keyPoints: [
      'Switch between real SIP drawings (Asarva Jn, Amarda Yard, Bhuj Quadrupling).',
      'Toggle AI Bounding Boxes to see Running Signals, Point Turnouts, Track Circuits, and Platforms.',
      'Inspect entity confidence scores, pixel coordinates, and interlocking chainage.',
      'Smooth zoom controls from 50% to 250% magnification.',
    ],
    actionLabel: 'Launch Drawing Viewer',
    actionHref: '/viewer',
  },
  {
    title: '56-Class IRISET Symbol Explorer',
    badge: 'Symbol Taxonomy',
    icon: Sparkles,
    description:
      'Standardized visual catalogue matching official IRISET Plates 99 to 105 and Kavach RFID / Electronic Interlocking registers.',
    keyPoints: [
      '56 real extracted symbol images with high-resolution crops.',
      'Filter by category: Running Signals, Shunt Signals, Track Circuits, Points, and Boards.',
      'Direct cross-reference to Indian Railways Signal Engineering Manual (SEM).',
      'Inspect symbol geometry, aspect ratios, and functional criticalities.',
    ],
    actionLabel: 'Open Symbol Explorer',
    actionHref: '/symbols',
  },
  {
    title: 'Grounded Railway Engineering Assistant',
    badge: 'Multimodal RAG',
    icon: MessageSquare,
    description:
      'Ask engineering questions grounded in authentic reference manuals (2.pdf Symbol Register, Kavach SPN/196, and IRISET standard drawings).',
    keyPoints: [
      'Ask about Kavach RFID tag positioning rules (50m ± 5m from signals).',
      'Look up Signal Overlap (180m) and Block Overlap safety margins.',
      'Every answer is strictly grounded with verifiable page citations.',
      'Zero AI hallucinations — source evidence is always displayed.',
    ],
    actionLabel: 'Ask Engineering Assistant',
    actionHref: '/assistant',
  },
  {
    title: 'Standards Validation & Revision Comparison',
    badge: 'Rule Engine & Diff',
    icon: ShieldCheck,
    description:
      'Validate signalling plans against codified Indian Railways safety standards and track topological changes across drawing revisions.',
    keyPoints: [
      'Automated rule checking against SEM Part II and RDSO specifications.',
      'Identify missing isolation traps, signal overlap errors, and fouling mark hazards.',
      'Compare revision states (e.g. Bhuj Phase I vs Phase II) with topological differencing.',
      'Export audit-ready engineering compliance reports.',
    ],
    actionLabel: 'View Validation Rules',
    actionHref: '/validation',
  },
];

export function TutorialModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [currentStep, setCurrentStep] = useState(0);

  if (!isOpen) return null;

  const step = STEPS[currentStep];
  const Icon = step.icon;

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-xl w-full border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Top Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse"></span>
            <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Platform Tutorial & Quickstart
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
            title="Close Tutorial"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Step Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
              {step.badge}
            </span>
            <span className="text-xs font-medium text-slate-400">
              Step {currentStep + 1} of {STEPS.length}
            </span>
          </div>

          <div className="flex items-start gap-4 pt-1">
            <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0 shadow-md">
              <Icon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                {step.title}
              </h2>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                {step.description}
              </p>
            </div>
          </div>

          {/* Key Capabilities */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 space-y-2 mt-4">
            <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wide">
              Key Capabilities:
            </p>
            <ul className="space-y-1.5">
              {step.keyPoints.map((point, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-600">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          {/* Progress dots */}
          <div className="flex items-center gap-1.5">
            {STEPS.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentStep(i)}
                className={`h-1.5 rounded-full transition-all ${
                  i === currentStep ? 'w-6 bg-blue-600' : 'w-2 bg-slate-300'
                }`}
                title={`Go to step ${i + 1}`}
              />
            ))}
          </div>

          <div className="flex items-center gap-2">
            {currentStep > 0 && (
              <button
                onClick={handlePrev}
                className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg flex items-center gap-1 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" /> Back
              </button>
            )}

            <Link
              href={step.actionHref}
              onClick={onClose}
              className="px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors"
            >
              {step.actionLabel}
            </Link>

            <button
              onClick={handleNext}
              className="px-4 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-1 shadow-sm transition-colors"
            >
              {currentStep === STEPS.length - 1 ? (
                'Finish Tour'
              ) : (
                <>
                  Next <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

