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
  selectPersonalities,
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
  const [profileFilter, setProfileFilter] = useState<string>("all");
  const [traitFilter, setTraitFilter] = useState<{
    enabled: boolean;
    key: "extroversion" | "forgiveness" | "ambition";
    comparator: ">=" | "<=";
    threshold: number;
  }>({ enabled: false, key: "extroversion", comparator: ">=", threshold: 0.5 });
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
  const personalities = useMemo(() => selectPersonalities(snapshot), [snapshot]);
  const personalityEnabled = Object.keys(personalities).length > 0;

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

  useEffect(() => {
    if (!personalityEnabled) {
      setProfileFilter("all");
      setTraitFilter((prev) => ({ ...prev, enabled: false }));
    }
  }, [personalityEnabled]);

  const availableProfiles = useMemo(() => {
    const profiles = new Set<string>();
    Object.values(personalities).forEach((entry) => {
      profiles.add(entry.profile);
    });
    return Array.from(profiles).sort((a, b) => a.localeCompare(b));
  }, [personalities]);

  const filterApplied = profileFilter !== "all" || traitFilter.enabled;

  const filteredAgents = useMemo(() => {
    if (!personalityEnabled) {
      return agentSummaries;
    }
    return agentSummaries.filter((agent) => {
      const entry = personalities[agent.agent_id];
      if (!entry) {
        return !filterApplied;
      }
      if (profileFilter !== "all" && entry.profile !== profileFilter) {
        return false;
      }
      if (traitFilter.enabled) {
        const value = entry.traits[traitFilter.key];
        if (traitFilter.comparator === ">=" && value < traitFilter.threshold) {
          return false;
        }
        if (traitFilter.comparator === "<=" && value > traitFilter.threshold) {
          return false;
        }
      }
      return true;
    });
  }, [
    agentSummaries,
    personalityEnabled,
    personalities,
    profileFilter,
    traitFilter,
    filterApplied
  ]);

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
          {personalityEnabled ? (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: tokens.spacing.md,
                marginBottom: tokens.spacing.md
              }}
            >
              <label style={{ fontFamily: tokens.typography.fontFamily, fontSize: 13 }}>
                Personality profile
                <select
                  value={profileFilter}
                  onChange={(event) => setProfileFilter(event.target.value)}
                  style={{
                    marginLeft: tokens.spacing.sm,
                    padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px`,
                    borderRadius: 6
                  }}
                  aria-label="Filter agents by personality profile"
                >
                  <option value="all">All profiles</option>
                  {availableProfiles.map((profile) => (
                    <option key={profile} value={profile}>
                      {profile}
                    </option>
                  ))}
                </select>
              </label>
              <fieldset
                style={{
                  border: `1px solid ${tokens.color.textMuted}`,
                  borderRadius: 8,
                  padding: tokens.spacing.sm,
                  minWidth: 220
                }}
              >
                <legend style={{ fontSize: 12 }}>Trait filter</legend>
                <label style={{ display: "flex", alignItems: "center", gap: tokens.spacing.xs }}>
                  <input
                    type="checkbox"
                    checked={traitFilter.enabled}
                    onChange={(event) =>
                      setTraitFilter((prev) => ({ ...prev, enabled: event.target.checked }))
                    }
                    aria-describedby="trait-filter-help"
                  />
                  Enable trait threshold
                </label>
                <div style={{ display: "flex", gap: tokens.spacing.sm, marginTop: tokens.spacing.sm }}>
                  <label style={{ fontSize: 12 }}>
                    Trait
                    <select
                      disabled={!traitFilter.enabled}
                      value={traitFilter.key}
                      onChange={(event) =>
                        setTraitFilter((prev) => ({
                          ...prev,
                          key: event.target.value as typeof prev.key
                        }))
                      }
                      style={{ marginLeft: tokens.spacing.xs }}
                    >
                      <option value="extroversion">Extroversion</option>
                      <option value="forgiveness">Forgiveness</option>
                      <option value="ambition">Ambition</option>
                    </select>
                  </label>
                  <label style={{ fontSize: 12 }}>
                    Comparator
                    <select
                      disabled={!traitFilter.enabled}
                      value={traitFilter.comparator}
                      onChange={(event) =>
                        setTraitFilter((prev) => ({
                          ...prev,
                          comparator: event.target.value as typeof prev.comparator
                        }))
                      }
                      style={{ marginLeft: tokens.spacing.xs }}
                    >
                      <option value=">=">≥</option>
                      <option value="<=">≤</option>
                    </select>
                  </label>
                  <label style={{ fontSize: 12 }}>
                    Threshold
                    <input
                      type="number"
                      step="0.1"
                      min="-1"
                      max="1"
                      disabled={!traitFilter.enabled}
                      value={traitFilter.threshold}
                      onChange={(event) =>
                        setTraitFilter((prev) => ({
                          ...prev,
                          threshold: Number(event.target.value)
                        }))
                      }
                      style={{
                        marginLeft: tokens.spacing.xs,
                        width: 72,
                        padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px`
                      }}
                    />
                  </label>
                </div>
                <p id="trait-filter-help" style={{ fontSize: 11, color: tokens.color.textMuted }}>
                  Filters apply only when personality telemetry is present.
                </p>
              </fieldset>
            </div>
          ) : (
            <p style={{ fontSize: 12, color: tokens.color.textMuted }}>
              Personality UI disabled or telemetry missing; showing baseline agent details.
            </p>
          )}
          <AgentSummaryGrid
            agents={personalityEnabled ? filteredAgents : agentSummaries}
            personalities={personalities}
            personalityEnabled={personalityEnabled}
            filterActive={personalityEnabled && filterApplied}
          />
        </section>
        <NarrationFeed entries={narrationEntries} />
        <RelationshipOverlay overlays={relationships} />
        <SocialPanel events={socialEvents} />
        <LegendPanel />
      </main>
    </div>
  );
}
