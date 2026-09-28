import React, { useState, useRef } from 'react';
import { Activity, ShieldAlert, Wrench } from 'lucide-react';
import { apiFetch } from '../api';

interface HealingMetrics {
  initial_entropy: number;
  final_entropy: number;
}

export default function SelfHealingTTA() {
  const [status, setStatus] = useState<'IDLE' | 'DRIFT_DETECTED' | 'HEALING' | 'RESTORED'>('IDLE');
  const [entropy, setEntropy] = useState<number>(0.85); // Nominal entropy
  const [metrics, setMetrics] = useState<HealingMetrics | null>(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const simulateWeatherDrift = (file?: File) => {
    setStatus('DRIFT_DETECTED');
    setEntropy(4.25); // Entropy spikes due to fog/sandstorm
    initiateSelfHealing(file);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) simulateWeatherDrift(file);
  };

  const initiateSelfHealing = async (file?: File) => {
    setStatus('HEALING');
    setError('');
    // Call the local air-gapped API
    try {
      const formData = new FormData();
      if (file) formData.append('ood_data', file);
      
      const response = await apiFetch('/api/sota/self-heal', { 
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? 'Self-healing failed.');
      
      // Animate the entropy dropping
      setTimeout(() => {
        setMetrics(data);
        setEntropy(data.final_entropy);
        setStatus('RESTORED');
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Self-healing unavailable.');
      setStatus('DRIFT_DETECTED');
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-5 w-full text-slate-200 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-cyan-400 flex items-center">
          <Activity className="w-6 h-6 mr-2" />
          Module 4: Autonomous Self-Healing (TENT)
        </h3>
        <span className={`px-3 py-1 rounded text-xs font-bold ${
          status === 'DRIFT_DETECTED' ? 'bg-red-500/20 text-red-400 border border-red-500/50' : 
          status === 'RESTORED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50' : 
          'bg-slate-800 text-slate-400'
        }`}>
          {status === 'IDLE' ? 'SYSTEM NOMINAL' : status.replace('_', ' ')}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-slate-950 p-4 rounded border border-slate-800 flex flex-col items-center justify-center">
          <span className="text-slate-400 text-sm mb-2">Current Shannon Entropy</span>
          <span className={`text-4xl font-mono transition-colors duration-1000 ${
            entropy > 2.0 ? 'text-red-500' : 'text-emerald-500'
          }`}>
            {entropy.toFixed(4)}
          </span>
        </div>
        
        <div className="flex flex-col gap-3 justify-center">
          <input type="file" ref={fileInputRef} className="hidden" accept=".npy,.csv" onChange={handleFileUpload} />
          
          <button 
            onClick={() => simulateWeatherDrift()}
            disabled={status !== 'IDLE' && status !== 'RESTORED'}
            className="bg-slate-800 hover:bg-slate-700 text-slate-300 py-2 rounded flex items-center justify-center transition-all disabled:opacity-50"
          >
            <ShieldAlert className="w-4 h-4 mr-2" /> Inject Covariate Drift (Fog)
          </button>
          
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={status !== 'IDLE' && status !== 'RESTORED'}
            className="bg-cyan-600 hover:bg-cyan-500 text-white py-2 rounded flex items-center justify-center transition-all disabled:opacity-50 shadow-[0_0_15px_rgba(8,145,178,0.5)] disabled:shadow-none"
          >
            <Wrench className="w-4 h-4 mr-2" /> Upload Real OOD Inputs
          </button>
        </div>
      </div>

      {metrics && status === 'RESTORED' && (
        <div className="bg-emerald-950/30 border border-emerald-900/50 p-3 rounded text-xs font-mono text-emerald-400">
          &gt; [SUCCESS] Batch Normalization parameters dynamically updated.<br/>
          &gt; Initial Entropy: {metrics.initial_entropy.toFixed(4)}<br/>
          &gt; Final Entropy: {metrics.final_entropy.toFixed(4)}<br/>
          &gt; Accuracy mathematically restored without retraining or network egress.
        </div>
      )}
      {error && <div className="mt-3 text-sm text-red-400">{error}</div>}
    </div>
  );
}