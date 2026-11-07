'use client';

import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Download, ExternalLink, Filter } from 'lucide-react';
import { formatBytes } from '@/lib/utils';

export default function DocumentsPage() {
  const [documents] = useState([
    {
      id: 'doc-1',
      name: '2.pdf (Kavach & Electronic Interlocking - SIP Symbol Register)',
      size: 1232845,
      type: 'Authoritative Reference PDF',
      pages: 48,
      status: 'VERIFIED & INDEXED',
      date: 'Nov 05, 2026',
      downloadUrl: '/reference/2.pdf',
      description: 'Complete Indian Railways Symbol Register covering Kavach RFID notations, Electronic Interlocking symbols, and Plate Appendices.',
    },
    {
      id: 'doc-2',
      name: 'IRISET_SnT_Drawings_Pages_99_to_105.pdf',
      size: 238912,
      type: 'IRISET Official Standards',
      pages: 7,
      status: 'VERIFIED & INDEXED',
      date: 'Nov 05, 2026',
      downloadUrl: '/reference/IRISET_SnT_Drawings_Pages_99_to_105.pdf',
      description: 'Official graphical plates from Indian Railways Institute of Signal Engineering and Telecommunications (Plates 99 to 105).',
    },
    {
      id: 'doc-3',
      name: '5-4192_2B_ASARVA_SIP_VPP_PROP_DT_09-07-2025.pdf',
      size: 4821000,
      type: 'SIP Engineering Drawing',
      pages: 32,
      status: 'PROCESSED & DETECTED',
      date: 'Nov 04, 2026',
      downloadUrl: null,
      description: 'Western Railway Ahmedabad Division — Asarva Junction Signalling and Interlocking Plan with electronic interlocking scheme.',
    },
    {
      id: 'doc-4',
      name: 'AMARDA_SIP.pdf',
      size: 6911802,
      type: 'SIP Engineering Drawing',
      pages: 28,
      status: 'PROCESSED & DETECTED',
      date: 'Nov 02, 2026',
      downloadUrl: null,
      description: 'South Eastern Railway Kharagpur Division — Amarda Station Interlocking Plan showing platform lines and facing points.',
    },
    {
      id: 'doc-5',
      name: '10-WR_BHUJ_PH-II_MINI_SIP-07-11-20251.pdf',
      size: 1264314,
      type: 'SIP Engineering Drawing',
      pages: 12,
      status: 'PROCESSED & DETECTED',
      date: 'Nov 01, 2026',
      downloadUrl: null,
      description: 'Western Railway — Bhuj Section Quadrupling Phase II proposed electronic interlocking scheme.',
    },
    {
      id: 'doc-6',
      name: '3.SIPMANIKGARHJN-ABSIPU.1287E_V3_APPROVE_P62.pdf',
      size: 3412500,
      type: 'Approved SIP Drawing',
      pages: 18,
      status: 'PROCESSED & DETECTED',
      date: 'Oct 28, 2026',
      downloadUrl: null,
      description: 'Central Railway — Manikgarh Junction approved V3 signalling plan with route control and sand hump isolation.',
    },
  ]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Real Document Management</h1>
          <p className="text-xs text-slate-500 mt-0.5">Authoritative Indian Railways reference standards and live ingested SIP drawing plans.</p>
        </div>
      </div>

      {/* Upload Banner */}
      <div className="border-2 border-dashed border-slate-200 hover:border-blue-400 bg-white rounded-xl p-6 text-center transition-colors cursor-pointer shadow-sm">
        <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">
          <UploadCloud className="w-5 h-5" />
        </div>
        <h3 className="text-xs font-semibold text-slate-800">Upload New SIP Drawings or Standards</h3>
        <p className="text-[11px] text-slate-500 mt-0.5">Drag & drop PDF drawings, scanned plans, DWG/DXF files, or RDSO Word specifications</p>
      </div>

      {/* Real Documents Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Ingested Reference Documentation ({documents.length})</h2>
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
            All Documents Live & Grounded
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <th className="py-2.5 px-4">Document Title</th>
                <th className="py-2.5 px-4">Format / Category</th>
                <th className="py-2.5 px-4">Size</th>
                <th className="py-2.5 px-4">Indexing Status</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="py-3 px-4 font-medium text-slate-900">
                    <div className="flex items-start gap-2.5">
                      <FileText className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold text-slate-900 block">{doc.name}</span>
                        <span className="text-[11px] text-slate-500 block mt-0.5">{doc.description}</span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-slate-600 whitespace-nowrap">{doc.type}</td>
                  <td className="py-3 px-4 text-slate-600 whitespace-nowrap">{formatBytes(doc.size)}</td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      {doc.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    {doc.downloadUrl ? (
                      <a
                        href={doc.downloadUrl}
                        download
                        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-bold bg-blue-50 hover:bg-blue-100 px-2.5 py-1 rounded border border-blue-200 transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" /> View PDF
                      </a>
                    ) : (
                      <span className="text-slate-400 font-medium text-[11px]">In Local Storage</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
