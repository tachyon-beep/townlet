import { fireEvent, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../App";
import type { TelemetryState } from "../utils/telemetryTypes";

const mockTelemetryState: TelemetryState = {
  snapshot: null,
  tick: null,
  schemaVersion: null
};

vi.mock("../hooks/useTelemetryClient", () => ({
  useTelemetryClient: () => mockTelemetryState
}));

describe("App personality filters", () => {
  const baseAgents = [
    {
      agent_id: "avery",
      wallet: 5,
      attendance_ratio: 0.8,
      shift_state: "on_shift"
    },
    {
      agent_id: "blair",
      wallet: 3,
      attendance_ratio: 0.6,
      shift_state: "off_shift"
    }
  ];

  const personalities = {
    avery: {
      profile: "socialite",
      traits: { extroversion: 0.8, forgiveness: 0.2, ambition: 0.3 }
    },
    blair: {
      profile: "stoic",
      traits: { extroversion: -0.2, forgiveness: 0.5, ambition: 0.1 }
    }
  };

  beforeEach(() => {
    mockTelemetryState.tick = 42;
    mockTelemetryState.schemaVersion = "1.0.0";
  });

  afterEach(() => {
    mockTelemetryState.snapshot = null;
  });

  it("filters agents by profile and trait when personality data is present", () => {
    mockTelemetryState.snapshot = {
      schema_version: "1.0.0",
      tick: 42,
      agents: baseAgents,
      personalities,
      narrations: [
        {
          tick: 5,
          category: "personality_event",
          message: "avery lit up the plaza",
          priority: false
        },
        {
          tick: 6,
          category: "queue_conflict",
          message: "queue conflict at market",
          priority: false
        }
      ]
    } as any;

    render(<App initialSnapshot={mockTelemetryState.snapshot as any} />);

    expect(screen.getByRole("heading", { name: /^avery$/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /^blair$/i })).toBeInTheDocument();
    const personalityToggle = screen.getByLabelText(/show personality stories/i) as HTMLInputElement;
    expect(personalityToggle.checked).toBe(true);
    expect(screen.getByText(/avery lit up the plaza/i)).toBeInTheDocument();

    const profileSelect = screen.getByLabelText(/personality profile/i);
    fireEvent.change(profileSelect, { target: { value: "stoic" } });
    expect(screen.queryByRole("heading", { name: /^avery$/i })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /^blair$/i })).toBeInTheDocument();

    fireEvent.change(profileSelect, { target: { value: "all" } });
    const traitCheckbox = screen.getByLabelText(/enable trait threshold/i);
    fireEvent.click(traitCheckbox);

    const thresholdInput = screen.getByRole("spinbutton", { name: /threshold/i });
    fireEvent.change(thresholdInput, { target: { value: "0.7" } });

    expect(screen.getByRole("heading", { name: /^avery$/i })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /^blair$/i })).not.toBeInTheDocument();

    fireEvent.click(personalityToggle);
    expect(personalityToggle.checked).toBe(false);
    expect(screen.queryByText(/avery lit up the plaza/i)).not.toBeInTheDocument();
  });

  it("shows fallback copy when personality data is missing", () => {
    mockTelemetryState.snapshot = {
      schema_version: "1.0.0",
      tick: 42,
      agents: baseAgents
    } as any;

    render(<App initialSnapshot={mockTelemetryState.snapshot as any} />);

    expect(
      screen.getByText(/personality ui disabled or telemetry missing/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /^avery$/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /^blair$/i })).toBeInTheDocument();
    expect(screen.queryByLabelText(/personality profile/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/show personality stories/i)).not.toBeInTheDocument();
  });
});
