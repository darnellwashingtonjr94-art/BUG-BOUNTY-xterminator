"use client";

import { useEffect, useState } from "react";
import { Activity, ShieldAlert, ShieldCheck, Target } from "lucide-react";

interface Finding {
  id: string;
  url: string;
  waf: string;
  anomalyScore: number;
  aiInsight: string;
  status: string;
}

export default function Dashboard() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFindings = async () => {
      try {
        const res = await fetch("/api/findings");
        const data = await res.json();
        setFindings(data.findings);
      } catch (error) {
        console.error("Failed to fetch swarm data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchFindings();
    // Poll the swarm state every 10 seconds
    const interval = setInterval(fetchFindings, 10000);
    return () => clearInterval(interval);
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-red-400 bg-red-400/10 border-red-400/20";
    if (score >= 0.5) return "text-amber-400 bg-amber-400/10 border-amber-400/20";
    return "text-emerald-400 bg-emerald-400/10 border-emerald-400/20";
  };

  if (loading) {
    return <div className="flex h-64 items-center justify-center text-zinc-500">Syncing with Swarm Event Bus...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-3">
        {/* Metric Cards */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
          <div className="flex items-center gap-4">
            <Target className="h-8 w-8 text-blue-500" />
            <div>
              <p className="text-sm text-zinc-400">Active Targets</p>
              <p className="text-2xl font-bold">{findings.length}</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
          <div className="flex items-center gap-4">
            <ShieldAlert className="h-8 w-8 text-red-500" />
            <div>
              <p className="text-sm text-zinc-400">High Anomalies (&gt;0.8)</p>
              <p className="text-2xl font-bold">
                {findings.filter(f => f.anomalyScore >= 0.8).length}
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
          <div className="flex items-center gap-4">
            <Activity className="h-8 w-8 text-emerald-500" />
            <div>
              <p className="text-sm text-zinc-400">Swarm Status</p>
              <p className="text-2xl font-bold text-emerald-500">Online</p>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-800/50 text-zinc-400">
            <tr>
              <th className="px-6 py-4 font-medium">Target Vector</th>
              <th className="px-6 py-4 font-medium">Infrastructure</th>
              <th className="px-6 py-4 font-medium">ML Anomaly Score</th>
              <th className="px-6 py-4 font-medium">Gemini Swarm Insight</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/50">
            {findings.map((finding) => (
              <tr key={finding.id} className="hover:bg-zinc-800/20 transition-colors">
                <td className="px-6 py-4 font-medium text-blue-400">{finding.url}</td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1.5 rounded-md bg-zinc-800 px-2 py-1 text-xs text-zinc-300">
                    {finding.waf !== "None Detected" ? <ShieldCheck className="h-3 w-3" /> : null}
                    {finding.waf}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex rounded-md border px-2 py-1 text-xs font-semibold ${getScoreColor(finding.anomalyScore)}`}>
                    {(finding.anomalyScore * 100).toFixed(1)}%
                  </span>
                </td>
                <td className="px-6 py-4 text-zinc-300 leading-relaxed">
                  {finding.aiInsight}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
