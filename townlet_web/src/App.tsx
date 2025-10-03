import { useEffect, useMemo, useRef, useState } from "react";
import { HeaderStatus } from "./components/HeaderStatus";
import { AgentSummaryGrid } from "./components/AgentSummaryGrid";
import { NarrationFeed } from "./components/NarrationFeed";
import { PerturbationBanner } from "./components/PerturbationBanner";
import { EconomyUtilitiesPanel } from "./components/EconomyUtilitiesPanel";
import { EmploymentSummary } from "./components/EmploymentSummary";
import { ConflictMetrics } from "./components/ConflictMetrics";
import { KpiPanel } from "./components/KpiPanel";
import { RelationshipOverlay } from "./components/RelationshipOverlay";
import { SocialPanel } from "./components/SocialPanel";
import { LegendPanel } from "./components/LegendPanel";
import { useTelemetryClient } from "./hooks/useTelemetryClient";
import { useAudioCue } from "./hooks/useAudioCue";
import { tokens } from "./theme/tokens";
import {
  selectConflict,
  selectEconomy,
  selectEmployment,
  selectKpis,
  selectPerturbations,
  selectRelationshipOverlays,
  selectSocialEvents,
  selectTransport
} from "./utils/selectors";

export interface AppProps {
  initialSnapshot?: Record<string, unknown> | null;
}

export function App({ initialSnapshot = null }: AppProps) {
  const [audioEnabled, setAudioEnabled] = useState(false);
  const { snapshot, tick, schemaVersion } = useTelemetryClient({
    autoConnect: true,
    initialSnapshot: initialSnapshot as any
  });

  const transport = selectTransport(snapshot);
  const agents = (snapshot?.agents as Array<Record<string, unknown>>) ?? [];
  const narrations = (snapshot?.narrations as Array<Record<string, unknown>>) ?? [];
  const perturbations = selectPerturbations(snapshot);
  const economy = selectEconomy(snapshot);
  const employment = selectEmployment(snapshot);
  const conflict = selectConflict(snapshot);
  const kpis = selectKpis(snapshot);
  const relationships = selectRelationshipOverlays(snapshot);
  const socialEvents = selectSocialEvents(snapshot);

  const { play } = useAudioCue({ enabled: audioEnabled });
  const lastAlertTickRef = useRef<number | null>(null);

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

  useEffect(() => {
    if (!audioEnabled) {
      return;
    }
    const latestAlert = narrationEntries.find((entry) => entry.priority);
    if (latestAlert && (lastAlertTickRef.current ?? -1) < latestAlert.tick) {
      lastAlertTickRef.current = latestAlert.tick;
      play("alert");
    }
  }, [audioEnabled, narrationEntries, play]);

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
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <HeaderStatus schemaVersion={schemaVersion} tick={tick} transportConnected={transport.connected} />
      <div style={{ alignSelf: "flex-end", paddingRight: tokens.spacing.lg }}>
        <label style={{ fontFamily: tokens.typography.fontFamily, fontSize: 13 }}>
          <input
            type="checkbox"
            checked={audioEnabled}
            onChange={(event) => setAudioEnabled(event.target.checked)}
          />
          Enable audio cues
        </label>
      </div>
      <main
        id="main"
        tabIndex={-1}
        style={{
          padding: `0 ${tokens.spacing.lg}px`,
          display: "grid",
          gap: tokens.spacing.lg,
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))"
        }}
      >
        <PerturbationBanner
          active={perturbations.active}
          pending={perturbations.pending}
          cooldowns={perturbations.cooldowns}
        />
        <EconomyUtilitiesPanel settings={economy.settings} utilities={economy.utilities} />
        <EmploymentSummary
          pending={employment.pending}
          pendingCount={employment.pendingCount}
          exitsToday={employment.exitsToday}
          queueLimit={employment.queueLimit}
          reviewWindow={employment.reviewWindow}
        />
        <ConflictMetrics
          cooldownEvents={conflict.cooldownEvents}
          ghostStepEvents={conflict.ghostStepEvents}
          rotationEvents={conflict.rotationEvents}
          rivalryEvents={conflict.rivalryEvents}
        />
        <KpiPanel kpis={kpis} />
        <section style={{ gridColumn: "1 / -1" }}>
          <h2 style={{ fontFamily: tokens.typography.fontFamily, marginBottom: tokens.spacing.md }}>Agents</h2>
          <AgentSummaryGrid agents={agentSummaries} />
        </section>
        <NarrationFeed entries={narrationEntries} />
        <RelationshipOverlay overlays={relationships} />
        <SocialPanel events={socialEvents} />
        <LegendPanel />
      </main>
    </div>
  );
}
