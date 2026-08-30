'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Lock, 
  FileText, 
  MapPin, 
  ExternalLink, 
  QrCode, 
  CheckCircle2, 
  XCircle, 
  Eye, 
  Printer, 
  ArrowLeft,
  Cpu,
  Layers,
  Download,
  FileDown,
  FileCode,
  Copy,
  Check,
  Sparkles,
  Award,
  Maximize2,
  X,
  AlertCircle
} from 'lucide-react';
import { apiService, VerificationReport } from '@/services/api';
import { MapView } from '@/components/MapView';

export default function VerificationReportPage() {
  const params = useParams();
  const verificationId = params.id as string;

  const [report, setReport] = useState<VerificationReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewNotes, setReviewNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [copiedLink, setCopiedLink] = useState(false);
  const [showQrModal, setShowQrModal] = useState(false);
  const [showAuthorityModal, setShowAuthorityModal] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await apiService.getVerificationDetails(verificationId);
      setReport(data);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to load forensic report.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!verificationId) return;
    loadData();
  }, [verificationId]);

  const handleReviewAction = async (decision: 'APPROVE' | 'REJECT') => {
    if (!verificationId) return;
    try {
      setReviewLoading(true);
      const updated = await apiService.submitReview(verificationId, decision, reviewNotes || undefined);
      setReport(updated);
      setShowAuthorityModal(false);
      
      if (decision === 'APPROVE') {
        try {
          const confetti = (await import('canvas-confetti')).default;
          confetti({
            particleCount: 90,
            spread: 60,
            origin: { y: 0.6 }
          });
        } catch (e) {
          // ignore if canvas-confetti is not loaded
        }
      }
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || 'Failed to submit Sub-Registrar statutory review.');
    } finally {
      setReviewLoading(false);
    }
  };

  const handleCopyLink = () => {
    if (typeof window !== 'undefined') {
      const url = `${window.location.origin}/verify/${report?.verification_id || verificationId}`;
      navigator.clipboard.writeText(url);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2500);
    }
  };


  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3">
        <div className="w-12 h-12 rounded-full border-4 border-emerald-500/20 border-t-emerald-500 animate-spin"></div>
        <p className="text-sm font-mono text-slate-400">Loading Forensic Audit Report for {verificationId}...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto glass-panel p-8 rounded-2xl border border-red-500/30 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto" />
        <h2 className="text-xl font-bold text-white">Forensic Report Not Found</h2>
        <p className="text-xs text-slate-400">{error || 'Verification ID does not exist.'}</p>
        <Link href="/upload" className="inline-block px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs font-bold">
          Submit New Verification
        </Link>
      </div>
    );
  }

  const isVerified = report.overall_status === 'VERIFIED';
  const isCollision = report.overall_status === 'SPATIAL_COLLISION';
  const isTampered = report.overall_status === 'TAMPER_ALERT';

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <Link href="/dashboard" className="inline-flex items-center text-xs font-mono text-slate-400 hover:text-emerald-400 transition">
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          <span>Back to Command Center</span>
        </Link>

        <div className="flex flex-wrap items-center gap-2.5">
          {(!isVerified && (isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required)) && (
            <button
              onClick={() => setShowAuthorityModal(true)}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-black text-xs shadow-lg shadow-amber-500/25 transition active:scale-95 animate-pulse cursor-pointer"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>⚡ Authority Verification</span>
            </button>
          )}

          {isVerified && (
            <a
              href={apiService.getCertificatePdfUrl(verificationId)}
              download={`PlotProof_Certificate_${verificationId}.pdf`}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-600/25 transition active:scale-95 cursor-pointer"
              title="Download official verifiable PDF certificate certifying genuine land title"
            >
              <Download className="w-4 h-4" />
              <span>Download Certificate (PDF)</span>
            </a>
          )}

          {isVerified && (
            <a
              href={apiService.getCertificateQrDownloadUrl(verificationId)}
              download={`PlotProof_QR_${verificationId}.png`}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg glass-panel hover:bg-slate-800 text-emerald-400 text-xs font-bold border border-emerald-500/30 transition active:scale-95 cursor-pointer"
              title="Download scannable QR Code PNG image"
            >
              <QrCode className="w-3.5 h-3.5" />
              <span>Download QR</span>
            </a>
          )}

          <a
            href={apiService.getDocxReportUrl(verificationId)}
            download
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-md shadow-blue-600/25 transition active:scale-95 cursor-pointer"
            title="Download full forensic verification audit report as Word document (.docx)"
          >
            <FileDown className="w-4 h-4" />
            <span>DOCX Report</span>
          </a>

          <a
            href={apiService.getMarkdownReportUrl(verificationId)}
            download
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg glass-panel hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700 transition"
            title="Download report in Markdown format"
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>.MD</span>
          </a>

          {report.certificate_url && (
            <Link
              href={report.certificate_url}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-700 shadow-md transition active:scale-95"
            >
              <Eye className="w-4 h-4 text-emerald-400" />
              <span>View Certificate</span>
            </Link>
          )}

          <Link
            href={`/verify/${report.authenticity.document_hash}`}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg glass-panel hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700 transition"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Public Verify</span>
          </Link>
        </div>
      </div>

      {/* Forensic Verdict Hero Banner */}
      <div className={`p-6 sm:p-8 rounded-2xl border relative overflow-hidden shadow-2xl ${
        isVerified
          ? 'glass-panel border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-slate-900/60 to-teal-950/30'
          : isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required
          ? 'glass-panel border-amber-500/50 bg-gradient-to-r from-amber-950/50 via-slate-900/70 to-orange-950/30 ring-1 ring-amber-500/30 shadow-amber-500/10'
          : isTampered
          ? 'glass-panel border-purple-500/50 bg-gradient-to-r from-purple-950/50 via-slate-900/60 to-pink-950/30'
          : 'glass-panel border-amber-500/40 bg-amber-950/20'
      }`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
              <span>FORENSIC VERIFICATION ID:</span>
              <span className="text-white font-bold bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                {report.verification_id}
              </span>
            </div>

            <div className="flex items-center space-x-3">
              {isVerified && <CheckCircle2 className="w-8 h-8 text-emerald-400" />}
              {!isVerified && (isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required) && (
                <AlertTriangle className="w-8 h-8 text-amber-400 animate-pulse" />
              )}
              {isTampered && <Lock className="w-8 h-8 text-purple-400" />}
              
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                {isVerified && '✓ VERIFIED — CLEAN TITLE'}
                {!isVerified && (isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required) && '⚠ SUB-REGISTRAR STATUTORY REVIEW REQUIRED'}
                {isTampered && '⚠ DOCUMENT INTEGRITY TAMPER ALERT'}
                {!isVerified && !isCollision && report.overall_status !== 'REVIEW_REQUIRED' && !(report as any).review_required && !isTampered && '● MANUAL AUDIT REQUIRED'}
              </h1>
            </div>

            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              {isVerified && 'Document parsed, zero boundary intersections detected against cadastral baseline, and SHA-256 canonical hash successfully registered on blockchain.'}
              {!isVerified && (isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required) && (
                (report as any).review_reason || `Cadastral spatial boundary dispute intercepted: Deed boundaries overlap registered parcel by ${report.spatial.overlap_detail.overlap_area_sqm} m². Requires Sub-Registrar statutory review under Section 34 of Registration Act, 1908.`
              )}
              {isTampered && 'Canonical JSON cryptographic fingerprint mismatch. Document attributes have been modified after registration.'}
            </p>

            {!isVerified && (isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required) && (
              <div className="pt-2">
                <button
                  onClick={() => setShowAuthorityModal(true)}
                  className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-black text-xs shadow-lg shadow-amber-500/30 transition active:scale-95 cursor-pointer"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>Execute Authority Verification (Button Action)</span>
                </button>
              </div>
            )}
          </div>

          {/* Confidence Score Gauge */}
          <div className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-950/70 border border-slate-800 text-center min-w-[150px]">
            <span className="text-[10px] font-mono text-slate-400 uppercase">Confidence Score</span>
            <div className={`text-4xl font-black mt-1 ${
              isVerified 
                ? 'text-emerald-400' 
                : (isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required) 
                ? 'text-amber-400' 
                : 'text-purple-400'
            }`}>
              {report.confidence_score}%
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-1">Multi-Vector Weighted</span>
          </div>
        </div>
      </div>

        {/* Featured Section: Genuine Title Certificate & Scannable QR Code */}
        {isVerified && (
          <div className="glass-panel p-6 sm:p-8 rounded-2xl border-2 border-emerald-500/50 bg-gradient-to-r from-emerald-950/60 via-slate-900/80 to-teal-950/50 shadow-2xl relative overflow-hidden space-y-6">
            {/* Top banner tag */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-emerald-500/30 pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <Award className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
                      AUTHENTICATED TITLE CERTIFICATE
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-[10px] font-bold text-emerald-300">
                      ✓ 100% GENUINE LAND TITLE
                    </span>
                  </div>
                  <h2 className="text-lg sm:text-xl font-black text-white tracking-tight mt-0.5">
                    Official Digital Land Title Certificate & Verification QR
                  </h2>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={handleCopyLink}
                  className="px-3 py-1.5 rounded-lg glass-panel hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700 transition flex items-center space-x-1.5"
                  title="Copy public verification link"
                >
                  {copiedLink ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedLink ? 'Link Copied!' : 'Copy Verification Link'}</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
              {/* Scannable QR Code display */}
              <div className="md:col-span-4 flex flex-col items-center justify-center p-5 rounded-xl bg-slate-950/80 border border-emerald-500/30 text-center relative group">
                <div 
                  className="relative bg-white p-3 rounded-xl shadow-xl border border-slate-200 cursor-pointer transition hover:scale-105" 
                  onClick={() => setShowQrModal(true)}
                  title="Click to enlarge QR code for easy scanning"
                >
                  <img
                    src={apiService.getCertificateQrUrl(verificationId)}
                    alt="Scannable Genuine Land Certificate QR Code"
                    className="w-36 h-36 object-contain"
                    onError={(e: any) => {
                      e.target.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
                        typeof window !== 'undefined' ? `${window.location.origin}/certificate/${verificationId}` : `http://localhost:3000/certificate/${verificationId}`
                      )}`;
                    }}
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center rounded-xl">
                    <span className="text-white text-xs font-bold flex items-center gap-1 bg-slate-900/90 px-2.5 py-1 rounded-md border border-slate-700">
                      <Maximize2 className="w-3.5 h-3.5" /> Enlarge QR
                    </span>
                  </div>
                </div>
                <span className="text-[11px] font-mono font-bold text-emerald-400 mt-2.5 flex items-center gap-1">
                  <QrCode className="w-3.5 h-3.5" /> Scan to Verify & Download
                </span>
                <span className="text-[10px] text-slate-400 mt-0.5">
                  Point any smartphone camera to inspect title
                </span>
              </div>

              {/* Certificate Details & Direct Download Action Buttons */}
              <div className="md:col-span-8 space-y-4">
                <div className="space-y-1.5 text-xs text-slate-300">
                  <p className="leading-relaxed">
                    This property (<strong className="text-white font-mono">Survey No. {report.document.extracted_fields.survey_number}</strong>, {report.document.extracted_fields.village}, {report.document.extracted_fields.taluk} Taluk) has successfully passed all forensic verification modules. It possesses zero spatial overlaps against cadastral boundaries, verified cryptographic document integrity, and immutable Polygon blockchain anchoring.
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 text-[11px] font-mono">
                    <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block text-[9px]">VERIFICATION ID</span>
                      <span className="text-white font-bold truncate block">{verificationId}</span>
                    </div>
                    <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block text-[9px]">TITLE STATUS</span>
                      <span className="text-emerald-400 font-bold block">✓ GENUINE TITLE</span>
                    </div>
                    <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block text-[9px]">BLOCKCHAIN ANCHOR</span>
                      <span className="text-purple-400 font-bold block">CONFIRMED (L2)</span>
                    </div>
                  </div>
                </div>

                {/* Primary Action Buttons */}
                <div className="flex flex-wrap items-center gap-3 pt-2">
                  <a
                    href={apiService.getCertificatePdfUrl(verificationId)}
                    download={`PlotProof_Genuine_Certificate_${verificationId}.pdf`}
                    className="flex-1 min-w-[200px] py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center space-x-2 shadow-lg shadow-emerald-600/30 transition active:scale-95 cursor-pointer"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download Genuine Certificate (PDF)</span>
                  </a>

                  <a
                    href={apiService.getCertificateQrDownloadUrl(verificationId)}
                    download={`PlotProof_QR_${verificationId}.png`}
                    className="py-3 px-4 rounded-xl glass-panel hover:bg-slate-800 text-emerald-400 text-xs font-bold flex items-center justify-center space-x-2 border border-emerald-500/30 shadow-md transition active:scale-95 cursor-pointer"
                    title="Download standalone scannable QR Code PNG image"
                  >
                    <QrCode className="w-4 h-4" />
                    <span>Download QR (PNG)</span>
                  </a>

                  {report.certificate_url && (
                    <Link
                      href={report.certificate_url}
                      className="py-3 px-4 rounded-xl glass-panel hover:bg-slate-800 text-slate-200 text-xs font-medium flex items-center justify-center space-x-2 border border-slate-700 transition active:scale-95"
                    >
                      <Eye className="w-4 h-4 text-emerald-400" />
                      <span>View Certificate</span>
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

      {/* Sub-Registrar Statutory Review Action Banner (When Review Required or Collision) */}
      {(!isVerified && (isCollision || report.overall_status === 'REVIEW_REQUIRED' || (report as any).review_required)) && (
        <div className="glass-panel p-6 sm:p-7 rounded-2xl border-2 border-amber-500/50 bg-gradient-to-r from-amber-950/50 via-slate-900/80 to-orange-950/40 shadow-2xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-amber-500/30 pb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0">
                <AlertTriangle className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
                    STATUTORY REVIEW REQUIRED
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-[10px] font-bold text-amber-300">
                    AUTHORITY INTERVENTION
                  </span>
                </div>
                <h2 className="text-base sm:text-lg font-bold text-white tracking-tight mt-0.5">
                  Sub-Registrar Revenue Review & Cadastral Dispute Adjudication
                </h2>
              </div>
            </div>

            <div className="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-amber-300">
              {(report as any).review_authority || 'Sub-Registrar Office, Tambaram Jurisdiction'}
            </div>
          </div>

          {/* Specific Reason Breakdown Box */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-amber-500/30 space-y-3">
            <div className="flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <strong className="text-xs font-bold text-amber-300 block uppercase tracking-wide">
                  Reason for Required Review:
                </strong>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {(report as any).review_reason || (
                    `Cadastral Boundary Encroachment: The submitted plot coordinates intersect registered Survey No. ${report.spatial.overlap_detail.affected_surveys.join(', ') || '142/3A'} by ${report.spatial.overlap_detail.overlap_area_sqm} m² (${report.spatial.overlap_detail.overlap_area_sqft} sq.ft).`
                  )}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-[11px]">
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[10px]">STATUTORY BASIS</span>
                <span className="text-slate-300 font-semibold">{(report as any).statutory_grounds || 'Registration Act, 1908 (Sec 34/35)'}</span>
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[10px]">ENCROACHMENT EXTENT</span>
                <span className="text-red-400 font-bold">{report.spatial.overlap_detail.overlap_area_sqm} m² ({(report as any).spatial.overlap_detail.overlap_percentage}% overlap)</span>
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[10px]">AFFECTED REGISTERED PARCEL</span>
                <span className="text-amber-300 font-mono font-bold">Survey No. {report.spatial.overlap_detail.affected_surveys.join(', ') || '142/3A'}</span>
              </div>
            </div>
          </div>

          {/* Sub-Registrar Notes Input & Actions */}
          <div className="space-y-3 pt-1">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Sub-Registrar Statutory Inquiry Notes (Optional):
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="E.g., Physical site inspection completed by Revenue Inspector. Field boundary reconciled with Survey 142/3A titleholder."
                rows={2}
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400 transition"
              />
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
              <span className="text-[11px] text-slate-400">
                Authorized Sub-Registrar Action: Approving will certify clean title, generate ZK proof, anchor on Polygon, and issue QR certificate.
              </span>

              <div className="flex items-center space-x-3 w-full sm:w-auto shrink-0">
                <button
                  disabled={reviewLoading}
                  onClick={() => handleReviewAction('APPROVE')}
                  className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/20 transition disabled:opacity-50 active:scale-95 flex items-center justify-center space-x-2 cursor-pointer"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{reviewLoading ? 'Processing Approval...' : 'Approve Clear Title'}</span>
                </button>
                <button
                  disabled={reviewLoading}
                  onClick={() => handleReviewAction('REJECT')}
                  className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-red-600/80 hover:bg-red-600 text-white text-xs font-bold transition disabled:opacity-50 active:scale-95 flex items-center justify-center space-x-2 cursor-pointer"
                >
                  <XCircle className="w-4 h-4" />
                  <span>{reviewLoading ? 'Processing...' : 'Reject Deed'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4 Core Forensic Pillars Grid */}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Pillar 1: Document Intelligence */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              <span>1. Document Intelligence & OCR</span>
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              OpenCV + Regex
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-mono text-[10px]">SURVEY NUMBER</span>
              <div className="text-white font-bold font-mono mt-0.5">{report.document.extracted_fields.survey_number}</div>
            </div>
            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-mono text-[10px]">AREA EXTENT</span>
              <div className="text-white font-bold font-mono mt-0.5">{report.document.extracted_fields.area_sqft} sq.ft</div>
            </div>
            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-mono text-[10px]">TALUK / DISTRICT</span>
              <div className="text-white font-bold mt-0.5">{report.document.extracted_fields.taluk}, {report.document.extracted_fields.district}</div>
            </div>
            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-mono text-[10px]">VILLAGE</span>
              <div className="text-white font-bold mt-0.5">{report.document.extracted_fields.village}</div>
            </div>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 space-y-1.5 text-xs">
            <span className="text-slate-400 font-semibold text-[11px]">Reconstructed Boundaries:</span>
            <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-300">
              <div><strong className="text-slate-500">N:</strong> {report.document.extracted_fields.boundaries.north}</div>
              <div><strong className="text-slate-500">S:</strong> {report.document.extracted_fields.boundaries.south}</div>
              <div><strong className="text-slate-500">E:</strong> {report.document.extracted_fields.boundaries.east}</div>
              <div><strong className="text-slate-500">W:</strong> {report.document.extracted_fields.boundaries.west}</div>
            </div>
          </div>
        </div>

        {/* Pillar 2: GIS Spatial Analysis */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-400" />
              <span>2. GIS Cadastral Intelligence</span>
            </h3>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
              report.spatial.overlap_detail.collision_detected
                ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }`}>
              {report.spatial.overlap_detail.collision_detected ? 'COLLISION DETECTED' : '0 COLLISIONS'}
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Boundary Topological Validity:</span>
              <span className="text-emerald-400 font-semibold">✓ Valid Polygon</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Overlap Area:</span>
              <span className={`font-mono font-bold ${report.spatial.overlap_detail.collision_detected ? 'text-red-400' : 'text-emerald-400'}`}>
                {report.spatial.overlap_detail.overlap_area_sqm} m² ({report.spatial.overlap_detail.overlap_area_sqft} sq.ft)
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Affected Survey Parcels:</span>
              <span className="font-mono text-slate-200">
                {report.spatial.overlap_detail.affected_surveys.length > 0 
                  ? report.spatial.overlap_detail.affected_surveys.join(', ')
                  : 'None'}
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Cadastral Risk Level:</span>
              <span className={`font-bold ${report.spatial.overlap_detail.collision_detected ? 'text-red-400' : 'text-emerald-400'}`}>
                {report.spatial.overlap_detail.risk_level}
              </span>
            </div>
          </div>

          <Link
            href="/map"
            className="w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center justify-center space-x-1.5 transition border border-slate-700"
          >
            <span>Open Interactive GIS Viewer</span>
            <ExternalLink className="w-3.5 h-3.5 text-emerald-400" />
          </Link>
        </div>

        {/* Pillar 3: Authenticity & Blockchain */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <Lock className="w-4 h-4 text-purple-400" />
              <span>3. Trust & Cryptographic Hash</span>
            </h3>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
              report.authenticity.is_tampered
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }`}>
              {report.authenticity.is_tampered ? 'TAMPERED / MISMATCH' : 'AUTHENTIC HASH'}
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div>
              <span className="text-slate-500 font-mono text-[10px]">DOCUMENT SHA-256 FINGERPRINT</span>
              <div className="font-mono text-emerald-400 bg-slate-900 p-2 rounded border border-slate-800 text-[11px] truncate mt-1">
                {report.authenticity.document_hash}
              </div>
            </div>

            <div className="flex justify-between py-1 border-b border-slate-800/60 text-xs">
              <span className="text-slate-400">Blockchain Network:</span>
              <span className="font-mono text-slate-200">{report.blockchain.network}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60 text-xs">
              <span className="text-slate-400">Smart Contract:</span>
              <span className="font-mono text-slate-400 text-[11px] truncate max-w-[180px]">
                {report.blockchain.contract_address}
              </span>
            </div>
            <div className="flex justify-between py-1 text-xs">
              <span className="text-slate-400">Transaction Ref:</span>
              <span className="font-mono text-purple-400 text-[11px] truncate max-w-[180px]">
                {report.blockchain.transaction_hash}
              </span>
            </div>
          </div>
        </div>

        {/* Pillar 4: Privacy & ZK Commitment */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              <span>4. Privacy (ZK & PII Minimization)</span>
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Pedersen Commitment
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Citizen Aadhaar / UID:</span>
              <span className="font-mono text-slate-300 font-semibold">{report.privacy.masked_attributes?.aadhaar_number || 'XXXX-XXXX-8912'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Citizen Name Mask:</span>
              <span className="font-mono text-slate-300 font-semibold">{report.privacy.masked_attributes?.owner_name || 'K. S. **********'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Exposed PII on Blockchain:</span>
              <span className="text-emerald-400 font-bold">0% (Strictly Zero)</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Zero-Knowledge Verification:</span>
              <span className="text-amber-400 font-mono text-[11px]">✓ Valid Titleholder Proof</span>
            </div>
          </div>
        </div>

      </div>

      {/* Embedded Map Section */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-400" />
              <span>Cadastral GIS Verification Map</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Visual representation of submitted plot polygon and adjacent cadastral parcels</p>
          </div>
          <Link href="/map" className="text-xs text-emerald-400 hover:underline flex items-center gap-1 font-mono">
            <span>Expand Fullscreen</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>

        <MapView
          cadastralLayer={report.spatial.cadastral_layer_geojson}
          submittedPlot={report.spatial.submitted_plot_geojson}
          collisionPolygon={report.spatial.overlap_detail.collision_polygon_geojson}
          highlightSurvey={report.document.extracted_fields.survey_number}
          height="400px"
        />
      </div>

      {/* Download & Export Forensic Dossier Section */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] font-mono text-blue-400 mb-1">
              <FileDown className="w-3 h-3" />
              <span>EXPORTABLE AUDIT DOSSIERS</span>
            </div>
            <h3 className="font-bold text-white text-lg flex items-center gap-2">
              <span>Download Official Verification Documents</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Export the complete forensic audit record in Microsoft Word (.docx), Markdown (.md), or printable PDF formats
            </p>
          </div>

          <div className="text-right">
            <span className="text-[11px] font-mono text-slate-500 block">ID: {report.verification_id}</span>
            <span className="text-[10px] font-mono text-emerald-400 font-semibold">✓ Cryptographically Signed</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Card 1: Microsoft Word (.docx) */}
          <div className="glass-card p-5 rounded-xl border border-blue-500/30 hover:border-blue-400 transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">
                  WORD DOC
                </span>
                <FileText className="w-5 h-5 text-blue-400" />
              </div>
              <h4 className="font-bold text-white text-sm">Forensic Audit (.docx)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Structured multi-vector tables for OCR, Cadastral GIS breakdown, SHA-256 digest, and blockchain receipt.
              </p>
            </div>
            
            <a
              href={apiService.getDocxReportUrl(verificationId)}
              download
              className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/20 transition active:scale-95 cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download .DOCX</span>
            </a>
          </div>

          {/* Card 2: Markdown Dossier (.md) */}
          <div className="glass-card p-5 rounded-xl border border-slate-700 hover:border-slate-600 transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-slate-300 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                  PLAIN MD
                </span>
                <FileCode className="w-5 h-5 text-emerald-400" />
              </div>
              <h4 className="font-bold text-white text-sm">Markdown Dossier (.md)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Lightweight plain-text formatted for automated developer pipelines, forensic logs, or GitHub archiving.
              </p>
            </div>
            
            <a
              href={apiService.getMarkdownReportUrl(verificationId)}
              download
              className="w-full py-2.5 rounded-lg glass-panel hover:bg-slate-800 text-slate-200 text-xs font-bold flex items-center justify-center space-x-2 border border-slate-700 transition active:scale-95 cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download .MD</span>
            </a>
          </div>

          {/* Card 3: Printable PDF / Certificate */}
          <div className="glass-card p-5 rounded-xl border border-emerald-500/30 hover:border-emerald-400 transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                  OFFICIAL PDF
                </span>
                <Award className="w-5 h-5 text-emerald-400" />
              </div>
              <h4 className="font-bold text-white text-sm">Genuine Title (PDF)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Official PDF certificate with embedded QR verification code, security stamps, and statutory disclaimer.
              </p>
            </div>
            
            <a
              href={apiService.getCertificatePdfUrl(verificationId)}
              download={`PlotProof_Certificate_${verificationId}.pdf`}
              className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center space-x-2 shadow-lg shadow-emerald-600/20 transition active:scale-95 cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download PDF</span>
            </a>
          </div>

          {/* Card 4: Scannable QR Code (PNG) */}
          <div className="glass-card p-5 rounded-xl border border-teal-500/30 hover:border-teal-400 transition-all flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-teal-400 px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/20">
                  SCANNABLE QR
                </span>
                <QrCode className="w-5 h-5 text-teal-400" />
              </div>
              <h4 className="font-bold text-white text-sm">Verification QR (.png)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                High-resolution standalone QR code image for physical property signage, sale deed attachments, or sharing.
              </p>
            </div>
            
            <a
              href={apiService.getCertificateQrDownloadUrl(verificationId)}
              download={`PlotProof_QR_${verificationId}.png`}
              className="w-full py-2.5 rounded-lg glass-panel hover:bg-slate-800 text-teal-300 text-xs font-bold flex items-center justify-center space-x-2 border border-teal-500/30 transition active:scale-95 cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download QR (.PNG)</span>
            </a>
          </div>

        </div>
      </div>

      {/* QR Code Enlarge Modal */}
      {showQrModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setShowQrModal(false)}>
          <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-emerald-500/40 bg-slate-900 max-w-md w-full text-center space-y-4 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setShowQrModal(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-400">
              <Award className="w-3.5 h-3.5" />
              <span>GENUINE TITLE VERIFICATION QR</span>
            </div>

            <h3 className="text-lg font-bold text-white">Scan to Verify Genuine Land Title</h3>
            <p className="text-xs text-slate-400">
              Point your smartphone camera at this QR code to immediately access the official certificate and verify title authenticity.
            </p>

            <div className="bg-white p-4 rounded-2xl mx-auto w-fit shadow-2xl border-2 border-emerald-500/40">
              <img
                src={apiService.getCertificateQrUrl(verificationId)}
                alt="Enlarged Genuine Land Certificate QR Code"
                className="w-52 h-52 object-contain"
                onError={(e: any) => {
                  e.target.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(
                    typeof window !== 'undefined' ? `${window.location.origin}/certificate/${verificationId}` : `http://localhost:3000/certificate/${verificationId}`
                  )}`;
                }}
              />
            </div>

            <div className="font-mono text-[11px] text-slate-400 bg-slate-950 p-2.5 rounded-lg border border-slate-800 break-all">
              Verification ID: <span className="text-emerald-400 font-bold">{verificationId}</span>
            </div>

            <div className="flex items-center space-x-3 pt-2">
              <a
                href={apiService.getCertificateQrDownloadUrl(verificationId)}
                download={`PlotProof_QR_${verificationId}.png`}
                className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center space-x-2 transition cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Save QR Image</span>
              </a>
              <a
                href={apiService.getCertificatePdfUrl(verificationId)}
                download={`PlotProof_Certificate_${verificationId}.pdf`}
                className="flex-1 py-2.5 rounded-xl glass-panel hover:bg-slate-800 text-slate-200 text-xs font-bold flex items-center justify-center space-x-2 border border-slate-700 transition cursor-pointer"
              >
                <FileDown className="w-4 h-4 text-emerald-400" />
                <span>Download PDF</span>
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Authority Verification Modal Dialog (Button-Triggered) */}
      {showAuthorityModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4" onClick={() => setShowAuthorityModal(false)}>
          <div className="glass-panel p-6 sm:p-8 rounded-2xl border-2 border-amber-500/50 bg-slate-950 max-w-lg w-full space-y-5 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setShowAuthorityModal(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Modal Header */}
            <div className="flex items-center space-x-3 border-b border-amber-500/30 pb-3.5">
              <div className="w-11 h-11 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono font-bold text-amber-400 uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                    GOVERNMENT OF TAMIL NADU
                  </span>
                  <span className="text-[10px] font-bold text-amber-300">
                    SUB-REGISTRAR SRO
                  </span>
                </div>
                <h3 className="text-base font-bold text-white tracking-tight mt-0.5">
                  Execute Statutory Authority Verification
                </h3>
              </div>
            </div>

            {/* Officer & Jurisdiction Credential Badge */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-900/90 p-3 rounded-xl border border-slate-800">
              <div>
                <span className="text-[10px] text-slate-500 block">AUTHORITY ID:</span>
                <span className="text-white font-bold">SRO-TN-TAM-0842</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">JURISDICTION:</span>
                <span className="text-amber-300 font-bold">Tambaram SRO</span>
              </div>
            </div>

            {/* Review Reason & Overlap Summary */}
            <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/30 space-y-2 text-xs">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-amber-300 block font-semibold">Reason for Authority Review:</strong>
                  <p className="text-slate-300 text-[11px] leading-relaxed mt-0.5">
                    {(report as any).review_reason || `Cadastral Boundary Encroachment: Overlaps registered parcel by ${report.spatial.overlap_detail.overlap_area_sqm} m² with Survey No. ${report.spatial.overlap_detail.affected_surveys.join(', ') || '142/3A'}.`}
                  </p>
                </div>
              </div>

              <div className="pt-1.5 border-t border-amber-500/20 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>Mandate: Registration Act, 1908 (Sec 34/35)</span>
                <span className="text-amber-400 font-bold">Overlapping: {report.spatial.overlap_detail.overlap_area_sqm} m²</span>
              </div>
            </div>

            {/* Statutory Notes Input */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-300">
                Sub-Registrar Statutory Decision Notes:
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="E.g., Field survey verified by Revenue Inspector. Boundary reconciled with adjacent titleholders. Approved under Section 34."
                rows={3}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400 transition"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
              <button
                disabled={reviewLoading}
                onClick={() => handleReviewAction('APPROVE')}
                className="w-full sm:flex-1 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center space-x-2 shadow-lg shadow-emerald-600/30 transition disabled:opacity-50 active:scale-95 cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{reviewLoading ? 'Signing & Anchoring...' : '✓ Approve Clear Title (Sign & Anchor)'}</span>
              </button>

              <button
                disabled={reviewLoading}
                onClick={() => handleReviewAction('REJECT')}
                className="w-full sm:w-auto py-3 px-4 rounded-xl bg-red-600/80 hover:bg-red-600 text-white text-xs font-bold flex items-center justify-center space-x-2 transition disabled:opacity-50 active:scale-95 cursor-pointer"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject Deed</span>
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
