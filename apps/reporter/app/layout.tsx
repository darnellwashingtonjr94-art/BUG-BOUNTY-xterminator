import type { Metadata } from "next";
import "./globals.css"; // Assumes standard Tailwind directives are configured here

export const metadata: Metadata = {
  title: "LLM-x Swarm Observability",
  description: "Autonomous Bug Bounty Triage Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-zinc-100 min-h-screen font-mono antialiased">
        <nav className="border-b border-zinc-800 bg-zinc-900/50 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse" />
            <h1 className="text-xl font-bold tracking-wider text-zinc-100">
              SWARM<span className="text-emerald-500">_OPS</span>
            </h1>
          </div>
          <div className="text-sm text-zinc-400">Target Scope: Global</div>
        </nav>
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
