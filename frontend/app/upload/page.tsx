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
  // Default to 'genuine' demo deed if no preset in query params
  const [selectedPreset, setSelectedPreset] = useState<string | null>(presetParam || 'genuine');
  const [uploadData, setUploadData] = useState<UploadResponse | null>(null);
  const [showInspector, setShowInspector] = useState(false);
  
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

  const handleResetToDefault = () => {
    setSelectedPreset('genuine');
    setSelectedFile(null);
    setErrorMsg(null);
  };

  const handleRunVerification = async () => {
    // If neither file nor preset is selected, automatically fallback to 'genuine'
    const effectivePreset = selectedFile ? undefined : (selectedPreset || 'genuine');

    try {
      setIsVerifying(true);
      setErrorMsg(null);
      setCurrentStep(0);

      // Step 1: Upload
      const uploadRes = await apiService.uploadDocument(
        selectedFile || undefined,
        effectivePreset
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

  const demoTextGenuine = `GOVERNMENT OF TAMIL NADU - REGISTRATION DEPARTMENT
TITLE DEED OF SALE / ABSOLUTE CONVEYANCE DEED
Document Registration Number: 4821/2024
Book 1, Volume 912, Pages 101 to 114
Sub-Registrar Office: Tambaram

DISTRICT: Chennai
TALUK: Tambaram
VILLAGE: Selaiyur Village
SURVEY NUMBER: 142/3A

EXTENT AND MEASUREMENT OF PROPERTY:
All that piece and parcel of land bearing Survey No: 142/3A, measuring an area of 2,400 Sq.ft (equivalent to 222.96 Sq.meters / 5.5 Cents).

BOUNDARIES:
North by: Survey No 142/2 (Road 30ft width)
South by: Survey No 142/4 (Vacant Plot)
East by: Survey No 142/3B (Adjacent Plot)
West by: Survey No 142/1 (Residential Property)

COORDINATES:
GPS Reference Bounds: 12.9249 N, 80.1472 E to 12.9255 N, 80.1478 E

PURCHASER / TITLE HOLDER:
Name: K. S. Ramanathan
Son of: Late K. Sundaram
Aadhaar UID: 5412-8823-8912

REGISTERED HASH COMMITMENT:
7c3e8f2c9a620d41e7845f096231ba4190284e91240185e2b028941785e091ad`;

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
          Submit a scanned conveyance deed or test with our pre-loaded default demonstration document to run automated OCR extraction, cadastral boundary overlap checks, and on-chain tamper detection.
        </p>
      </div>

      {/* Default Document Feature Banner */}
      <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-slate-900/60 to-teal-950/30 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/40">
                  DEFAULT DEMONSTRATION DOCUMENT
                </span>
                <span className="text-[11px] font-semibold text-slate-300">Ready to Test</span>
              </div>
              <h2 className="text-base font-bold text-white mt-0.5">
                Tamil Nadu Title Deed — Survey 142/3A, Selaiyur
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowInspector(!showInspector)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>{showInspector ? 'Hide Text' : 'Inspect Text'}</span>
            </button>
            <a
              href="/static/uploads/sample_default_deed.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 transition-colors flex items-center gap-1.5"
            >
              <span>Download PDF</span>
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800 text-xs">
          <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 font-mono block">SURVEY NO</span>
            <span className="font-bold text-emerald-400">142/3A</span>
          </div>
          <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 font-mono block">AREA EXTENT</span>
            <span className="font-bold text-slate-200">2,400 Sq.ft (222.96 m²)</span>
          </div>
          <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 font-mono block">LOCATION</span>
            <span className="font-bold text-slate-200">Selaiyur, Tambaram</span>
          </div>
          <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 font-mono block">INTEGRITY STATUS</span>
            <span className="font-bold text-emerald-400">✓ 100% Genuine Match</span>
          </div>
        </div>

        {/* Collapsible Deed Text Inspector */}
        {showInspector && (
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-[11px] text-slate-300 space-y-2 animate-in fade-in duration-200">
            <div className="flex items-center justify-between text-slate-500 text-[10px] border-b border-slate-800 pb-1">
              <span>RAW DEED STREAM (sample_genuine_142_3A.txt)</span>
              <span>SHA-256: 7c3e8f2c9a620d41...</span>
            </div>
            <pre className="whitespace-pre-wrap leading-relaxed overflow-x-auto text-slate-300 text-[11px]">
              {demoTextGenuine}
            </pre>
          </div>
        )}
      </div>

      {/* 3 Demo Preset Quick Selectors */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>Select Demonstration Scenario</span>
          </h2>
          <span className="text-[11px] font-mono text-slate-400">Instant Pre-calibrated Test Cases</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          
          {/* Preset 1 (Default: Genuine) */}
          <button
            type="button"
            onClick={() => handlePresetSelect('genuine')}
            className={`p-4 rounded-xl border text-left transition-all duration-150 flex flex-col justify-between ${
              selectedPreset === 'genuine'
                ? 'bg-emerald-950/40 border-emerald-400 shadow-lg shadow-emerald-500/15 ring-1 ring-emerald-400/50'
                : 'glass-card border-slate-800 hover:border-slate-700'
            }`}
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                  CASE 1 (DEFAULT)
                </span>
                {selectedPreset === 'genuine' && (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                )}
              </div>
              <h3 className="font-bold text-white text-sm mt-2">Genuine Title Deed</h3>
              <p className="text-xs text-slate-400 mt-1">Survey 142/3A (2,400 sq.ft) • Clean Title</p>
            </div>
            <div className="mt-3 text-[11px] font-semibold text-emerald-400">✓ Expected: VERIFIED</div>
          </button>

          {/* Preset 2 (Authority Review Required) */}
          <button
            type="button"
            onClick={() => handlePresetSelect('review_required')}
            className={`p-4 rounded-xl border text-left transition-all duration-150 flex flex-col justify-between ${
              selectedPreset === 'review_required' || selectedPreset === 'collision'
                ? 'bg-amber-950/40 border-amber-400 shadow-lg shadow-amber-500/15 ring-1 ring-amber-400/50'
                : 'glass-card border-slate-800 hover:border-slate-700'
            }`}
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-amber-300 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                  CASE 2 (AUTHORITY REVIEW)
                </span>
                {(selectedPreset === 'review_required' || selectedPreset === 'collision') && (
                  <CheckCircle2 className="w-4 h-4 text-amber-400" />
                )}
              </div>
              <h3 className="font-bold text-white text-sm mt-2">Authority Review Deed</h3>
              <p className="text-xs text-slate-400 mt-1">Survey 142/3B • 17.8 m² Cadastral Dispute</p>
            </div>
            <div className="mt-3 text-[11px] font-semibold text-amber-300">⚠ Expected: REVIEW_REQUIRED</div>
          </button>

          {/* Preset 3 (Tampered) */}
          <button
            type="button"
            onClick={() => handlePresetSelect('tampered')}
            className={`p-4 rounded-xl border text-left transition-all duration-150 flex flex-col justify-between ${
              selectedPreset === 'tampered'
                ? 'bg-purple-950/40 border-purple-400 shadow-lg shadow-purple-500/15 ring-1 ring-purple-400/50'
                : 'glass-card border-slate-800 hover:border-slate-700'
            }`}
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-purple-300 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
                  CASE 3
                </span>
                {selectedPreset === 'tampered' && (
                  <CheckCircle2 className="w-4 h-4 text-purple-400" />
                )}
              </div>
              <h3 className="font-bold text-white text-sm mt-2">Tampered Deed</h3>
              <p className="text-xs text-slate-400 mt-1">Area Forged: 2,400 &rarr; 3,400 sq.ft</p>
            </div>
            <div className="mt-3 text-[11px] font-semibold text-purple-300">⚠ Expected: TAMPER_ALERT</div>
          </button>

        </div>

        {/* Selected Preset Reason Context Card */}
        {(selectedPreset === 'review_required' || selectedPreset === 'collision') && (
          <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs text-slate-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-in fade-in duration-200">
            <div className="flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-amber-300 block font-semibold">Reason for Authority Review:</strong>
                <p className="text-slate-300 text-[11px] leading-relaxed mt-0.5">
                  This deed contains a 17.8 m² cadastral boundary overlap with registered parcel Survey No. 142/3A. Under Section 34 & 35 of the Registration Act, 1908, the Sub-Registrar / Revenue Authority must physically inspect or hold a statutory hearing before clear title can be confirmed.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleRunVerification}
              disabled={isVerifying}
              className="shrink-0 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-black text-xs shadow-md shadow-amber-500/20 transition active:scale-95 disabled:opacity-50 cursor-pointer flex items-center justify-center space-x-1.5"
            >
              <span>⚡ Run Authority Verification</span>
            </button>
          </div>
        )}
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
            {selectedFile 
              ? `Selected Custom File: ${selectedFile.name}` 
              : selectedPreset 
              ? `Armed Preset: ${selectedPreset.toUpperCase()} (Click below to verify)` 
              : 'Drag & drop land deed or browse'}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            {selectedFile 
              ? `${(selectedFile.size / 1024).toFixed(1)} KB • Ready for automated multi-vector verification`
              : 'Supports PDF, JPG, PNG, TIFF, or plain text deeds (Max 25MB). Default demonstration document is armed.'}
          </p>
        </label>

        {selectedFile && (
          <div className="flex items-center justify-center gap-2">
            <button
              type="button"
              onClick={handleResetToDefault}
              className="text-xs font-mono text-emerald-400 hover:underline flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Reset to Default Demo Document</span>
            </button>
          </div>
        )}

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
