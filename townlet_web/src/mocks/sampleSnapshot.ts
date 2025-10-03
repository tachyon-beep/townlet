export const sampleSnapshot = {
  schema_version: "0.9.7",
  tick: 240,
  transport: {
    connected: true,
    dropped_messages: 0,
    queue_length: 0
  },
  agents: [
    {
      agent_id: "alice",
      wallet: 2.5,
      attendance_ratio: 0.92,
      shift_state: "on_shift"
    },
    {
      agent_id: "bob",
      wallet: 1.8,
      attendance_ratio: 0.78,
      shift_state: "off_shift"
    }
  ],
  narrations: [
    {
      tick: 238,
      category: "utility_outage",
      message: "Power outage resolved for sector 7",
      priority: true
    },
    {
      tick: 240,
      category: "queue_conflict",
      message: "Bob yielded shower queue to Alice",
      priority: false
    }
  ],
  perturbations: {
    active: {
      outage: { severity: "high" }
    },
    pending: [{ id: "market_shock" }],
    cooldowns: {}
  },
  economy_settings: {
    meal_cost: 0.4
  },
  utilities: {
    power: true,
    water: false
  },
  employment: {
    pending: ["alice"],
    pending_count: 1,
    exits_today: 0,
    queue_limit: 8,
    review_window: 1440
  },
  conflict: {
    queues: {
      cooldown_events: 1,
      ghost_step_events: 2,
      rotation_events: 3
    },
    rivalry_events: [{ tick: 239, agent_a: "alice", agent_b: "bob", intensity: 1.2 }]
  },
  kpis: {
    queue_conflict_intensity: [0.2, 0.4],
    employment_lateness: [0.1, 0.05]
  },
  relationship_overlay: {
    alice: [{ other: "bob", trust: 0.7, familiarity: 0.5 }]
  },
  social_events: [{ type: "chat_success", payload: { speaker: "alice", listener: "bob" } }]
} satisfies Record<string, unknown>;
