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
      personalities
    } as any;

    render(<App initialSnapshot={mockTelemetryState.snapshot as any} />);

    expect(screen.getByText(/avery/i)).toBeInTheDocument();
    expect(screen.getByText(/blair/i)).toBeInTheDocument();

    const profileSelect = screen.getByLabelText(/personality profile/i);
    fireEvent.change(profileSelect, { target: { value: "stoic" } });
    expect(screen.queryByText(/avery/i)).not.toBeInTheDocument();
    expect(screen.getByText(/blair/i)).toBeInTheDocument();

    fireEvent.change(profileSelect, { target: { value: "all" } });
    const traitCheckbox = screen.getByLabelText(/enable trait threshold/i);
    fireEvent.click(traitCheckbox);

    const thresholdInput = screen.getByRole("spinbutton", { name: /threshold/i });
    fireEvent.change(thresholdInput, { target: { value: "0.7" } });

    expect(screen.getByText(/avery/i)).toBeInTheDocument();
    expect(screen.queryByText(/blair/i)).not.toBeInTheDocument();
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
    expect(screen.getByText(/avery/i)).toBeInTheDocument();
    expect(screen.getByText(/blair/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/personality profile/i)).not.toBeInTheDocument();
  });
});
