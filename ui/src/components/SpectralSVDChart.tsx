import React, { useEffect, useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, ShieldCheck } from 'lucide-react';
import { apiFetch } from '../api';

export default function SpectralSVDChart() {
  const [data, setData] = useState<{ id: number; score: number }[]>([]);
  const [verdict, setVerdict] = useState<string>('');
  const [flaggedIndices, setFlaggedIndices] = useState<number[]>([]);
  const [threshold, setThreshold] = useState<number>(4.5);
  const [poisonedCount, setPoisonedCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const runAnalysis = (file?: File) => {
    setLoading(true);
    setError('');
    const formData = new FormData();
    if (file) {
      formData.append('features', file);
    }
    
    apiFetch('/api/module1/svd-scan', {
      method: 'POST',
      body: formData
    })
      .then(async res => { const body = await res.json(); if (!res.ok) throw new Error(body.detail ?? 'Analysis failed.'); return body; })
      .then(report => {
        const chartData = report.scores.map((score: number, idx: number) => ({
          id: idx,
          score: score
        }));
        setData(chartData);
        setThreshold(report.threshold);
        setPoisonedCount(report.quarantine_count);
        setVerdict(report.verdict ?? (report.quarantine_count > 0 ? 'COMPROMISED' : 'CLEAN'));
        setFlaggedIndices(report.flagged_indices ?? []);
      })
      .catch(err => { setError(err instanceof Error ? err.message : 'Analysis unavailable.'); setData([]); setPoisonedCount(-1); setVerdict(''); setFlaggedIndices([]); })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    runAnalysis(); // Run with default/real fallback data on load
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) runAnalysis(file);
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 w-full text-slate-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-cyan-400">Module 1: Spectral SVD Screener</h3>
        <div className="flex items-center space-x-3">
          <input type="file" ref={fileInputRef} className="hidden" accept=".npy,.csv" onChange={handleFileUpload} />
          <button onClick={() => { if (fileInputRef.current) fileInputRef.current.value = ''; fileInputRef.current?.click(); }} disabled={loading} className="text-xs bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded border border-slate-600 transition-colors disabled:opacity-60 disabled:cursor-wait">
            {loading ? 'Analyzing...' : 'Upload Real Features (.npy)'}
          </button>
        {error ? (
          <div className="flex items-center text-red-400 bg-red-400/10 px-3 py-1 rounded"><AlertTriangle className="w-5 h-5 mr-2" /><span>{error}</span></div>
        ) : poisonedCount > 0 ? (
          <div className="flex items-center text-red-400 bg-red-400/10 px-3 py-1 rounded">
            <AlertTriangle className="w-5 h-5 mr-2" />
            <span>{poisonedCount} Outliers Flagged</span>
          </div>
        ) : (
          <div className="flex items-center text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded">
            <ShieldCheck className="w-5 h-5 mr-2" />
            <span>Clean Dataset</span>
          </div>
        )}
        </div>
      </div>

      {loading && <div className="mb-4 rounded border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-300">Analyzing feature matrix...</div>}
      {!loading && verdict && !error && <div className={`mb-4 rounded border px-3 py-3 ${poisonedCount > 0 ? 'border-red-500/50 bg-red-500/10 text-red-300' : 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'}`}><strong>{poisonedCount > 0 ? 'FLAGGED' : 'SAFE'}</strong><span className="ml-2">{poisonedCount > 0 ? `${poisonedCount} outliers require review.` : 'No anomalous samples detected.'}</span>{flaggedIndices.length > 0 && <div className="mt-1 text-xs opacity-80">Sample IDs: {flaggedIndices.join(', ')}</div>}</div>}
      {error && <div className="mb-4 rounded border border-red-500/50 bg-red-500/10 px-3 py-2 text-sm text-red-300">Scan failed: {error}</div>}
      
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 30, bottom: 20, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="id" type="number" name="Sample ID" stroke="#94a3b8" />
            <YAxis dataKey="score" type="number" name="Variance Score (τ)" stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#f8fafc' }}
              cursor={{ strokeDasharray: '3 3' }}
            />
            <ReferenceLine y={threshold} stroke="#f59e0b" strokeDasharray="3 3" label={{ position: 'top', value: 'Quarantine Threshold', fill: '#f59e0b' }} />
            <Scatter name="Features" data={data}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.score > threshold ? '#ef4444' : '#10b981'} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}