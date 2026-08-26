'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  ShieldCheck,
  MapPin,
  UploadCloud,
  Layers,
  Activity,
  UserCheck,
  Building2,
  Sparkles,
  ChevronDown,
  FileText,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../services/api';

export const Navbar = () => {
  const pathname = usePathname();
  const { user, openAuthModal } = useAuth();

  const navItems = [
    { href: '/', label: 'Overview', icon: Layers },
    { href: '/dashboard', label: 'Command Center', icon: Activity },
    { href: '/upload', label: 'Verify Deed', icon: UploadCloud },
    { href: '/map', label: 'GIS Cadastral Map', icon: MapPin },
  ];

  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case 'CITIZEN':
        return {
          bg: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300',
          dot: 'bg-cyan-400',
          label: 'Citizen Titleholder',
          icon: UserCheck,
        };
      case 'REGISTRAR':
        return {
          bg: 'bg-purple-500/10 border-purple-500/30 text-purple-300',
          dot: 'bg-purple-400',
          label: 'Sub-Registrar',
          icon: ShieldCheck,
        };
      case 'BANK_OFFICER':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
          dot: 'bg-amber-400',
          label: 'Bank Loan Officer',
          icon: Building2,
        };
      case 'ADMIN':
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
          dot: 'bg-emerald-400',
          label: 'System Admin',
          icon: Sparkles,
        };
    }
  };

  const currentBadge = user ? getRoleBadge(user.role) : null;
  const RoleIcon = currentBadge?.icon;

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-emerald-500 to-teal-400 p-0.5 shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform duration-200">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="text-xl font-black tracking-wider text-white">PLOT<span className="text-emerald-400">PROOF</span></span>
                <span className="px-1.5 py-0.5 text-[10px] font-bold bg-emerald-500/10 text-emerald-400 rounded border border-emerald-500/20">RBAC</span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono">Digital Land Verification Network</p>
            </div>
          </Link>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm shadow-emerald-500/10'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Role Indicator & Actions */}
          <div className="flex items-center space-x-2.5">
            {/* Identity Switcher Button */}
            <button
              onClick={openAuthModal}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all hover:scale-[1.02] active:scale-95 ${
                currentBadge
                  ? `${currentBadge.bg} shadow-sm`
                  : 'bg-slate-900 border-slate-800 text-slate-300 hover:text-white'
              }`}
              title="Click to switch identity or sign in"
            >
              {RoleIcon && <RoleIcon className="w-3.5 h-3.5" />}
              <div className="flex flex-col text-left">
                <span className="text-[10px] text-slate-400 font-mono">Role Identity:</span>
                <span className="font-bold">{currentBadge ? currentBadge.label : 'Sign In'}</span>
              </div>
              <ChevronDown className="w-3.5 h-3.5 ml-1 text-slate-400" />
            </button>

            {/* Launch Demo / Deed Verify Button */}
            <Link
              href="/upload"
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-emerald-600/25 transition-all duration-150 active:scale-95"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Verify Deed</span>
            </Link>
          </div>

        </div>
      </div>
    </header>
  );
};

