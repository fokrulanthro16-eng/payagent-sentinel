import React, { useState } from 'react';
import { Play, ShieldAlert, CheckCircle, Zap, Cpu, Terminal, Sparkles } from 'lucide-react';

interface PromptCommanderProps {
  onExecute: (type: 'procure' | 'rogue_drain' | 'rogue_vendor' | 'legitimate', customGoal?: string) => Promise<void>;
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
                Zero-Trust Cap: $100.00
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-LLM bilateral negotiation (Gemini 2.5 Flash + Nebius LLaMA-3.3) &bull; PayPal Orders v2 Escrow
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-cyan-300 bg-cyan-950/40 px-3 py-1.5 rounded-lg border border-cyan-500/30 flex items-center gap-1.5 backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Gemini 2.5 Flash Active</span>
          </span>
        </div>
      </div>

      {/* Natural Language Prompt Input Bar */}
      <form onSubmit={handleCustomSubmit} className="relative mb-4">
        <input
          type="text"
          value={customGoal}
          onChange={(e) => setCustomGoal(e.target.value)}
          placeholder="e.g. Procure 4x H100 GPU compute hours for model fine-tuning with $14.50 budget..."
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

      {/* Preset Action Buttons */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5 mr-1 font-mono">
          <Zap className="w-3.5 h-3.5 text-yellow-400" /> Quick Presets:
        </span>

        <button
          onClick={() => onExecute('procure', 'Procure 2x H100 GPU Compute Cluster ($14.50)')}
          disabled={loading}
          className="px-4 py-2 bg-slate-800/60 hover:bg-slate-700/70 border border-slate-600/40 hover:border-cyan-500/50 text-slate-200 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all shadow-sm active:scale-95"
        >
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span>Procure Compute ($14.50)</span>
        </button>

        <button
          onClick={() => onExecute('legitimate', 'End-to-End Escrow Settlement ($45.00)')}
          disabled={loading}
          className="px-4 py-2 bg-emerald-950/40 hover:bg-emerald-900/50 border border-emerald-500/40 text-emerald-300 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all shadow-sm shadow-emerald-500/10 active:scale-95"
        >
          <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
          <span>Legitimate Escrow ($45.00)</span>
        </button>

        <button
          onClick={() => onExecute('rogue_drain')}
          disabled={loading}
          className="px-4 py-2 bg-rose-950/50 hover:bg-rose-900/60 border border-rose-500/40 text-rose-300 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all shadow-md shadow-rose-500/10 active:scale-95 ml-auto"
        >
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
          <span>Simulate Rogue Drain ($1,850) &gt; Cap</span>
        </button>

        <button
          onClick={() => onExecute('rogue_vendor')}
          disabled={loading}
          className="px-4 py-2 bg-amber-950/40 hover:bg-amber-900/50 border border-amber-500/40 text-amber-300 text-xs rounded-xl font-medium flex items-center space-x-2 transition-all shadow-sm active:scale-95"
        >
          <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
          <span>Unauthorized Vendor Attack</span>
        </button>
      </div>
    </div>
  );
};
