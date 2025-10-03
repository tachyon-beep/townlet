import { describe, expect, it } from "vitest";

import { sampleSnapshot } from "../mocks/sampleSnapshot";
import {
  selectTransport,
  selectPerturbations,
  selectEconomy,
  selectEmployment,
  selectConflict,
  selectKpis,
  selectRelationshipOverlays,
  selectSocialEvents
} from "./selectors";

const merged = sampleSnapshot as typeof sampleSnapshot & { payload_type?: string };

describe("selectors", () => {
  it("extracts transport fields", () => {
    const transport = selectTransport(merged as any);
    expect(transport.connected).toBe(true);
  });

  it("extracts perturbations", () => {
    const perturbations = selectPerturbations(merged);
    expect(Array.isArray(perturbations.active)).toBe(true);
  });

  it("extracts economy settings", () => {
    const economy = selectEconomy(merged);
    expect(Object.keys(economy.settings)).toContain("meal_cost");
  });

  it("extracts employment summary", () => {
    const employment = selectEmployment(merged);
    expect(employment.pendingCount).toBeDefined();
  });

  it("extracts conflict metrics", () => {
    const conflict = selectConflict(merged);
    expect(conflict.ghostStepEvents).toBeDefined();
  });

  it("extracts kpis", () => {
    const kpis = selectKpis(merged);
    expect(Array.isArray(kpis)).toBe(true);
  });

  it("extracts relationship overlays", () => {
    const overlays = selectRelationshipOverlays(merged);
    expect(Array.isArray(overlays)).toBe(true);
  });

  it("extracts social events", () => {
    const events = selectSocialEvents(merged);
    expect(Array.isArray(events)).toBe(true);
  });
});
