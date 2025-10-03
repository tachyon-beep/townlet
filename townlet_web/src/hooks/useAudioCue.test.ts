import { describe, expect, it, vi } from "vitest";
import { useAudioCue } from "./useAudioCue";
import { renderHook } from "@testing-library/react";

describe("useAudioCue", () => {
  it("does not play when disabled", () => {
    const playSpy = vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue();
    const { result } = renderHook(() => useAudioCue({ enabled: false }));
    result.current.play("alert");
    expect(playSpy).not.toHaveBeenCalled();
    playSpy.mockRestore();
  });
});
