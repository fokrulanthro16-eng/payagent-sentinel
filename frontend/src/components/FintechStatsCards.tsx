import { DollarSign, ShieldAlert, CheckCircle2, ShieldCheck, TrendingUp, AlertTriangle, Percent, Sliders } from 'lucide-react';

interface FintechStatsProps {
  totalEscrowVolume: number;
  settledPayouts: number;
  fraudIntercepted: number;
  arbiterStatus: string;
  onOpenVault: () => void;
}

export const FintechStatsCards: React.FC<FintechStatsProps> = ({
  totalEscrowVolume,
  settledPayouts,
  fraudIntercepted,
  arbiterStatus,
  onOpenVault,
}) => {
  const escrowFeeGenerated = settledPayouts * 0.035;

  return (
    <div className="space-y-4">
      {/* 4 Primary Financial Cards */}
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
                <span>Multi-Agent Procurement</span>
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
                <span>Rogue Drains Prevented</span>
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
              <button
                onClick={onOpenVault}
                className="mt-1 text-[11px] text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1 underline underline-offset-2 transition-colors"
              >
                <Sliders className="w-3 h-3" />
                <span>Configure Policy Vault</span>
              </button>
            </div>
            <div className="p-3 bg-violet-500/10 border border-violet-500/20 rounded-xl text-violet-400 shadow-sm shadow-violet-500/10">
              <ShieldCheck className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Enterprise Protection ROI Strip */}
      <div className="glass-panel p-4 flex flex-wrap items-center justify-between gap-4 border border-white/10 bg-slate-900/40">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 border border-cyan-500/30 rounded-lg text-cyan-400">
            <Percent className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white tracking-wide">
              PayPal Enterprise Protection ROI Panel
            </h4>
            <p className="text-[11px] text-slate-400">
              Autonomous Escrow Fee Yield & Prevention Multiplier
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Take-Rate Generated (3.5%):</span>
            <span className="text-cyan-400 font-bold">${escrowFeeGenerated.toFixed(2)}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400">Fraud Loss Prevented:</span>
            <span className="text-rose-400 font-bold">${fraudIntercepted.toFixed(2)}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400">SLA Enforcement Rate:</span>
            <span className="text-emerald-400 font-bold">100.0%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
