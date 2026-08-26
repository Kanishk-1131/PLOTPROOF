'use client';

import React, { useState } from 'react';
import { useAuth, DEMO_USERS } from '../contexts/AuthContext';
import { UserRole } from '../services/api';
import {
  X,
  ShieldCheck,
  UserCheck,
  Building2,
  Lock,
  Mail,
  User,
  Phone,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';

export const AuthModal: React.FC = () => {
  const { isAuthModalOpen, closeAuthModal, user, quickSwitchRole, login, register, logout, isLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<'quick' | 'login' | 'register'>('quick');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isAuthModalOpen) return null;

  const handleQuickSwitch = async (role: UserRole) => {
    setError(null);
    setSubmitting(true);
    try {
      await quickSwitchRole(role);
      setSuccess(`Switched identity to ${role}`);
      setTimeout(() => {
        closeAuthModal();
      }, 400);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to switch identity');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      setSuccess('Logged in successfully!');
      setTimeout(() => {
        closeAuthModal();
      }, 400);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Invalid email or password');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register({
        email,
        password,
        full_name: fullName,
        phone: phone || undefined,
      });
      setSuccess('Account created! Citizen role assigned.');
      setTimeout(() => {
        closeAuthModal();
      }, 400);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Registration failed. Try another email.');
    } finally {
      setSubmitting(false);
    }
  };

  const getRoleConfig = (role: UserRole) => {
    switch (role) {
      case 'CITIZEN':
        return {
          color: 'from-blue-600 to-cyan-500',
          border: 'border-cyan-500/40',
          bg: 'bg-cyan-500/10',
          text: 'text-cyan-400',
          badge: 'CITIZEN',
          icon: UserCheck,
        };
      case 'REGISTRAR':
        return {
          color: 'from-purple-600 to-indigo-500',
          border: 'border-purple-500/40',
          bg: 'bg-purple-500/10',
          text: 'text-purple-400',
          badge: 'REGISTRAR',
          icon: ShieldCheck,
        };
      case 'BANK_OFFICER':
        return {
          color: 'from-amber-600 to-yellow-500',
          border: 'border-amber-500/40',
          bg: 'bg-amber-500/10',
          text: 'text-amber-400',
          badge: 'BANK OFFICER',
          icon: Building2,
        };
      case 'ADMIN':
        return {
          color: 'from-emerald-600 to-teal-500',
          border: 'border-emerald-500/40',
          bg: 'bg-emerald-500/10',
          text: 'text-emerald-400',
          badge: 'SYSTEM ADMIN',
          icon: Sparkles,
        };
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl shadow-emerald-500/10 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-400 p-0.5 shadow-md">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Identity & Access Control
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  Layer 2 RBAC
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Multi-role authentication with Argon2id encryption & audit trails
              </p>
            </div>
          </div>
          <button
            onClick={closeAuthModal}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selection */}
        <div className="flex border-b border-slate-800 bg-slate-950/30 px-6 pt-3 gap-2">
          <button
            onClick={() => { setActiveTab('quick'); setError(null); }}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'quick'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            Quick Demo Persona
          </button>
          <button
            onClick={() => { setActiveTab('login'); setError(null); }}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'login'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Mail className="w-4 h-4" />
            Sign In
          </button>
          <button
            onClick={() => { setActiveTab('register'); setError(null); }}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'register'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <User className="w-4 h-4" />
            Create Account
          </button>
        </div>

        {/* Body */}
        <div className="p-6 max-h-[75vh] overflow-y-auto">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{success}</span>
            </div>
          )}

          {/* TAB 1: QUICK DEMO PERSONAS */}
          {activeTab === 'quick' && (
            <div className="space-y-3">
              <p className="text-xs text-slate-400 mb-2">
                Click any role to authenticate instantly with verified credentials. Perfect for testing role-specific actions:
              </p>

              {(Object.keys(DEMO_USERS) as UserRole[]).map((roleKey) => {
                const conf = getRoleConfig(roleKey);
                const persona = DEMO_USERS[roleKey];
                const Icon = conf.icon;
                const isCurrent = user?.role === roleKey;

                return (
                  <button
                    key={roleKey}
                    disabled={submitting}
                    onClick={() => handleQuickSwitch(roleKey)}
                    className={`w-full text-left p-4 rounded-xl border transition-all flex items-start justify-between group ${
                      isCurrent
                        ? `${conf.border} ${conf.bg} ring-1 ring-emerald-400/50`
                        : 'border-slate-800 hover:border-slate-700 bg-slate-950/40 hover:bg-slate-800/40'
                    }`}
                  >
                    <div className="flex items-start space-x-3.5">
                      <div className={`p-2.5 rounded-lg bg-gradient-to-br ${conf.color} text-white shadow-md`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-white text-sm">{persona.name}</span>
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${conf.bg} ${conf.text} border ${conf.border}`}>
                            {conf.badge}
                          </span>
                          {isCurrent && (
                            <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/20 px-1.5 py-0.5 rounded">
                              ACTIVE
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5 font-mono">{persona.email}</p>
                        <p className="text-xs text-slate-300 mt-1.5">{persona.desc}</p>
                      </div>
                    </div>
                    <ArrowRight className={`w-4 h-4 mt-2 transition-transform group-hover:translate-x-1 ${conf.text}`} />
                  </button>
                );
              })}
            </div>
          )}

          {/* TAB 2: MANUAL LOGIN */}
          {activeTab === 'login' && (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@plotproof.gov.in"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
              >
                {submitting ? 'Authenticating...' : 'Sign In with JWT & Argon2id'}
              </button>
            </form>
          )}

          {/* TAB 3: REGISTER NEW CITIZEN */}
          {activeTab === 'register' && (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Legal Name</label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Venkatesan Subramanian"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="venkat@example.com"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Phone Number (Optional)</label>
                <div className="relative">
                  <Phone className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98400 12345"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password (Min 8 chars)</label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="SecurePass@2026"
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-[11px] text-slate-400 space-y-1">
                <p className="flex items-center gap-1.5 font-medium text-emerald-400">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Anti-Privilege Escalation Guarantee
                </p>
                <p>
                  Public registration assigns the default <strong>CITIZEN</strong> role. Registrar and Bank Officer privileges require administrative key delegation.
                </p>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
              >
                {submitting ? 'Creating Account...' : 'Register Citizen Titleholder'}
              </button>
            </form>
          )}
        </div>

        {/* Footer info */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2 font-mono text-[11px]">
            <span>Active Session:</span>
            {user ? (
              <span className="text-emerald-400 font-semibold">{user.email} ({user.role})</span>
            ) : (
              <span className="text-slate-500">Unauthenticated</span>
            )}
          </div>
          {user && (
            <button
              onClick={() => { logout(); closeAuthModal(); }}
              className="text-rose-400 hover:text-rose-300 text-xs font-semibold underline"
            >
              Sign Out
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
