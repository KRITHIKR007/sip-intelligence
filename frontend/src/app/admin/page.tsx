'use client';

import React from 'react';
import { Cpu, Database, CheckCircle2, ShieldCheck, Zap } from 'lucide-react';

export default function AdminPage() {
  const models = [
    {
      name: 'YOLO11n Symbol Detector',
      type: 'Computer Vision Object Detection',
      weights: 'ml/weights/yolo_sip_best.pt (6.23 MB)',
      inputSize: '800 × 800 px',
      device: 'NVIDIA RTX 3050 Laptop GPU (CUDA 12.4)',
      metrics: 'Overall mAP50: 0.249 | Platform: 62.2% | Running Signal: 50.8%',
      status: 'LOADED & ACTIVE',
    },
    {
      name: 'Seq2Vec Structural BiLSTM',
      type: 'Sequence-to-Vector Topology Encoder',
      weights: 'ml/weights/seq2vec_sip.pt (11.0 MB)',
      inputSize: 'Chainage Sequences ($X$-sorted)',
      device: 'PyTorch CUDA (256d L2 Normalized)',
      metrics: 'Contrastive Loss: 0.00025 | Invariant layout similarity: 1.000',
      status: 'LOADED & ACTIVE',
    },
    {
      name: 'Railway R-GCN Graph Model',
      type: 'Relational Graph Convolutional Network',
      weights: 'ml/weights/rgcn_sip.pt (859 KB)',
      inputSize: 'Interlocking Adjacency Subgraphs',
      device: 'PyTorch Geometric (256d Graph Pooling)',
      metrics: 'Smoothness Loss: 0.00166 | Node Feature Dim: 256d',
      status: 'LOADED & ACTIVE',
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Model Registry & GPU Hardware Engine</h1>
        <p className="text-xs text-slate-500 mt-0.5">Live local neural models, GPU execution context, and container database engine.</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {models.map((m, i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Cpu className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">{m.name}</h3>
                  <span className="text-[11px] text-slate-500">{m.type}</span>
                </div>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                {m.status}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs bg-slate-50 p-3.5 rounded-lg border border-slate-100">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Weights Path</span>
                <span className="font-mono text-[11px] text-slate-800 truncate block">{m.weights}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Resolution / Dimension</span>
                <span className="font-semibold text-slate-800">{m.inputSize}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Execution Device</span>
                <span className="font-semibold text-emerald-700">{m.device}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Performance Metrics</span>
                <span className="font-bold text-blue-700">{m.metrics}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
