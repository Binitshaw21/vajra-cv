import { useEffect, useState } from 'react';
import { Link as LinkIcon, AlertOctagon, CheckCircle2, Server, RefreshCw } from 'lucide-react';
import { apiFetch } from '../api';

interface LedgerStatus {
  integrity_status: string;
  broken_block_id: number | null;
  latest_root_hash: string;
}

export default function MerkleDAGExplorer() {
  const [chain] = useState<{ id: number; root: string; sig: string; intact: boolean; detections: string }[]>([]);
  const [ledgerStatus, setLedgerStatus] = useState<LedgerStatus | null>(null);

  const verifyLedger = () => {
    apiFetch('/api/module3/verify-ledger', { method: 'POST' })
      .then(async res => { const data = await res.json(); if (!res.ok) throw new Error(data.detail ?? 'Ledger verification failed.'); return data; })
      .then(data => setLedgerStatus(data))
      .catch(err => setLedgerStatus({ integrity_status: 'UNAVAILABLE', broken_block_id: null, latest_root_hash: err instanceof Error ? err.message : '' }));
  };

  useEffect(verifyLedger, []);

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 w-full text-slate-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-cyan-400">Module 3: C2PA Merkle DAG Ledger</h3>
        <button onClick={verifyLedger} className="text-slate-400 hover:text-cyan-300" title="Verify ledger now"><RefreshCw className="w-5 h-5" /></button>
      </div>

      <div className="space-y-4">
        {chain.map((block) => (
          <div key={block.id} className={`p-4 rounded border ${block.intact ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-red-500/50 bg-red-500/10'}`}>
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center space-x-2">
                {block.intact ? <CheckCircle2 className="w-5 h-5 text-emerald-400" /> : <AlertOctagon className="w-5 h-5 text-red-400" />}
                <span className="font-mono text-sm font-bold">Block #{block.id}</span>
              </div>
            </div>
            <div className="font-mono text-xs text-slate-400 space-y-1">
              <p><span className="text-slate-500">Root Hash:</span> {block.root}</p>
              <p><span className="text-slate-500">Signature:</span> {block.sig}</p>
              <p><span className="text-slate-500">Payload:</span> <span className={block.intact ? 'text-slate-300' : 'text-red-300'}>{block.detections}</span></p>
            </div>
          </div>
        ))}
        {!chain.length && <div className="p-4 rounded border border-slate-700 text-sm text-slate-400">No persisted ledger blocks are available in this view. Run an inference commit to populate the ledger.</div>}
      </div>
      
      {ledgerStatus && (
        <div className={`mt-4 p-3 rounded-md border text-sm flex items-center justify-between ${ledgerStatus.integrity_status === 'INTACT' ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-red-500/50 bg-red-500/10'}`}>
          <div className="flex items-center space-x-2">
            <Server className="w-4 h-4 text-slate-400" />
            <span className="font-bold text-slate-300">Backend Status: {ledgerStatus.integrity_status}</span>
          </div>
          <div className="font-mono text-xs text-slate-400">
            Hash: {ledgerStatus.latest_root_hash ? ledgerStatus.latest_root_hash.substring(0, 10) + '...' : 'N/A'}
          </div>
        </div>
      )}

      <div className="mt-4 flex items-center justify-center text-slate-500 text-sm">
        <LinkIcon className="w-4 h-4 mr-2" /> Local SQLite WAL Storage • Air-Gapped
      </div>
    </div>
  );
}