import React, { useState } from 'react';
import { Play, ShieldAlert, Zap, Cpu, Terminal, Sparkles, RefreshCcw, UserCheck } from 'lucide-react';

interface PromptCommanderProps {
  onExecute: (type: 'procure' | 'tier2_audit' | 'tier3_human' | 'sla_timeout' | 'rogue_drain' | 'rogue_vendor' | 'legitimate', customGoal?: string) => Promise<void>;
  loading: boolean;
}

export const PromptCommander: React.FC<PromptCommanderProps> = ({ onExecute, loading }) => {
  const [customGoal, setCustomGoal] = useState('');

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customGoal.trim() || loading) return;
    onExecute('procure', customGoal.trim());
    setCustomGoal('');
  };

  return (
    <div className="glass-panel p-6 shadow-2xl relative overflow-hidden transition-all duration-300">
      {/* Glow highlight strip */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#06b6d4] to-transparent opacity-75" />

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-cyan-500/30 rounded-xl text-cyan-400 shadow-lg shadow-cyan-500/10">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-wide flex items-center gap-2">
              Autonomous Agent Commander
              <span className="px-2.5 py-0.5 text-[11px] font-mono rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 shadow-sm shadow-emerald-500/10">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                Zero-Trust Escalations Active
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Tier 1 (&le;$50) Autonomous &bull; Tier 2 ($50-$200) Deep Audit &bull; Tier 3 (&gt;$200) Human Sign-Off &bull; Auto-Refund on SLA Breach
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-cyan-300 bg-cyan-950/40 px-3 py-1.5 rounded-lg border border-cyan-500/30 flex items-center gap-1.5 backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>NVIDIA Nemotron via Nebius</span>
          </span>
        </div>
      </div>

      {/* Natural Language Prompt Input Bar */}
      <form onSubmit={handleCustomSubmit} className="relative mb-4">
        <input
          type="text"
          value={customGoal}
          onChange={(e) => setCustomGoal(e.target.value)}
          placeholder="e.g. Procure 4x H100 GPU compute hours for batch training with $14.50 budget..."
          disabled={loading}
          className="w-full bg-[#0a0f1e]/80 border border-white/10 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 rounded-xl px-4 py-3.5 text-sm text-white placeholder-slate-500 outline-none transition-all pl-11 shadow-inner"
        />
        <Terminal className="w-4 h-4 text-cyan-400 absolute left-4 top-4" />
        <button
          type="submit"
          disabled={loading || !customGoal.trim()}
          className="absolute right-2 top-2 bottom-2 px-5 bg-gradient-to-r from-[#0070ba] to-cyan-500 hover:from-[#005ea6] hover:to-cyan-600 disabled:opacity-40 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 transition-all shadow-md shadow-cyan-500/20 active:scale-95"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Negotiate</span>
        </button>
      </form>

      {/* Preset Action Buttons with Tiers and Auto-Refund */}
      <div className="flex flex-wrap items-center gap-2.5">
        <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 mr-1 font-mono">
          <Zap className="w-3.5 h-3.5 text-yellow-400" /> Enterprise Presets:
        </span>

        {/* Tier 1: Low <= $50 */}
        <button
          onClick={() => onExecute('procure', 'Tier 1 Compute: 2x H100 GPU Batch ($14.50)')}
          disabled={loading}
          className="px-3.5 py-2 bg-slate-800/60 hover:bg-slate-700/70 border border-slate-600/40 hover:border-cyan-500/50 text-slate-200 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all active:scale-95"
        >
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span>Tier 1 Autonomous ($14.50)</span>
        </button>

        {/* Tier 2: Medium $50-$200 */}
        <button
          onClick={() => onExecute('tier2_audit', 'Tier 2 Procurement: Full Fine-tuning Cluster ($120.00)')}
          disabled={loading}
          className="px-3.5 py-2 bg-indigo-950/40 hover:bg-indigo-900/50 border border-indigo-500/40 text-indigo-300 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all active:scale-95"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Tier 2 Nemotron Audit ($120.00)</span>
        </button>

        {/* Tier 3: High > $200 (Requires Human Approval) */}
        <button
          onClick={() => onExecute('tier3_human', 'Tier 3 Heavy Compute Cluster: Multi-Node H100 ($350.00)')}
          disabled={loading}
          className="px-3.5 py-2 bg-amber-950/40 hover:bg-amber-900/50 border border-amber-500/40 text-amber-300 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all active:scale-95"
        >
          <UserCheck className="w-3.5 h-3.5 text-amber-400" />
          <span>Tier 3 Human Escalation ($350.00)</span>
        </button>

        {/* Automated SLA Breach Auto-Refund */}
        <button
          onClick={() => onExecute('sla_timeout', 'Simulate Vendor Delivery Timeout & Escrow Auto-Refund ($35.00)')}
          disabled={loading}
          className="px-3.5 py-2 bg-orange-950/40 hover:bg-orange-900/50 border border-orange-500/40 text-orange-300 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all active:scale-95"
        >
          <RefreshCcw className="w-3.5 h-3.5 text-orange-400" />
          <span>Simulate SLA Auto-Refund</span>
        </button>

        {/* Rogue Drain Hard Block */}
        <button
          onClick={() => onExecute('rogue_drain')}
          disabled={loading}
          className="px-3.5 py-2 bg-rose-950/50 hover:bg-rose-900/60 border border-rose-500/40 text-rose-300 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all ml-auto active:scale-95"
        >
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
          <span>Rogue Drain ($1,850)</span>
        </button>
      </div>
    </div>
  );
};
