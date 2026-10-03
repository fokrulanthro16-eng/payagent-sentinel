import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { ShieldCheck, ShieldAlert, CheckCircle2, Clock } from 'lucide-react';

export interface LedgerRowData {
  id: string;
  timestamp: string;
  action: string;
  targetVendor: string;
  amount: number;
  policyDecision: 'APPROVED' | 'BLOCKED' | 'PENDING';
  paypalOrderId: string;
  riskScore: number;
  status: 'SETTLED' | 'BLOCKED' | 'ESCROW_HELD' | 'NEGOTIATED';
}

interface AGGridLedgerProps {
  rowData: LedgerRowData[];
}

export const AGGridLedger: React.FC<AGGridLedgerProps> = ({ rowData }) => {
  const columnDefs = useMemo<ColDef<LedgerRowData>[]>(() => [
    {
      field: 'timestamp',
      headerName: 'Timestamp',
      width: 140,
      valueFormatter: (params) => {
        if (!params.value) return '';
        const d = new Date(params.value);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      },
    },
    {
      field: 'action',
      headerName: 'Action / Event',
      width: 180,
      cellRenderer: (params: any) => (
        <span className="font-semibold text-slate-200">
          {params.value}
        </span>
      ),
    },
    {
      field: 'targetVendor',
      headerName: 'Target Vendor',
      flex: 1,
      minWidth: 200,
      cellRenderer: (params: any) => (
        <span className="font-mono text-xs text-sky-400">
          {params.value}
        </span>
      ),
    },
    {
      field: 'amount',
      headerName: 'Requested ($)',
      width: 130,
      valueFormatter: (params) => `$${Number(params.value || 0).toFixed(2)}`,
      cellClass: 'font-mono font-bold text-slate-100',
    },
    {
      field: 'policyDecision',
      headerName: 'Policy Decision',
      width: 150,
      cellRenderer: (params: any) => {
        if (params.value === 'APPROVED' || params.value === 'PASSED') {
          return (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              <ShieldCheck className="w-3.5 h-3.5" /> PASSED
            </span>
          );
        }
        if (params.value === 'BLOCKED' || params.value === 'INTERCEPTED') {
          return (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse">
              <ShieldAlert className="w-3.5 h-3.5" /> INTERCEPTED
            </span>
          );
        }
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-500/15 text-slate-400 border border-slate-500/30">
            <Clock className="w-3.5 h-3.5" /> PENDING
          </span>
        );
      },
    },
    {
      field: 'paypalOrderId',
      headerName: 'PayPal Order ID',
      width: 170,
      cellRenderer: (params: any) => (
        <span className="font-mono text-[11px] text-slate-300 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
          {params.value || 'N/A'}
        </span>
      ),
    },
    {
      field: 'riskScore',
      headerName: 'Risk Score',
      width: 110,
      cellRenderer: (params: any) => {
        const val = params.value || 0;
        const color = val > 70 ? 'text-rose-400' : val > 30 ? 'text-amber-400' : 'text-emerald-400';
        return <span className={`font-mono font-bold ${color}`}>{val}/100</span>;
      },
    },
    {
      field: 'status',
      headerName: 'Status Badge',
      width: 150,
      cellRenderer: (params: any) => {
        const status = params.value;
        if (status === 'SETTLED') {
          return (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold bg-emerald-900/40 text-emerald-300 border border-emerald-500/40">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> CAPTURED
            </span>
          );
        }
        if (status === 'BLOCKED') {
          return (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold bg-rose-900/40 text-rose-300 border border-rose-500/40">
              ROGUE BLOCKED
            </span>
          );
        }
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-sky-950/40 text-sky-300 border border-sky-500/30">
            {status}
          </span>
        );
      },
    },
  ], []);

  const defaultColDef = useMemo(() => ({
    sortable: true,
    filter: true,
    resizable: true,
  }), []);

  return (
    <div className="bg-[#0e1726] border border-[#1f293d] rounded-xl p-5 shadow-2xl flex flex-col h-[380px]">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide">
            Cryptographic Audit Ledger & PayPal Escrow Events
          </h2>
          <p className="text-xs text-slate-400">
            Immutable hash-chained records with real-time policy verdicts
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs font-mono text-emerald-400">Live SSE Feed Active</span>
        </div>
      </div>

      <div className="ag-theme-alpine-dark flex-1 w-full rounded-lg overflow-hidden border border-[#1f293d]">
        <AgGridReact
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          animateRows={true}
          getRowClass={(params) => {
            if (params.data?.status === 'SETTLED') return 'bg-emerald-950/20';
            if (params.data?.status === 'BLOCKED') return 'bg-rose-950/25';
            return '';
          }}
        />
      </div>
    </div>
  );
};
