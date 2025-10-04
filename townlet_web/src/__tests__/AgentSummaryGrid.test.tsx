import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { AgentSummaryGrid } from "../components/AgentSummaryGrid";
import type { PersonalitySnapshotEntry } from "../utils/telemetryTypes";

describe("AgentSummaryGrid", () => {
  const baseAgents = [
    { agent_id: "avery", wallet: 5, attendance_ratio: 0.8, shift_state: "on_shift" },
    { agent_id: "blair", wallet: 3, attendance_ratio: 0.6, shift_state: "off_shift" }
  ];

  const personalities: Record<string, PersonalitySnapshotEntry> = {
    avery: {
      profile: "socialite",
      traits: { extroversion: 0.7, forgiveness: 0.1, ambition: 0.2 }
    },
    blair: {
      profile: "stoic",
      traits: { extroversion: -0.3, forgiveness: 0.4, ambition: 0.1 }
    }
  } as const;

  it("renders badges and traits when personality data is present", () => {
    render(
      <AgentSummaryGrid
        agents={baseAgents}
        personalities={personalities}
        personalityEnabled
        filterActive={false}
      />
    );

    const badges = screen.getAllByTestId("personality-badge");
    expect(badges).toHaveLength(2);
    expect(badges[0]).toHaveTextContent(/socialite/i);
    expect(badges[0]).toHaveAttribute("title", expect.stringContaining("Profile"));
    expect(screen.getByText(/traits ext \+0\.70/i)).toBeInTheDocument();
  });

  it("falls back to neutral message when no agents match filters", () => {
    render(
      <AgentSummaryGrid
        agents={[]}
        personalities={personalities}
        personalityEnabled
        filterActive
      />
    );

    expect(
      screen.getByText(/no agents match the current personality filters/i)
    ).toBeInTheDocument();
  });

  it("omits badges when personality mode is disabled", () => {
    render(
      <AgentSummaryGrid
        agents={baseAgents}
        personalities={{}}
        personalityEnabled={false}
        filterActive={false}
      />
    );

    expect(screen.queryByTestId("personality-badge")).not.toBeInTheDocument();
    expect(screen.getByText(/avery/)).toBeInTheDocument();
  });
});
