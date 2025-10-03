import type { Meta, StoryObj } from "@storybook/react";
import { PerturbationBanner } from "./PerturbationBanner";
import { EconomyUtilitiesPanel } from "./EconomyUtilitiesPanel";
import { EmploymentSummary } from "./EmploymentSummary";
import { ConflictMetrics } from "./ConflictMetrics";
import { KpiPanel } from "./KpiPanel";
import { RelationshipOverlay } from "./RelationshipOverlay";
import { SocialPanel } from "./SocialPanel";
import { LegendPanel } from "./LegendPanel";

const meta: Meta = {
  title: "Spectator/Panels"
};

export default meta;

type Story = StoryObj;

export const Perturbations: Story = {
  render: () => (
    <PerturbationBanner
      active={[{ id: "outage", data: { severity: "high" } }]}
      pending={[{ id: "market_shock" }]}
      cooldowns={{}}
    />
  )
};

export const EconomyPanel: Story = {
  render: () => (
    <EconomyUtilitiesPanel settings={{ meal_cost: 0.4 }} utilities={{ power: true, water: false }} />
  )
};

export const Employment: Story = {
  render: () => (
    <EmploymentSummary
      pending={["alice"]}
      pendingCount={1}
      exitsToday={0}
      queueLimit={8}
      reviewWindow={1440}
    />
  )
};

export const Conflict: Story = {
  render: () => (
    <ConflictMetrics
      cooldownEvents={1}
      ghostStepEvents={2}
      rotationEvents={3}
      rivalryEvents={[{ tick: 10, agent_a: "alice", agent_b: "bob" }]}
    />
  )
};

export const Kpis: Story = {
  render: () => (
    <KpiPanel kpis={[{ key: "queue_conflict_intensity", latest: 0.4, trend: "up" }]} />
  )
};

export const Relationships: Story = {
  render: () => (
    <RelationshipOverlay overlays={[{ owner: "alice", ties: [{ other: "bob", trust: 0.7 }] }]} />
  )
};

export const Social: Story = {
  render: () => (
    <SocialPanel events={[{ type: "chat_success", payload: { speaker: "alice", listener: "bob" } }]} />
  )
};

export const Legend: Story = {
  render: () => <LegendPanel />
};
