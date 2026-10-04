import React, { useState } from 'react';
import { X, Shield, Sliders, Check } from 'lucide-react';

export interface VaultConfig {
  tier_1_max: number;
  tier_2_max: number;
  hard_cap: number;
  hourly_velocity_limit: number;
  take_rate_percentage: number;
  whitelisted_agents: string[];
  blacklisted_agents: string[];
}

interface PolicyVaultDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  config: VaultConfig;
  onSave: (updated: Partial<VaultConfig>) => Promise<void>;
}

export const PolicyVaultDrawer: React.FC<PolicyVaultDrawerProps> = ({
  isOpen,
  onClose,
  config,
  onSave,
}) => {
  const [hardCap, setHardCap] = useState(config.hard_cap);
  const [tier1Max, setTier1Max] = useState(config.tier_1_max);
  const [tier2Max, setTier2Max] = useState(config.tier_2_max);
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    setHardCap(config.hard_cap);
    setTier1Max(config.tier_1_max);
    setTier2Max(config.tier_2_max);
  }, [config]);

  if (!isOpen) return null;

  const handleSaveAll = async () => {
    setSaving(true);
    try {
      await onSave({
        hard_cap: hardCap,
        tier_1_max: tier1Max,
        tier_2_max: tier2Max,
      });
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md bg-[#0a0f1e]/95 border-l border-white/10 h-full p-6 flex flex-col shadow-2xl relative overflow-y-auto">
        {/* Glow accent */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-cyan-400 via-violet-500 to-transparent" />

        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-cyan-500/15 border border-cyan-500/30 rounded-xl text-cyan-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">Enterprise Policy Vault</h2>
              <p className="text-xs text-slate-400">Real-time spend limits & escalation parameters</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Sliders & Configurations */}
        <div className="space-y-6 flex-1">
          {/* 1. Hard Cap Slider ($50 to $500) */}
          <div className="glass-panel p-4 space-y-2">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-slate-300 font-semibold">Per-Transaction Cap</span>
              <span className="text-cyan-400 font-bold text-sm">${hardCap}</span>
            </div>
            <input
              type="range"
              min="50"
              max="500"
              step="10"
              value={hardCap}
              onChange={(e) => setHardCap(Number(e.target.value))}
              className="w-full accent-cyan-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>$50</span>
              <span>$250</span>
              <span>$500</span>
            </div>
          </div>

          {/* 1b. Hourly Velocity Vault */}
          <div className="glass-panel p-4 space-y-2">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-slate-300 font-semibold">Hourly Velocity Vault</span>
              <span className="text-violet-400 font-bold text-sm">${config.hourly_velocity_limit}</span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Hard 24h rolling velocity governor protects against automated multi-agent draining loops.
            </p>
          </div>

          {/* 2. Tier 1 & Tier 2 Thresholds */}
          <div className="glass-panel p-4 space-y-3">
            <h4 className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-violet-400" />
              Escalation Tiers
            </h4>
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-400">Tier 1: Autonomous Max</span>
                <span className="text-emerald-400 font-bold">${tier1Max}</span>
              </div>
              <input
                type="range"
                min="10"
                max="100"
                step="5"
                value={tier1Max}
                onChange={(e) => setTier1Max(Number(e.target.value))}
                className="w-full accent-emerald-400 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-400">Tier 2: Deep Audit Max</span>
                <span className="text-amber-400 font-bold">${tier2Max}</span>
              </div>
              <input
                type="range"
                min="100"
                max="300"
                step="10"
                value={tier2Max}
                onChange={(e) => setTier2Max(Number(e.target.value))}
                className="w-full accent-amber-400 cursor-pointer"
              />
            </div>
            <p className="text-[10px] text-slate-400 font-mono italic">
              Transactions &gt; ${tier2Max} automatically halt in TIER 3 (Pending Human Biometric Sign-off).
            </p>
          </div>

          {/* 3. Whitelisted Agents */}
          <div className="glass-panel p-4 space-y-2">
            <h4 className="text-xs font-mono font-semibold text-slate-300">Whitelisted Entities</h4>
            <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
              {config.whitelisted_agents.map((agent) => (
                <span key={agent} className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/40 text-cyan-300 border border-cyan-500/30">
                  {agent}
                </span>
              ))}
            </div>
          </div>

          {/* 4. Blacklisted Entities */}
          <div className="glass-panel p-4 space-y-2">
            <h4 className="text-xs font-mono font-semibold text-rose-300">Blacklisted Rogue Agents</h4>
            <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
              {config.blacklisted_agents.map((agent) => (
                <span key={agent} className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950/40 text-rose-300 border border-rose-500/30">
                  {agent}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-white/10 flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-white/10 hover:bg-white/5 text-slate-300 text-xs font-semibold transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSaveAll}
            disabled={saving}
            className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-600 hover:to-violet-700 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-1.5 transition-all"
          >
            <Check className="w-4 h-4" />
            <span>{saving ? 'Applying...' : 'Apply Policies'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
