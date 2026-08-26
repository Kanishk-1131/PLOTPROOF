'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Sparkles, 
  ShieldCheck, 
  MapPin, 
  Lock, 
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import { apiService, UploadResponse } from '@/services/api';

function UploadContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const presetParam = searchParams.get('preset');

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<string | null>(presetParam || null);
  const [uploadData, setUploadData] = useState<UploadResponse | null>(null);
  
  const [isVerifying, setIsVerifying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const steps = [
    { title: 'Document Ingestion', desc: 'Secure hash initialization & file hashing' },
    { title: 'Image Preprocessing', desc: 'OpenCV deskew, noise reduction, & Otsu binarization' },
    { title: 'OCR Extraction', desc: 'Document layout analysis & domain regex rule parsing' },
    { title: 'Spatial GIS Verification', desc: 'Topological intersection & cadastral overlap detection' },
    { title: 'Trust & Blockchain Anchoring', desc: 'Canonical SHA-256 comparison & smart contract lookup' },
    { title: 'Certificate Generation', desc: 'Issuing verifiable certificate & QR code' },
  ];

  useEffect(() => {
    if (presetParam) {
      setSelectedPreset(presetParam);
    }
  }, [presetParam]);

  const handlePresetSelect = (preset: string) => {
    setSelectedPreset(preset);
    setSelectedFile(null);
    setErrorMsg(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setSelectedPreset(null);
      setErrorMsg(null);
    }
  };

  const handleRunVerification = async () => {
    if (!selectedFile && !selectedPreset) {
      setErrorMsg('Please select a sample preset deed or upload a deed file to proceed.');
      return;
    }

    try {
      setIsVerifying(true);
      setErrorMsg(null);
      setCurrentStep(0);

      // Step 1: Upload
      const uploadRes = await apiService.uploadDocument(
        selectedFile || undefined,
        selectedPreset || undefined
      );
      setUploadData(uploadRes);
      setCurrentStep(1);

      // Animate progress through the pipeline stages for high-impact live demo
      await new Promise((r) => setTimeout(r, 600));
      setCurrentStep(2); // Preprocessing
      await new Promise((r) => setTimeout(r, 700));
      setCurrentStep(3); // OCR
      await new Promise((r) => setTimeout(r, 800));
      setCurrentStep(4); // GIS
      await new Promise((r) => setTimeout(r, 700));
      setCurrentStep(5); // Blockchain & Certificate

      // Execute full verification engine on backend
      const result = await apiService.startVerification(uploadRes.document_id);
      
      setCurrentStep(6);
      await new Promise((r) => setTimeout(r, 600));

      // Navigate to forensic report
      router.push(`/verification/${result.verification_id}`);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'An error occurred during verification.');
      setIsVerifying(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-mono text-emerald-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>MULTI-VECTOR FORENSIC ENGINE</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white">Upload Land Title Deed</h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Submit a scanned conveyance deed or select a pre-calibrated demo scenario to run automated OCR extraction, cadastral boundary overlap checks, and on-chain tamper detection.
        </p>
      </div>

      {/* 3 Demo Preset Quick Selectors */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>1-Click Demonstration Presets</span>
          </h2>
          <span className="text-[11px] font-mono text-slate-400">Instant Test Cases</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          
          {/* Preset 1 */}
          <button
            type="button"
            onClick={() => handlePresetSelect('genuine')}
            className={`p-4 rounded-xl border text-left transition-all duration-150 flex flex-col justify-between ${
              selectedPreset === 'genuine'
                ? 'bg-emerald-950/40 border-emerald-400 shadow-lg shadow-emerald-500/15'
                : 'glass-card border-slate-800 hover:border-slate-700'
            }`}
          >
            <div>
              <span className="text-[10px] font-mono font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                CASE 1
              </span>
              <h3 className="font-bold text-white text-sm mt-2">Genuine Deed</h3>
              <p className="text-xs text-slate-400 mt-1">Survey 142/3A (2400 sq.ft) • 0 Collisions</p>
            </div>
            <div className="mt-3 text-[11px] font-semibold text-emerald-400">✓ Passes all checks</div>
          </button>

          {/* Preset 2 */}
          <button
            type="button"
            onClick={() => handlePresetSelect('tampered')}
            className={`p-4 rounded-xl border text-left transition-all duration-150 flex flex-col justify-between ${
              selectedPreset === 'tampered'
                ? 'bg-purple-950/40 border-purple-400 shadow-lg shadow-purple-500/15'
                : 'glass-card border-slate-800 hover:border-slate-700'
            }`}
          >
            <div>
              <span className="text-[10px] font-mono font-bold text-purple-300 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
                CASE 2
              </span>
              <h3 className="font-bold text-white text-sm mt-2">Tampered Deed</h3>
              <p className="text-xs text-slate-400 mt-1">Area Forged: 2400 &rarr; 3400 sq.ft</p>
            </div>
            <div className="mt-3 text-[11px] font-semibold text-purple-300">⚠ Hash Mismatch Alert</div>
          </button>

          {/* Preset 3 */}
          <button
            type="button"
            onClick={() => handlePresetSelect('collision')}
            className={`p-4 rounded-xl border text-left transition-all duration-150 flex flex-col justify-between ${
              selectedPreset === 'collision'
                ? 'bg-red-950/40 border-red-400 shadow-lg shadow-red-500/15'
                : 'glass-card border-slate-800 hover:border-slate-700'
            }`}
          >
            <div>
              <span className="text-[10px] font-mono font-bold text-red-400 px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20">
                CASE 3
              </span>
              <h3 className="font-bold text-white text-sm mt-2">Spatial Collision</h3>
              <p className="text-xs text-slate-400 mt-1">Survey 142/3B Overlaps by 17.8 m²</p>
            </div>
            <div className="mt-3 text-[11px] font-semibold text-red-400">⚠ GIS Overlap Alert</div>
          </button>

        </div>
      </div>

      {/* File Upload Zone */}
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center space-y-4 relative">
        <input
          type="file"
          id="deed-upload"
          accept=".pdf,.png,.jpg,.jpeg,.txt"
          onChange={handleFileChange}
          className="hidden"
          disabled={isVerifying}
        />
        <label
          htmlFor="deed-upload"
          className="cursor-pointer block border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-8 transition-colors bg-slate-900/40 hover:bg-slate-900/70"
        >
          <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center mx-auto mb-3 text-slate-400 group-hover:text-emerald-400">
            <UploadCloud className="w-7 h-7 text-emerald-400" />
          </div>
          <h3 className="text-base font-bold text-white">
            {selectedFile ? selectedFile.name : selectedPreset ? `Selected Preset: ${selectedPreset.toUpperCase()}` : 'Drag & drop land deed or browse'}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Supports PDF, JPG, PNG, TIFF, or plain text deeds (Max 25MB)
          </p>
        </label>

        {errorMsg && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center justify-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Submit Verification Button */}
        <button
          type="button"
          onClick={handleRunVerification}
          disabled={isVerifying}
          className={`w-full py-4 rounded-xl font-bold text-sm tracking-wide text-white shadow-xl transition-all duration-200 flex items-center justify-center space-x-2 ${
            isVerifying
              ? 'bg-slate-800 cursor-not-allowed opacity-80'
              : 'bg-gradient-to-r from-emerald-600 via-teal-500 to-emerald-500 hover:from-emerald-500 hover:to-teal-400 shadow-emerald-600/25 active:scale-[0.99]'
          }`}
        >
          {isVerifying ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Running Multi-Vector Forensic Audit...</span>
            </>
          ) : (
            <>
              <span>Run Automated Verification Pipeline</span>
              <ArrowRight className="w-5 h-5 ml-1" />
            </>
          )}
        </button>
      </div>

      {/* Live 6-Stage Progress Stepper Modal / Panel */}
      {isVerifying && (
        <div className="glass-panel p-6 rounded-2xl border border-emerald-500/40 shadow-2xl bg-slate-950/90 space-y-5 animate-in fade-in duration-300">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 font-bold text-white text-sm">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              <span>Real-Time Forensic Pipeline Execution</span>
            </div>
            <span className="text-xs font-mono text-emerald-400">Step {currentStep} of 6</span>
          </div>

          <div className="space-y-3">
            {steps.map((step, idx) => {
              const isDone = currentStep > idx + 1;
              const isCurrent = currentStep === idx + 1;
              const isWaiting = currentStep < idx + 1;

              return (
                <div
                  key={idx}
                  className={`flex items-start space-x-3 p-3 rounded-lg border transition-all duration-200 ${
                    isDone
                      ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                      : isCurrent
                      ? 'bg-slate-800/80 border-emerald-400 text-white shadow-md'
                      : 'bg-slate-900/30 border-slate-800/60 text-slate-500'
                  }`}
                >
                  <div className="mt-0.5">
                    {isDone ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    ) : isCurrent ? (
                      <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-slate-700 flex items-center justify-center text-[10px] font-mono">
                        {idx + 1}
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-xs flex items-center justify-between">
                      <span>{step.title}</span>
                      {isDone && <span className="text-[10px] font-mono text-emerald-400">COMPLETED</span>}
                      {isCurrent && <span className="text-[10px] font-mono text-amber-400 animate-pulse">PROCESSING</span>}
                    </div>
                    <p className="text-[11px] text-slate-400 mt-0.5">{step.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
}

export default function UploadPage() {
  return (
    <Suspense fallback={
      <div className="min-h-[50vh] flex items-center justify-center text-slate-500 font-mono text-xs">
        Loading Upload Portal...
      </div>
    }>
      <UploadContent />
    </Suspense>
  );
}
