import React, { useState } from 'react';
import { Play, ShieldAlert, CheckCircle, Zap, Cpu, Terminal } from 'lucide-react';

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
    <div className="bg-[#0e1726] border border-[#1f293d] rounded-xl p-5 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-[#0070ba]/20 border border-[#0070ba]/40 rounded-lg text-[#00e5ff]">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-wide flex items-center gap-2">
              Autonomous Agent Commander
              <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Sentinel Active
              </span>
            </h2>
            <p className="text-xs text-slate-400">Issue natural language procurement goals or trigger adversarial simulations</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-[11px] font-mono text-slate-400 bg-[#080c14] px-3 py-1.5 rounded border border-[#1f293d]">
            HMAC: <span className="text-[#00e5ff]">SHA-256 Dual-Key</span>
          </span>
        </div>
      </div>

      {/* Natural Language Prompt Input Bar */}
      <form onSubmit={handleCustomSubmit} className="relative mb-4">
        <input
          type="text"
          value={customGoal}
          onChange={(e) => setCustomGoal(e.target.value)}
          placeholder="e.g. Procure 8x H100 GPU compute hours for batch model training with max budget $14.50..."
          disabled={loading}
          className="w-full bg-[#080c14] border border-[#1f293d] focus:border-[#0070ba] focus:ring-1 focus:ring-[#0070ba] rounded-lg px-4 py-3 text-sm text-white placeholder-slate-500 outline-none transition-all pl-10"
        />
        <Terminal className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
        <button
          type="submit"
          disabled={loading || !customGoal.trim()}
          className="absolute right-2 top-2 bottom-2 px-4 bg-[#0070ba] hover:bg-[#005ea6] disabled:opacity-50 text-white text-xs font-semibold rounded-md flex items-center space-x-1.5 transition-colors"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Execute</span>
        </button>
      </form>

      {/* Preset Action Buttons */}
      <div className="flex flex-wrap items-center gap-2.5">
        <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 mr-1">
          <Zap className="w-3.5 h-3.5 text-yellow-400" /> Presets:
        </span>

        <button
          onClick={() => onExecute('procure', 'Procure 2x H100 GPU Compute Cluster ($14.50)')}
          disabled={loading}
          className="px-3.5 py-1.5 bg-[#152238] hover:bg-[#1a2b47] border border-[#273854] text-slate-200 text-xs rounded-lg font-medium flex items-center space-x-2 transition-all"
        >
          <Cpu className="w-3.5 h-3.5 text-[#00e5ff]" />
          <span>Procure Compute ($14.50)</span>
        </button>

        <button
          onClick={() => onExecute('legitimate', 'Complete End-to-End Escrow Settlement ($45.00)')}
          disabled={loading}
          className="px-3.5 py-1.5 bg-emerald-950/40 hover:bg-emerald-900/50 border border-emerald-500/30 text-emerald-300 text-xs rounded-lg font-medium flex items-center space-x-2 transition-all"
        >
          <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
          <span>Legitimate Escrow Settlement</span>
        </button>

        <button
          onClick={() => onExecute('rogue_drain')}
          disabled={loading}
          className="px-3.5 py-1.5 bg-rose-950/40 hover:bg-rose-900/50 border border-rose-500/30 text-rose-300 text-xs rounded-lg font-medium flex items-center space-x-2 transition-all ml-auto"
        >
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400 animate-bounce" />
          <span>Simulate Rogue Drain ($1,850)</span>
        </button>

        <button
          onClick={() => onExecute('rogue_vendor')}
          disabled={loading}
          className="px-3.5 py-1.5 bg-amber-950/40 hover:bg-amber-900/50 border border-amber-500/30 text-amber-300 text-xs rounded-lg font-medium flex items-center space-x-2 transition-all"
        >
          <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
          <span>Unauthorized Vendor Attack</span>
        </button>
      </div>
    </div>
  );
};
