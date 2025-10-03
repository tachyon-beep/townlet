import { useMemo } from "react";
import { HeaderStatus } from "./components/HeaderStatus";
import { AgentSummaryGrid } from "./components/AgentSummaryGrid";
import { NarrationFeed } from "./components/NarrationFeed";
import { useTelemetryClient } from "./hooks/useTelemetryClient";
import { tokens } from "./theme/tokens";

export interface AppProps {
  initialSnapshot?: Record<string, unknown> | null;
}

export function App({ initialSnapshot = null }: AppProps) {
  const { snapshot, tick, schemaVersion } = useTelemetryClient({
    autoConnect: false,
    initialSnapshot: initialSnapshot as any
  });

  const transport = snapshot?.transport as { connected?: boolean } | undefined;
  const agents = (snapshot?.agents as Array<Record<string, unknown>>) ?? [];
  const narrations = (snapshot?.narrations as Array<Record<string, unknown>>) ?? [];

  const agentSummaries = useMemo(
    () =>
      agents.map((agent) => ({
        agent_id: String(agent.agent_id ?? agent.id ?? "unknown"),
        wallet: typeof agent.wallet === "number" ? agent.wallet : undefined,
        attendance_ratio:
          typeof agent.attendance_ratio === "number" ? agent.attendance_ratio : undefined,
        shift_state: typeof agent.shift_state === "string" ? agent.shift_state : undefined
      })),
    [agents]
  );

  const narrationEntries = useMemo(
    () =>
      narrations
        .slice(0, 10)
        .map((entry) => ({
          tick: Number(entry.tick ?? 0),
          category: String(entry.category ?? ""),
          message: String(entry.message ?? ""),
          priority: Boolean(entry.priority)
        })),
    [narrations]
  );

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: tokens.color.background,
        color: tokens.color.textPrimary,
        display: "flex",
        flexDirection: "column",
        gap: tokens.spacing.lg,
        paddingBottom: tokens.spacing.xl
      }}
    >
      <HeaderStatus
        schemaVersion={schemaVersion}
        tick={tick}
        transportConnected={transport?.connected ?? null}
      />
      <main style={{ padding: `0 ${tokens.spacing.lg}px`, display: "grid", gap: tokens.spacing.lg }}>
        <section>
          <h2 style={{ fontFamily: tokens.typography.fontFamily, marginBottom: tokens.spacing.md }}>
            Agents
          </h2>
          <AgentSummaryGrid agents={agentSummaries} />
        </section>
        <NarrationFeed entries={narrationEntries} />
      </main>
    </div>
  );
}
