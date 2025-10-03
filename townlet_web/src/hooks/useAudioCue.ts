import { useEffect, useRef } from "react";

type AudioCue = "alert" | "success";

export interface UseAudioCueOptions {
  enabled: boolean;
  sounds?: Partial<Record<AudioCue, string>>;
}

const DEFAULT_SOUNDS: Record<AudioCue, string> = {
  alert: "/sounds/alert.wav",
  success: "/sounds/success.wav"
};

export function useAudioCue({ enabled, sounds = {} }: UseAudioCueOptions) {
  const audioCache = useRef<Map<AudioCue, HTMLAudioElement>>(new Map());

  useEffect(() => {
    if (!enabled) {
      audioCache.current.clear();
    }
  }, [enabled]);

  const play = (cue: AudioCue) => {
    if (!enabled) return;
    const src = sounds[cue] ?? DEFAULT_SOUNDS[cue];
    if (!src) return;
    let audio = audioCache.current.get(cue);
    if (!audio) {
      audio = new Audio(src);
      audioCache.current.set(cue, audio);
    }
    audio.currentTime = 0;
    void audio.play();
  };

  return { play };
}
