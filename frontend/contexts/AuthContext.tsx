'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiService, User, UserRole } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isAuthModalOpen: boolean;
  openAuthModal: () => void;
  closeAuthModal: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; phone?: string }) => Promise<void>;
  quickSwitchRole: (role: UserRole) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Pre-seeded Demo Credentials for instant Hackathon / SIH jury testing
export const DEMO_USERS: Record<UserRole, { email: string; name: string; title: string; desc: string }> = {
  CITIZEN: {
    email: 'citizen@plotproof.gov.in',
    name: 'Ramanathan K. S.',
    title: 'Land Titleholder / Citizen',
    desc: 'Uploads deeds, monitors title verification status, and accesses tamper-evident digital certificates.'
  },
  REGISTRAR: {
    email: 'registrar@tn.gov.in',
    name: 'Sub-Registrar Officer',
    title: 'Tambaram Registration Authority',
    desc: 'Reviews automated OCR extraction, verifies spatial boundaries, inspects tamper alerts, and issues statutory approvals.'
  },
  BANK_OFFICER: {
    email: 'auditor@hdfcbank.com',
    name: 'HDFC Land Audit Officer',
    title: 'Bank Mortgage Due-Diligence',
    desc: 'Audits property authenticity, validates zero double-pledging, and issues collateral clearance certificates.'
  },
  ADMIN: {
    email: 'admin@plotproof.gov.in',
    name: 'System Administrator',
    title: 'PlotProof Network Operator',
    desc: 'Manages cryptographic registry, monitors blockchain sync, and audits full forensic security logs.'
  }
};

export const DEMO_PASSWORD = 'PlotProof2026!';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  // Restore session from localStorage on initial load
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('plotproof_access_token');
      const storedUser = localStorage.getItem('plotproof_user');

      if (storedToken && storedUser) {
        try {
          setUser(JSON.parse(storedUser));
          // Refresh user profile in background
          const me = await apiService.getMe();
          setUser(me);
          localStorage.setItem('plotproof_user', JSON.stringify(me));
        } catch (e) {
          console.warn('Session expired or invalid, clearing local credentials.');
          localStorage.removeItem('plotproof_access_token');
          localStorage.removeItem('plotproof_refresh_token');
          localStorage.removeItem('plotproof_user');
          setUser(null);
        }
      } else {
        // Default to Citizen demo persona for instant friction-free evaluation
        try {
          const res = await apiService.login(DEMO_USERS.CITIZEN.email, DEMO_PASSWORD);
          if (res.user && res.access_token) {
            localStorage.setItem('plotproof_access_token', res.access_token);
            if (res.refresh_token) localStorage.setItem('plotproof_refresh_token', res.refresh_token);
            localStorage.setItem('plotproof_user', JSON.stringify(res.user));
            setUser(res.user);
          }
        } catch (e) {
          // Backend might not be running yet during static builds
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await apiService.login(email, password);
      localStorage.setItem('plotproof_access_token', res.access_token);
      if (res.refresh_token) {
        localStorage.setItem('plotproof_refresh_token', res.refresh_token);
      }
      if (res.user) {
        localStorage.setItem('plotproof_user', JSON.stringify(res.user));
        setUser(res.user);
      } else {
        const me = await apiService.getMe();
        localStorage.setItem('plotproof_user', JSON.stringify(me));
        setUser(me);
      }
      setIsAuthModalOpen(false);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: { email: string; password: string; full_name: string; phone?: string }) => {
    setIsLoading(true);
    try {
      await apiService.register(data);
      // Auto-login after registration
      await login(data.email, data.password);
    } finally {
      setIsLoading(false);
    }
  };

  const quickSwitchRole = async (role: UserRole) => {
    setIsLoading(true);
    try {
      const demoAccount = DEMO_USERS[role];
      const res = await apiService.login(demoAccount.email, DEMO_PASSWORD);
      localStorage.setItem('plotproof_access_token', res.access_token);
      if (res.refresh_token) {
        localStorage.setItem('plotproof_refresh_token', res.refresh_token);
      }
      if (res.user) {
        localStorage.setItem('plotproof_user', JSON.stringify(res.user));
        setUser(res.user);
      }
      setIsAuthModalOpen(false);
    } catch (err) {
      console.error('Error switching demo role:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('plotproof_refresh_token') || undefined;
    await apiService.logout(refreshToken);
    localStorage.removeItem('plotproof_access_token');
    localStorage.removeItem('plotproof_refresh_token');
    localStorage.removeItem('plotproof_user');
    setUser(null);
  };

  const hasRole = useCallback((...roles: UserRole[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role);
  }, [user]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        isAuthModalOpen,
        openAuthModal: () => setIsAuthModalOpen(true),
        closeAuthModal: () => setIsAuthModalOpen(false),
        login,
        register,
        quickSwitchRole,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
