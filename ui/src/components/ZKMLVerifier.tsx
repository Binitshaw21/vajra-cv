import { useState, useRef } from 'react';
import { Lock, Cpu, CheckCircle } from 'lucide-react';
import { apiFetch } from '../api';

interface ZkRecord {
  frame_hash: string;
  weight_commitment: string;
  zk_proof: string;
  proof_generation_ms: number;
}

export default function ZKMLVerifier() {
  const [zkRecord, setZkRecord] = useState<ZkRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [frameName, setFrameName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateProof = async (file?: File) => {
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      if (file) {
        formData.append('frame', file);
        setFrameName(file.name);
      } else {
        setFrameName('Built-in demo frame');
      }
      
      const response = await apiFetch('/api/sota/zkml-verify', { 
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? 'Proof verification failed.');
      setZkRecord(data.record);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Proof verification unavailable.');
    }
    setLoading(false);
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-5 w-full text-slate-200 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-cyan-400 flex items-center">
          <Lock className="w-6 h-6 mr-2" />
          Module 3: zkML Provenance Circuit
        </h3>
        <div className="flex space-x-2">
          <input type="file" ref={fileInputRef} className="hidden" accept="image/*,.npy" onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) generateProof(file);
          }} />
          <button 
            onClick={() => generateProof()}
            disabled={loading}
            className="bg-slate-800 hover:bg-slate-700 border border-slate-600 px-3 py-1 rounded text-sm transition-all flex items-center"
          >
            {loading ? 'Recording...' : 'Run Edge Commitment'}
          </button>
          <button 
            onClick={() => { if (fileInputRef.current) fileInputRef.current.value = ''; fileInputRef.current?.click(); }}
            disabled={loading}
            className="bg-cyan-600 hover:bg-cyan-500 text-white border border-cyan-500 px-3 py-1 rounded text-sm transition-all flex items-center shadow-[0_0_10px_rgba(8,145,178,0.3)]"
          >
            Upload Real Frame
          </button>
        </div>
      </div>

      {zkRecord ? (
        <div className="space-y-4">
          <div className="bg-slate-950 p-4 rounded border border-slate-800 relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded-bl text-xs font-bold flex items-center">
              <CheckCircle className="w-3 h-3 mr-1" /> COMMITMENT RECORDED
            </div>
            
            <div className="grid grid-cols-1 gap-2 font-mono text-xs">
              <div className="flex flex-col">
                <span className="text-slate-500 mb-1">Uploaded frame:</span>
                <span className="text-slate-300 break-all">{frameName}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-slate-500 mb-1">Input Frame Hash (SHA-256):</span>
                <span className="text-slate-300 break-all">{zkRecord.frame_hash}</span>
              </div>
              <div className="flex flex-col mt-2">
                <span className="text-slate-500 mb-1">Classified Weight Commitment:</span>
                <span className="text-amber-400 break-all">{zkRecord.weight_commitment} <span className="text-slate-500">(Weights Hidden)</span></span>
              </div>
              <div className="flex flex-col mt-2">
                <span className="text-slate-500 mb-1">Inference Commitment:</span>
                <span className="text-cyan-400 break-all">{zkRecord.zk_proof}</span>
              </div>
            </div>
          </div>
          <div className="flex justify-between text-xs text-slate-400">
            <span>Proof backend: not configured</span>
            <span>Proof Generation: {zkRecord.proof_generation_ms} ms</span>
          </div>
        </div>
      ) : (
        <div className="h-40 flex flex-col items-center justify-center text-slate-500 bg-slate-950 rounded border border-slate-800 border-dashed">
          <Cpu className="w-8 h-8 mb-2 opacity-50" />
          <p>Awaiting edge node inference trigger...</p>
        </div>
      )}
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
    </div>
  );
}
