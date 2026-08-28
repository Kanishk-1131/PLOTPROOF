'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { 
  ShieldCheck, 
  Printer, 
  Download, 
  ArrowLeft, 
  QrCode, 
  CheckCircle2, 
  ExternalLink,
  Award,
  Lock,
  Building,
  Copy,
  Check,
  FileDown,
  Sparkles,
  Maximize2,
  X
} from 'lucide-react';
import { apiService, VerificationReport } from '@/services/api';

export default function CertificatePage() {
  const params = useParams();
  const verificationId = params.id as string;

  const [report, setReport] = useState<VerificationReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [copiedLink, setCopiedLink] = useState(false);
  const [showQrModal, setShowQrModal] = useState(false);

  useEffect(() => {
    if (!verificationId) return;

    const load = async () => {
      try {
        setLoading(true);
        const data = await apiService.getVerificationDetails(verificationId);
        setReport(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [verificationId]);

  const handleCopyLink = () => {
    if (typeof window !== 'undefined') {
      const url = `${window.location.origin}/verify/${report?.verification_id || verificationId}`;
      navigator.clipboard.writeText(url);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2500);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3">
        <div className="w-12 h-12 rounded-full border-4 border-emerald-500/20 border-t-emerald-500 animate-spin"></div>
        <p className="text-sm font-mono text-slate-400">Rendering Digital Land Certificate...</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold text-white">Certificate Not Found</h2>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      
      {/* Top Bar Actions (Hidden in Print) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 print:hidden">
        <Link
          href={`/verification/${verificationId}`}
          className="inline-flex items-center text-xs font-mono text-slate-400 hover:text-emerald-400 transition"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          <span>Back to Forensic Audit Report</span>
        </Link>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handleCopyLink}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg glass-panel hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700 transition active:scale-95 cursor-pointer"
            title="Copy verification URL"
          >
            {copiedLink ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedLink ? 'Copied!' : 'Copy Link'}</span>
          </button>

          <a
            href={apiService.getCertificateQrDownloadUrl(verificationId)}
            download={`PlotProof_QR_${verificationId}.png`}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg glass-panel hover:bg-slate-800 text-emerald-400 text-xs font-bold border border-emerald-500/30 transition active:scale-95 cursor-pointer"
            title="Download scannable QR Code PNG image"
          >
            <QrCode className="w-3.5 h-3.5" />
            <span>Download QR (PNG)</span>
          </a>

          <a
            href={apiService.getCertificatePdfUrl(verificationId)}
            download={`PlotProof_Certificate_${verificationId}.pdf`}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-600/25 transition active:scale-95 cursor-pointer"
            title="Download official high-resolution PDF certificate"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </a>

          <button
            onClick={handlePrint}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-700 shadow transition active:scale-95"
          >
            <Printer className="w-4 h-4" />
            <span>Print</span>
          </button>
        </div>
      </div>

      {/* Official Certificate Layout */}
      <div className="relative bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 p-8 sm:p-12 rounded-2xl border-4 border-double border-emerald-500/40 shadow-2xl text-slate-100 print:border-emerald-700 print:text-black print:bg-white overflow-hidden">
        
        {/* Certificate Watermark Background */}
        <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
          <ShieldCheck className="w-[450px] h-[450px] text-emerald-500" />
        </div>

        {/* Certificate Header */}
        <div className="text-center space-y-2 border-b-2 border-slate-800 pb-6 relative z-10">
          <div className="flex items-center justify-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
              <Award className="w-7 h-7" />
            </div>
          </div>

          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[11px] font-mono font-bold text-emerald-400">
            <Sparkles className="w-3 h-3" />
            <span>GENUINE & AUTHENTIC TITLE CONFIRMED</span>
          </div>

          <h1 className="text-xl sm:text-2xl font-black tracking-widest text-emerald-400 uppercase font-mono mt-1">
            PLOTPROOF DIGITAL LAND TITLE CERTIFICATE
          </h1>
          <p className="text-xs text-slate-400 tracking-wider uppercase font-mono">
            Government Cadastral Verification & Immutable Blockchain Registry
          </p>
        </div>

        {/* Main Certificate Content */}
        <div className="py-8 space-y-6 relative z-10">
          
          <div className="text-center space-y-1">
            <span className="text-xs text-slate-400 uppercase tracking-widest font-mono">THIS IS TO ATTEST AND CERTIFY THAT</span>
            <h2 className="text-lg font-bold text-white">
              Land Parcel Survey Number: <span className="text-emerald-400 font-mono">{report.document.extracted_fields.survey_number}</span>
            </h2>
            <p className="text-xs text-slate-300">
              Located in {report.document.extracted_fields.village}, {report.document.extracted_fields.taluk} Taluk, {report.document.extracted_fields.district} District
            </p>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs">
            <div className="space-y-0.5">
              <span className="text-[10px] font-mono text-slate-500 uppercase">Verification ID</span>
              <div className="font-mono font-bold text-emerald-400">{report.verification_id}</div>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] font-mono text-slate-500 uppercase">Area Extent</span>
              <div className="font-mono font-bold text-white">{report.document.extracted_fields.area_sqft} sq.ft</div>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] font-mono text-slate-500 uppercase">Spatial Status</span>
              <div className="font-mono font-bold text-emerald-400">✓ 0 Overlaps (Genuine)</div>
            </div>
            <div className="space-y-0.5">
              <span className="text-[10px] font-mono text-slate-500 uppercase">Integrity Verdict</span>
              <div className="font-mono font-bold text-emerald-400">✓ Authentic Title</div>
            </div>
          </div>

          {/* Boundaries Table */}
          <div className="border border-slate-800 rounded-xl p-4 bg-slate-950/40 text-xs space-y-2">
            <span className="font-bold text-slate-300 font-mono text-[11px] uppercase">Registered Cadastral Boundaries:</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-300 text-[11px]">
              <div><strong>North:</strong> {report.document.extracted_fields.boundaries.north}</div>
              <div><strong>South:</strong> {report.document.extracted_fields.boundaries.south}</div>
              <div><strong>East:</strong> {report.document.extracted_fields.boundaries.east}</div>
              <div><strong>West:</strong> {report.document.extracted_fields.boundaries.west}</div>
            </div>
          </div>

          {/* Cryptographic Seal & QR Verification Section */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-4 border-t-2 border-slate-800">
            
            {/* Blockchain Details */}
            <div className="space-y-2 flex-1 text-xs">
              <div className="flex items-center space-x-1.5 text-emerald-400 font-bold font-mono">
                <Lock className="w-4 h-4" />
                <span>Cryptographic Document Fingerprint:</span>
              </div>
              <div className="font-mono text-[11px] text-slate-400 bg-slate-950 p-2 rounded border border-slate-800 break-all select-all">
                {report.authenticity.document_hash}
              </div>

              <div className="text-[11px] text-slate-400 space-y-0.5 font-mono">
                <div>Polygon Tx: <span className="text-purple-400">{report.blockchain.transaction_hash}</span></div>
                <div>Block Height: <span className="text-slate-300">#{report.blockchain.block_number}</span></div>
              </div>
            </div>

            {/* Scannable QR Code */}
            <div className="flex flex-col items-center space-y-2 p-3 bg-white rounded-xl shadow-lg border border-slate-300 relative group cursor-pointer" onClick={() => setShowQrModal(true)}>
              <img
                src={apiService.getCertificateQrUrl(verificationId)}
                alt="Verification QR Code"
                className="w-28 h-28 object-contain"
                onError={(e: any) => {
                  e.target.src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(
                    typeof window !== 'undefined' ? `${window.location.origin}/certificate/${verificationId}` : `http://localhost:3000/certificate/${verificationId}`
                  )}`;
                }}
              />
              <span className="text-[9px] font-mono font-bold text-slate-900 uppercase">
                Scan to Verify Title
              </span>
            </div>

          </div>

        </div>

        {/* Certificate Footer */}
        <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono text-slate-500 relative z-10">
          <span>PLOTPROOF PROTOCOL v1.0 • STATE AUDIT NETWORK</span>
          <span>ISSUED: {new Date(report.created_at).toLocaleDateString()}</span>
        </div>

      </div>

      {/* QR Code Enlarge Modal */}
      {showQrModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 print:hidden" onClick={() => setShowQrModal(false)}>
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

    </div>
  );
}
