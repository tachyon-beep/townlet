export const sampleSnapshot = {
  schema_version: "0.9.7",
  tick: 240,
  transport: {
    connected: true
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
  ]
} satisfies Record<string, unknown>;
