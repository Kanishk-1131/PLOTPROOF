'use client';

import React from 'react';
import Link from 'next/link';
import { 
  ShieldCheck, 
  MapPin, 
  Lock, 
  FileText, 
  ArrowRight, 
  AlertTriangle, 
  CheckCircle2, 
  Cpu, 
  QrCode, 
  Layers, 
  Sparkles,
  Search,
  ExternalLink
} from 'lucide-react';

export default function HomePage() {
  const modules = [
    {
      id: 'A',
      title: 'Module A — Document Intelligence',
      icon: FileText,
      tech: 'OpenCV + OCR + Regex Rules',
      desc: 'Preprocesses legacy deeds (denoise, deskew, Otsu binarization), extracts survey numbers, boundaries, district, taluk, and extent.',
      color: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400',
    },
    {
      id: 'B',
      title: 'Module B — GIS Intelligence',
      icon: MapPin,
      tech: 'Cadastral DB + PostGIS / Shapely',
      desc: 'Reconstructs parcel polygon, runs topological ST_Intersects & ST_Overlaps queries against cadastral layers, and flags collisions in real-time.',
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400',
    },
    {
      id: 'C',
      title: 'Module C — Trust & Tamper Detection',
      icon: Lock,
      tech: 'Canonical JSON + SHA-256 + Smart Contract',
      desc: 'Calculates cryptographic document fingerprint. Detects modified areas or altered terms via instant on-chain hash mismatch alerts.',
      color: 'from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400',
    },
    {
      id: 'D',
      title: 'Module D — Privacy (ZK & PII Minimization)',
      icon: ShieldCheck,
      tech: 'Pedersen Commitments + PII Masking',
      desc: 'Proves titleholder validity without leaking citizen Aadhaar, personal phone, or private citizen information to unauthorized parties.',
      color: 'from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400',
    },
  ];

  return (
    <div className="space-y-16 pb-12">
      
      {/* Hero Section */}
      <section className="relative pt-8 pb-12 text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-xs font-semibold text-emerald-400">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Smart India Hackathon MVP Architecture</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Cryptographically Tamper-Evident <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
            Land Title & Cadastral Verification
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
          PlotProof transforms 20-year-old scanned land deeds into verified digital assets, reconstructs boundary polygons, flags spatial boundary collisions, and registers tamper-evident proofs on-chain.
        </p>

        {/* Demo Quick Launchers */}
        <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/upload"
            className="flex items-center space-x-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-bold shadow-xl shadow-emerald-500/25 transition-all duration-200 hover:scale-[1.02] active:scale-95"
          >
            <span>Start Live Verification</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center space-x-2 px-6 py-3.5 rounded-xl glass-panel hover:bg-slate-800/80 text-slate-200 font-semibold border border-slate-700 transition-all duration-200"
          >
            <Layers className="w-5 h-5 text-emerald-400" />
            <span>Open Command Center</span>
          </Link>
        </div>
      </section>

      {/* 3 Killer Demo Scenarios Bar */}
      <section className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-emerald-400" />
              <span>Demonstration Scenarios</span>
            </h2>
            <p className="text-xs text-slate-400">Pre-calibrated test cases showing the multi-vector verification engine in action</p>
          </div>
          <span className="text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
            Cadastral Cluster: Selaiyur, Tambaram (Survey 142)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          
          {/* Demo 1 */}
          <Link
            href="/upload?preset=genuine"
            className="group glass-card p-5 rounded-xl border border-emerald-500/30 hover:border-emerald-400 transition-all duration-200 hover:shadow-lg hover:shadow-emerald-500/10 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">DEMO 1 (DEFAULT)</span>
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              </div>
              <h3 className="font-bold text-white text-base group-hover:text-emerald-300 transition-colors">Default Genuine Title Deed</h3>
              <p className="text-xs text-slate-400 mt-1.5">
                Clean Deed for Survey 142/3A (2,400 sq.ft, Selaiyur). Reconstructs boundary, validates zero overlap, verifies SHA-256 fingerprint, and generates verifiable QR Certificate.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-emerald-400">
              <span>Expected: ✓ VERIFIED (100%)</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          {/* Demo 2 */}
          <Link
            href="/upload?preset=review_required"
            className="group glass-card p-5 rounded-xl border border-amber-500/30 hover:border-amber-400 transition-all duration-200 hover:shadow-lg hover:shadow-amber-500/10 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">DEMO 2 (AUTHORITY REVIEW)</span>
                <AlertTriangle className="w-5 h-5 text-amber-400" />
              </div>
              <h3 className="font-bold text-white text-base group-hover:text-amber-300 transition-colors">Authority Review Required Deed</h3>
              <p className="text-xs text-slate-400 mt-1.5">
                Deed for Survey 142/3B overlapping Survey 142/3A by 17.8 sq.m. Triggers Sub-Registrar statutory review gate with full reason & authority approval override.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-amber-300">
              <span>Expected: ⚠ REVIEW REQUIRED</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          {/* Demo 3 */}
          <Link
            href="/upload?preset=tampered"
            className="group glass-card p-5 rounded-xl border border-purple-500/30 hover:border-purple-400 transition-all duration-200 hover:shadow-lg hover:shadow-purple-500/10 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40">DEMO 3</span>
                <Lock className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="font-bold text-white text-base group-hover:text-purple-300 transition-colors">Tampered Deed (Forged Area)</h3>
              <p className="text-xs text-slate-400 mt-1.5">
                Deed with modified area (2400 &rarr; 3400 sq.ft). Verification engine calculates canonical hash mismatch and triggers instant cryptographic tampering alert.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-purple-300">
              <span>Expected: ⚠ TAMPER ALERT</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

        </div>
      </section>

      {/* 4 Architecture Modules */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-white">4 Core Engineering Pillars</h2>
          <p className="text-sm text-slate-400 mt-1">Modular full-stack pipeline built with Python, PostGIS, Web3, and Next.js</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {modules.map((m) => {
            const Icon = m.icon;
            return (
              <div key={m.id} className={`glass-panel p-6 rounded-xl border bg-gradient-to-b ${m.color} flex flex-col justify-between`}>
                <div>
                  <div className="w-10 h-10 rounded-lg bg-slate-900/80 border border-slate-700/60 flex items-center justify-center mb-4">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-mono uppercase tracking-wider font-semibold opacity-80">Pillar {m.id}</span>
                  <h3 className="font-bold text-white text-base mt-1">{m.title}</h3>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">{m.desc}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800/60 text-[11px] font-mono text-slate-400">
                  {m.tech}
                </div>
              </div>
            );
          })}
        </div>
      </section>

    </div>
  );
}
