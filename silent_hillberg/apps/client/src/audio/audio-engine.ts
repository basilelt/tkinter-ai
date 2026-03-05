import * as Tone from "tone";

export interface AudioMixSettings {
  master: number;
  music: number;
  sfx: number;
  voice: number;
}

const DEFAULT_MIX: AudioMixSettings = {
  master: 0.82,
  music: 0.62,
  sfx: 0.75,
  voice: 0.55
};

export class AudioEngine {
  private initialized = false;
  private lowAudioMode = false;

  private limiter: Tone.Limiter | null = null;
  private masterBus: Tone.Gain | null = null;
  private musicBus: Tone.Gain | null = null;
  private sfxBus: Tone.Gain | null = null;
  private voiceBus: Tone.Gain | null = null;

  private ambientNoise: Tone.Noise | null = null;
  private ambientFilter: Tone.Filter | null = null;
  private ambientLfo: Tone.LFO | null = null;

  private shotSynth: Tone.MembraneSynth | null = null;
  private hitSynth: Tone.MetalSynth | null = null;
  private killSynth: Tone.FMSynth | null = null;
  private damageSynth: Tone.Synth | null = null;
  private waveSynth: Tone.PolySynth | null = null;

  private settings: AudioMixSettings = { ...DEFAULT_MIX };

  public async start(): Promise<void> {
    if (this.initialized) {
      return;
    }

    await Tone.start();

    this.limiter = new Tone.Limiter(-2).toDestination();
    this.masterBus = new Tone.Gain(this.settings.master).connect(this.limiter);
    this.musicBus = new Tone.Gain(this.settings.music).connect(this.masterBus);
    this.sfxBus = new Tone.Gain(this.settings.sfx).connect(this.masterBus);
    this.voiceBus = new Tone.Gain(this.settings.voice).connect(this.masterBus);

    this.ambientNoise = new Tone.Noise("pink").start();
    this.ambientFilter = new Tone.Filter(240, "lowpass").connect(this.musicBus);
    this.ambientLfo = new Tone.LFO("0.06hz", 170, 330).start();
    this.ambientLfo.connect(this.ambientFilter.frequency);
    this.ambientNoise.connect(this.ambientFilter);

    this.shotSynth = new Tone.MembraneSynth({
      pitchDecay: 0.022,
      octaves: 1.4,
      oscillator: {
        type: "sine"
      },
      envelope: {
        attack: 0.001,
        decay: 0.09,
        sustain: 0,
        release: 0.12
      }
    }).connect(this.sfxBus);

    this.hitSynth = new Tone.MetalSynth({
      octaves: 1.6,
      envelope: {
        attack: 0.001,
        decay: 0.1,
        release: 0.08
      },
      harmonicity: 5.1,
      modulationIndex: 10
    }).connect(this.sfxBus);

    this.killSynth = new Tone.FMSynth({
      harmonicity: 2.2,
      modulationIndex: 16,
      oscillator: {
        type: "triangle"
      },
      envelope: {
        attack: 0.001,
        decay: 0.2,
        sustain: 0,
        release: 0.14
      }
    }).connect(this.voiceBus);

    this.damageSynth = new Tone.Synth({
      oscillator: {
        type: "square"
      },
      envelope: {
        attack: 0.001,
        decay: 0.08,
        sustain: 0,
        release: 0.08
      }
    }).connect(this.voiceBus);

    this.waveSynth = new Tone.PolySynth(Tone.Synth, {
      oscillator: {
        type: "sawtooth"
      },
      envelope: {
        attack: 0.004,
        decay: 0.2,
        sustain: 0.2,
        release: 0.6
      }
    }).connect(this.musicBus);

    this.initialized = true;
  }

  public setMix(settings: Partial<AudioMixSettings>): void {
    this.settings = {
      ...this.settings,
      ...settings
    };

    if (!this.initialized) {
      return;
    }

    this.masterBus?.gain.rampTo(this.settings.master, 0.08);
    this.musicBus?.gain.rampTo(this.settings.music, 0.08);
    this.sfxBus?.gain.rampTo(this.settings.sfx, 0.08);
    this.voiceBus?.gain.rampTo(this.settings.voice, 0.08);
  }

  public setLowAudioMode(enabled: boolean): void {
    this.lowAudioMode = enabled;

    if (!this.initialized) {
      return;
    }

    this.musicBus?.gain.rampTo(enabled ? 0.35 : this.settings.music, 0.25);
  }

  public onPrimaryShot(relativeX = 0): void {
    if (!this.initialized || !this.shotSynth || !this.sfxBus) {
      return;
    }

    const pan = Tone.context.createStereoPanner();
    pan.pan.value = Math.max(-1, Math.min(1, relativeX / 20));
    this.shotSynth.connect(pan);
    const output = Tone.context.createGain();
    output.gain.value = this.lowAudioMode ? 0.6 : 1;
    pan.connect(output);
    output.connect(this.sfxBus.input as AudioNode);

    this.shotSynth.triggerAttackRelease("C1", "16n");

    window.setTimeout(() => {
      this.shotSynth?.disconnect(pan);
      pan.disconnect();
      output.disconnect();
    }, 120);
  }

  public onHit(): void {
    if (!this.initialized || !this.hitSynth) {
      return;
    }

    this.hitSynth.triggerAttackRelease("C5", "32n");
  }

  public onDamage(): void {
    if (!this.initialized || !this.damageSynth) {
      return;
    }

    this.damageSynth.triggerAttackRelease("A2", "32n");
  }

  public onKill(): void {
    if (!this.initialized || !this.killSynth) {
      return;
    }

    this.killSynth.triggerAttackRelease("E2", "16n");
  }

  public onWaveStart(wave: number): void {
    if (!this.initialized || !this.waveSynth) {
      return;
    }

    const notes = wave % 2 === 0 ? ["C3", "G3", "A3"] : ["A2", "E3", "G3"];
    this.waveSynth.triggerAttackRelease(notes, "8n");
  }

  public onExtractionOpen(): void {
    if (!this.initialized || !this.waveSynth) {
      return;
    }

    this.waveSynth.triggerAttackRelease(["D3", "F3", "A3", "C4"], "4n");
  }
}
