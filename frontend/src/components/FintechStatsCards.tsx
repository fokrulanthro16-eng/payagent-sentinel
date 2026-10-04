import React from 'react';
import { DollarSign, ShieldAlert, CheckCircle2, ShieldCheck, TrendingUp, AlertTriangle } from 'lucide-react';

interface FintechStatsProps {
  totalEscrowVolume: number;
  settledPayouts: number;
  fraudIntercepted: number;
  arbiterStatus: 'ACTIVE' | 'ENGAGED' | 'HALTED';
}

export const FintechStatsCards: React.FC<FintechStatsProps> = ({
  totalEscrowVolume,
  settledPayouts,
  fraudIntercepted,
  arbiterStatus,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Total Escrow Volume */}
      <div className="glass-panel p-5 relative overflow-hidden transition-all duration-300 hover:border-cyan-500/40 group">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
              Total Escrow Volume
            </p>
            <h3 className="text-2xl font-black text-white mt-1 font-mono tracking-tight">
              ${totalEscrowVolume.toFixed(2)}
            </h3>
            <p className="text-[11px] text-cyan-400/80 mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              <span>Multi-Agent Procurement Pipeline</span>
            </p>
          </div>
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-400 shadow-sm shadow-cyan-500/10">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* 2. Settled Payouts */}
      <div className="glass-panel p-5 relative overflow-hidden transition-all duration-300 hover:border-emerald-500/40 group">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
              Settled Payouts
            </p>
            <h3 className="text-2xl font-black text-emerald-300 mt-1 font-mono tracking-tight">
              ${settledPayouts.toFixed(2)}
            </h3>
            <p className="text-[11px] text-emerald-400/80 mt-1 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>SLA Cryptographic Releases</span>
            </p>
          </div>
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 shadow-sm shadow-emerald-500/10">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* 3. Fraud Intercepted */}
      <div className="glass-panel p-5 relative overflow-hidden transition-all duration-300 hover:border-rose-500/40 group">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-rose-500 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
              Fraud Intercepted
            </p>
            <h3 className="text-2xl font-black text-rose-400 mt-1 font-mono tracking-tight drop-shadow-[0_0_10px_rgba(244,63,94,0.4)]">
              ${fraudIntercepted.toFixed(2)}
            </h3>
            <p className="text-[11px] text-rose-400/90 mt-1 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3 text-rose-400" />
              <span>Rogue Drains Hard-Blocked</span>
            </p>
          </div>
          <div className="p-3 bg-rose-500/15 border border-rose-500/30 rounded-xl text-rose-400 shadow-sm shadow-rose-500/20 animate-pulse">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* 4. Zero-Trust Arbiter Status */}
      <div className="glass-panel p-5 relative overflow-hidden transition-all duration-300 hover:border-violet-500/40 group">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-violet-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider font-mono">
              Zero-Trust Arbiter
            </p>
            <h3 className="text-2xl font-black text-white mt-1 font-mono tracking-tight flex items-center gap-2">
              <span className="text-emerald-400 font-bold">100%</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                {arbiterStatus}
              </span>
            </h3>
            <p className="text-[11px] text-violet-400/90 mt-1 flex items-center gap-1 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-ping" />
              <span>Hard Cap: $100.00 / txn</span>
            </p>
          </div>
          <div className="p-3 bg-violet-500/10 border border-violet-500/20 rounded-xl text-violet-400 shadow-sm shadow-violet-500/10">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>
      </div>
    </div>
  );
};
