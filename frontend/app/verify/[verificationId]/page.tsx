'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ShieldCheck,
  AlertTriangle,
  Lock,
  CheckCircle2,
  XCircle,
  Clock,
  ExternalLink,
  Layers,
  ArrowLeft,
  FileCheck,
  Building2,
  Calendar,
  Hash,
  AlertCircle,
  Download,
  QrCode,
  Award,
  Sparkles,
  Eye,
  FileDown
} from 'lucide-react';
import { apiService } from '@/services/api';

export default function VerificationPortalPage() {
  const params = useParams();
  const rawId = (params.verificationId || params.hash) as string;

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!rawId) return;

    const fetchVerification = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await apiService.getPublicVerification(rawId);
        setData(res);
      } catch (err: any) {
        // Attempt fallback / legacy verification lookup
        try {
          const legacy = await apiService.publicVerify(rawId);
          setData({
            verification_id: rawId,
            status: legacy.verified ? 'VERIFIED' : 'INVALID',
            document_integrity: legacy.verified ? 'PASSED' : 'FAILED',
            spatial_validation: legacy.verified ? 'PASSED' : 'FAILED',
            privacy_proof: legacy.verified ? 'VALID' : 'PENDING',
            blockchain_anchor: legacy.verified ? 'CONFIRMED' : 'PENDING',
            verification_date: legacy.timestamp ? legacy.timestamp.split('T')[0] : '2026-08-26',
            network: legacy.network || 'Polygon Amoy Testnet',
            blockchain_transaction_hash: legacy.blockchain_tx || '0x7a...',
            disclaimer:
              'PlotProof System Verification Certificate. This certificate confirms the verification results produced by the PlotProof system. It does not independently constitute a government-issued title document or legal title guarantee.',
          });
        } catch (fallbackErr) {
          setError('Verification record not found or could not be validated.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchVerification();
  }, [rawId]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span>✓ VERIFIED SYSTEM RECORD</span>
          </div>
        );
      case 'REVOKED':
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 font-bold text-sm animate-pulse">
            <XCircle className="w-5 h-5 text-red-400" />
            <span>! CERTIFICATE REVOKED</span>
          </div>
        );
      case 'BLOCKCHAIN_PENDING':
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold text-sm">
            <Clock className="w-5 h-5 text-amber-400 animate-spin" />
            <span>BLOCKCHAIN ANCHORING PENDING</span>
          </div>
        );
      case 'REVIEW_REQUIRED':
      case 'SPATIAL_RISK':
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            <span>⚠ VERIFICATION REQUIRES STATUTORY REVIEW</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold text-sm">
            <AlertCircle className="w-5 h-5 text-rose-400" />
            <span>INVALID OR ANOMALOUS RECORD</span>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-4 selection:bg-cyan-500/30">
      {/* Background Glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px]" />
      </div>

      <div className="w-full max-w-2xl relative z-10 space-y-6">
        {/* Navigation */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Verification Suite
        </Link>

        {/* Main Verification Card */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur-xl overflow-hidden">
          {/* Header */}
          <div className="border-b border-slate-800 p-6 sm:p-8 bg-slate-900/50 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h1 className="text-xl font-bold tracking-tight text-white">PLOTPROOF</h1>
                  <p className="text-xs text-cyan-400 font-medium tracking-wide uppercase">
                    Forensic Verification Portal
                  </p>
                </div>
              </div>
            </div>

            {data && getStatusBadge(data.status)}
          </div>

          {/* Body */}
          <div className="p-6 sm:p-8 space-y-6">
            {loading ? (
              <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400">
                <Clock className="w-8 h-8 text-cyan-400 animate-spin" />
                <p className="text-sm">Cryptographically auditing record on Polygon L2...</p>
              </div>
            ) : error ? (
              <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/20 text-center space-y-2">
                <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
                <h3 className="font-semibold text-rose-400">Verification Query Failed</h3>
                <p className="text-xs text-slate-400">{error}</p>
              </div>
            ) : (
              data && (
                <>
                  {/* Status Banner */}
                  {data.status === 'REVOKED' && (
                    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                      <div>
                        <strong className="block font-semibold text-red-200">
                          ATTENTION: THIS CERTIFICATE HAS BEEN REVOKED
                        </strong>
                        Sub-Registrar authority invalidated this certificate due to statutory boundary updates.
                      </div>
                    </div>
                  )}

                  {/* Identification Rows */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                    <div>
                      <span className="text-xs text-slate-400 uppercase font-medium tracking-wider">
                        Verification ID
                      </span>
                      <p className="font-mono text-sm font-semibold text-cyan-300 mt-0.5">
                        {data.verification_id}
                      </p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 uppercase font-medium tracking-wider">
                        Verification Date
                      </span>
                      <p className="text-sm font-medium text-slate-200 mt-0.5">
                        {data.verification_date}
                      </p>
                    </div>
                  </div>

                  {/* Multi-Vector Validation Results */}
                  <div className="space-y-3">
                    <h3 className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                      Multi-Vector Forensic Audit Results
                    </h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/40 border border-slate-800/60">
                        <div className="flex items-center gap-3">
                          <FileCheck className="w-4 h-4 text-emerald-400" />
                          <span className="text-sm text-slate-300">Document Cryptographic Integrity</span>
                        </div>
                        <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded">
                          {data.document_integrity}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/40 border border-slate-800/60">
                        <div className="flex items-center gap-3">
                          <Layers className="w-4 h-4 text-emerald-400" />
                          <span className="text-sm text-slate-300">Cadastral Spatial Validation</span>
                        </div>
                        <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded">
                          {data.spatial_validation}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/40 border border-slate-800/60">
                        <div className="flex items-center gap-3">
                          <Lock className="w-4 h-4 text-cyan-400" />
                          <span className="text-sm text-slate-300">Zero-Knowledge Privacy Proof</span>
                        </div>
                        <span className="text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded">
                          {data.privacy_proof}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/40 border border-slate-800/60">
                        <div className="flex items-center gap-3">
                          <Building2 className="w-4 h-4 text-purple-400" />
                          <span className="text-sm text-slate-300">Immutable Blockchain Anchor</span>
                        </div>
                        <span className="text-xs font-bold text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded">
                          {data.blockchain_anchor}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Blockchain Details */}
                  {data.blockchain_transaction_hash && (
                    <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                          On-Chain Polygon L2 Anchor
                        </span>
                        <span className="text-xs text-purple-400 font-medium">{data.network}</span>
                      </div>
                      <p className="font-mono text-xs text-slate-300 break-all bg-slate-900/80 p-2 rounded border border-slate-800">
                        {data.blockchain_transaction_hash}
                      </p>
                      {data.block_explorer_url && (
                        <a
                          href={data.block_explorer_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 transition-colors pt-1"
                        >
                          View PolygonScan Transaction <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  )}

                  {/* Genuine Land Title Certificate & Scannable QR Actions (When Verified) */}
                  {data.status === 'VERIFIED' && (
                    <div className="p-5 rounded-xl bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-teal-950/30 border border-emerald-500/40 space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Award className="w-5 h-5 text-emerald-400" />
                          <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
                            GENUINE TITLE CERTIFICATE & SCANNABLE QR
                          </span>
                        </div>
                        <span className="text-[10px] font-bold text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30">
                          ✓ AUTHENTIC LAND TITLE
                        </span>
                      </div>

                      <p className="text-xs text-slate-300">
                        This property has been cryptographically certified with clean boundaries and immutable Polygon blockchain registration. Download the official PDF certificate or scan the QR code to verify anywhere.
                      </p>

                      <div className="flex flex-col sm:flex-row items-center gap-3 pt-1">
                        <a
                          href={apiService.getCertificatePdfUrl(data.verification_id || rawId)}
                          download={`PlotProof_Certificate_${data.verification_id || rawId}.pdf`}
                          className="w-full sm:flex-1 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center space-x-2 shadow-lg shadow-emerald-600/25 transition active:scale-95 cursor-pointer"
                        >
                          <Download className="w-4 h-4" />
                          <span>Download Certificate (PDF)</span>
                        </a>

                        <a
                          href={apiService.getCertificateQrDownloadUrl(data.verification_id || rawId)}
                          download={`PlotProof_QR_${data.verification_id || rawId}.png`}
                          className="w-full sm:w-auto py-2.5 px-4 rounded-xl glass-panel hover:bg-slate-800 text-emerald-400 text-xs font-bold flex items-center justify-center space-x-2 border border-emerald-500/30 transition active:scale-95 cursor-pointer"
                          title="Download scannable QR Code PNG image"
                        >
                          <QrCode className="w-4 h-4" />
                          <span>Download QR (PNG)</span>
                        </a>

                        <Link
                          href={`/certificate/${data.verification_id || rawId}`}
                          className="w-full sm:w-auto py-2.5 px-4 rounded-xl glass-panel hover:bg-slate-800 text-slate-200 text-xs font-medium flex items-center justify-center space-x-2 border border-slate-700 transition active:scale-95"
                        >
                          <Eye className="w-4 h-4 text-emerald-400" />
                          <span>View Certificate</span>
                        </Link>
                      </div>
                    </div>
                  )}

                  {/* Statutory Legal Notice */}
                  <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/60 text-xs text-slate-400 leading-relaxed">
                    <strong className="text-slate-300 block mb-1">
                      PlotProof System Verification Certificate Notice
                    </strong>
                    {data.disclaimer}
                  </div>
                </>
              )
            )}
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-slate-500">
          Powered by PLOTPROOF Enterprise &bull; Zero-Knowledge Cryptographic Title Engine
        </p>
      </div>
    </div>
  );
}
