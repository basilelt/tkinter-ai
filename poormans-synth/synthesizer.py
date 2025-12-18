"""
Synthétiseur Audio avec Tkinter
Contrôle de fréquence, ADSR, formes d'onde, filtres et effets
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import threading
import queue
import struct
import math

# Essayer d'importer pyaudio, sinon utiliser une alternative
try:
    import pyaudio
    AUDIO_BACKEND = 'pyaudio'
except ImportError:
    try:
        import sounddevice as sd
        AUDIO_BACKEND = 'sounddevice'
    except ImportError:
        AUDIO_BACKEND = None
        print("⚠️ Installez pyaudio ou sounddevice pour le son:")
        print("   pip install pyaudio")
        print("   ou: pip install sounddevice")

# Constantes audio
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024
CHANNELS = 1

# Couleurs du thème
COLORS = {
    'bg': '#1a1a2e',
    'panel': '#16213e',
    'accent': '#0f3460',
    'highlight': '#e94560',
    'text': '#eaeaea',
    'knob': '#533483',
    'led_on': '#00ff88',
    'led_off': '#004422',
}


class Oscillator:
    """Générateur de formes d'onde"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.phase = 0.0
    
    def generate(self, frequency, num_samples, waveform='sine'):
        """Génère des échantillons audio"""
        t = np.arange(num_samples) / self.sample_rate
        phase_increment = 2 * np.pi * frequency / self.sample_rate
        phases = self.phase + np.cumsum(np.full(num_samples, phase_increment))
        self.phase = phases[-1] % (2 * np.pi)
        
        if waveform == 'sine':
            return np.sin(phases)
        elif waveform == 'square':
            return np.sign(np.sin(phases))
        elif waveform == 'sawtooth':
            return 2 * (phases / (2 * np.pi) % 1) - 1
        elif waveform == 'triangle':
            return 2 * np.abs(2 * (phases / (2 * np.pi) % 1) - 1) - 1
        elif waveform == 'noise':
            return np.random.uniform(-1, 1, num_samples)
        else:
            return np.sin(phases)
    
    def reset(self):
        self.phase = 0.0


class ADSREnvelope:
    """Enveloppe ADSR (Attack, Decay, Sustain, Release)"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.attack = 0.01  # secondes
        self.decay = 0.1
        self.sustain = 0.7  # niveau (0-1)
        self.release = 0.3
        
        self.state = 'idle'  # idle, attack, decay, sustain, release
        self.level = 0.0
        self.release_level = 0.0
    
    def note_on(self):
        self.state = 'attack'
        self.level = 0.0
    
    def note_off(self):
        if self.state != 'idle':
            self.state = 'release'
            self.release_level = self.level
    
    def process(self, num_samples):
        """Génère l'enveloppe pour un bloc d'échantillons"""
        envelope = np.zeros(num_samples)
        
        for i in range(num_samples):
            if self.state == 'idle':
                self.level = 0.0
            
            elif self.state == 'attack':
                if self.attack > 0:
                    self.level += 1.0 / (self.attack * self.sample_rate)
                else:
                    self.level = 1.0
                if self.level >= 1.0:
                    self.level = 1.0
                    self.state = 'decay'
            
            elif self.state == 'decay':
                if self.decay > 0:
                    self.level -= (1.0 - self.sustain) / (self.decay * self.sample_rate)
                else:
                    self.level = self.sustain
                if self.level <= self.sustain:
                    self.level = self.sustain
                    self.state = 'sustain'
            
            elif self.state == 'sustain':
                self.level = self.sustain
            
            elif self.state == 'release':
                if self.release > 0:
                    self.level -= self.release_level / (self.release * self.sample_rate)
                else:
                    self.level = 0.0
                if self.level <= 0.0:
                    self.level = 0.0
                    self.state = 'idle'
            
            envelope[i] = self.level
        
        return envelope


class Filter:
    """Filtre passe-bas simple"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.cutoff = 5000  # Hz
        self.resonance = 0.5
        self.prev_sample = 0.0
    
    def process(self, samples):
        """Applique le filtre"""
        rc = 1.0 / (2 * np.pi * self.cutoff)
        dt = 1.0 / self.sample_rate
        alpha = dt / (rc + dt)
        
        output = np.zeros_like(samples)
        for i, sample in enumerate(samples):
            self.prev_sample = self.prev_sample + alpha * (sample - self.prev_sample)
            output[i] = self.prev_sample + self.resonance * (sample - self.prev_sample)
        
        return output


class LFO:
    """Low Frequency Oscillator pour modulation"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.frequency = 5.0  # Hz
        self.depth = 0.0  # 0-1
        self.phase = 0.0
        self.waveform = 'sine'
    
    def process(self, num_samples):
        """Génère le signal LFO"""
        if self.depth == 0:
            return np.ones(num_samples)
        
        t = np.arange(num_samples) / self.sample_rate
        phase_increment = 2 * np.pi * self.frequency / self.sample_rate
        phases = self.phase + np.cumsum(np.full(num_samples, phase_increment))
        self.phase = phases[-1] % (2 * np.pi)
        
        if self.waveform == 'sine':
            lfo_signal = np.sin(phases)
        elif self.waveform == 'triangle':
            lfo_signal = 2 * np.abs(2 * (phases / (2 * np.pi) % 1) - 1) - 1
        else:
            lfo_signal = np.sin(phases)
        
        # Convertir de -1,1 à 1-depth, 1+depth
        return 1 + self.depth * lfo_signal


class Delay:
    """Effet Delay/Echo"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.time = 0.3  # secondes
        self.feedback = 0.4  # 0-1
        self.mix = 0.0  # 0-1 (dry/wet)
        self.buffer_size = int(sample_rate * 2)  # 2 sec max
        self.buffer = np.zeros(self.buffer_size)
        self.write_pos = 0
    
    def process(self, samples):
        if self.mix == 0:
            return samples
        
        delay_samples = int(self.time * self.sample_rate)
        output = np.zeros_like(samples)
        
        for i, sample in enumerate(samples):
            read_pos = (self.write_pos - delay_samples) % self.buffer_size
            delayed = self.buffer[read_pos]
            
            output[i] = sample * (1 - self.mix) + delayed * self.mix
            self.buffer[self.write_pos] = sample + delayed * self.feedback
            self.write_pos = (self.write_pos + 1) % self.buffer_size
        
        return output


class Arpeggiator:
    """Arpégiateur simple"""
    
    def __init__(self):
        self.enabled = False
        self.speed = 8  # notes par seconde
        self.pattern = 'up'  # up, down, updown
        self.octaves = 1
        self.base_freq = 440
        self.current_step = 0
        self.last_time = 0
        
        # Intervalles pour arpège (en demi-tons)
        self.chord = [0, 4, 7]  # Accord majeur
    
    def get_frequency(self, current_time):
        if not self.enabled:
            return self.base_freq
        
        interval = 1.0 / self.speed
        if current_time - self.last_time >= interval:
            self.last_time = current_time
            self.current_step = (self.current_step + 1) % (len(self.chord) * self.octaves)
        
        # Calculer la note
        step = self.current_step
        if self.pattern == 'down':
            step = (len(self.chord) * self.octaves - 1) - step
        elif self.pattern == 'updown':
            total = len(self.chord) * self.octaves * 2 - 2
            step = self.current_step % total
            if step >= len(self.chord) * self.octaves:
                step = total - step
        
        octave = step // len(self.chord)
        note_in_chord = step % len(self.chord)
        semitones = self.chord[note_in_chord] + octave * 12
        
        return self.base_freq * (2 ** (semitones / 12))


# Presets
PRESETS = {
    'Init': {'wave': 'sine', 'attack': 0.01, 'decay': 0.1, 'sustain': 0.7, 'release': 0.3,
             'cutoff': 5000, 'resonance': 0.5, 'delay_mix': 0, 'delay_time': 0.3},
    'Bass': {'wave': 'sawtooth', 'attack': 0.01, 'decay': 0.2, 'sustain': 0.6, 'release': 0.1,
             'cutoff': 800, 'resonance': 0.7, 'delay_mix': 0, 'delay_time': 0.3},
    'Pad': {'wave': 'sine', 'attack': 0.8, 'decay': 0.5, 'sustain': 0.8, 'release': 1.0,
            'cutoff': 3000, 'resonance': 0.3, 'delay_mix': 0.4, 'delay_time': 0.4},
    'Lead': {'wave': 'square', 'attack': 0.01, 'decay': 0.3, 'sustain': 0.5, 'release': 0.2,
             'cutoff': 4000, 'resonance': 0.6, 'delay_mix': 0.3, 'delay_time': 0.25},
    'Pluck': {'wave': 'triangle', 'attack': 0.001, 'decay': 0.4, 'sustain': 0.0, 'release': 0.3,
              'cutoff': 6000, 'resonance': 0.4, 'delay_mix': 0.2, 'delay_time': 0.15},
}


class Synthesizer:
    """Moteur de synthèse principal"""
    
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.oscillator = Oscillator(self.sample_rate)
        self.oscillator2 = Oscillator(self.sample_rate)
        self.envelope = ADSREnvelope(self.sample_rate)
        self.filter = Filter(self.sample_rate)
        self.lfo = LFO(self.sample_rate)
        self.delay = Delay(self.sample_rate)
        self.arpeggiator = Arpeggiator()
        self.time = 0.0
        
        # Paramètres
        self.frequency = 440.0
        self.volume = 0.5
        self.waveform = 'sine'
        self.waveform2 = 'sine'
        self.osc2_enabled = False
        self.osc2_detune = 0  # cents
        self.osc2_mix = 0.5
        
        self.playing = False
        self.audio_stream = None
        self.audio_thread = None
        self.running = False
    
    def start(self):
        """Démarre le moteur audio"""
        self.running = True
        
        if AUDIO_BACKEND == 'pyaudio':
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=BUFFER_SIZE,
                stream_callback=self._audio_callback_pyaudio
            )
            self.audio_stream.start_stream()
        
        elif AUDIO_BACKEND == 'sounddevice':
            self.audio_stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=CHANNELS,
                blocksize=BUFFER_SIZE,
                callback=self._audio_callback_sounddevice
            )
            self.audio_stream.start()
    
    def stop(self):
        """Arrête le moteur audio"""
        self.running = False
        
        if self.audio_stream:
            if AUDIO_BACKEND == 'pyaudio':
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.pa.terminate()
            elif AUDIO_BACKEND == 'sounddevice':
                self.audio_stream.stop()
                self.audio_stream.close()
    
    def _audio_callback_pyaudio(self, in_data, frame_count, time_info, status):
        """Callback pour PyAudio"""
        samples = self._generate_samples(frame_count)
        return (samples.astype(np.float32).tobytes(), pyaudio.paContinue)
    
    def _audio_callback_sounddevice(self, outdata, frames, time, status):
        """Callback pour sounddevice"""
        samples = self._generate_samples(frames)
        outdata[:, 0] = samples
    
    def _generate_samples(self, num_samples):
        """Génère les échantillons audio"""
        if not self.playing and self.envelope.state == 'idle':
            return np.zeros(num_samples)
        
        self.time += num_samples / self.sample_rate
        
        # Arpégiateur
        if self.arpeggiator.enabled:
            freq = self.arpeggiator.get_frequency(self.time)
        else:
            freq = self.frequency
        
        # LFO pour modulation de fréquence
        lfo_mod = self.lfo.process(num_samples)
        
        # Oscillateur 1
        freq1 = freq * lfo_mod
        samples = self.oscillator.generate(freq1.mean(), num_samples, self.waveform)
        
        # Oscillateur 2 (si activé)
        if self.osc2_enabled:
            detune_factor = 2 ** (self.osc2_detune / 1200)  # cents to ratio
            freq2 = freq * detune_factor * lfo_mod
            samples2 = self.oscillator2.generate(freq2.mean(), num_samples, self.waveform2)
            samples = samples * (1 - self.osc2_mix) + samples2 * self.osc2_mix
        
        # Enveloppe ADSR
        envelope = self.envelope.process(num_samples)
        samples = samples * envelope
        
        # Filtre
        samples = self.filter.process(samples)
        
        # Delay
        samples = self.delay.process(samples)
        
        # Volume
        samples = samples * self.volume
        
        # Limiter
        samples = np.clip(samples, -1.0, 1.0)
        
        return samples
    
    def note_on(self):
        """Déclenche une note"""
        self.playing = True
        self.envelope.note_on()
        self.oscillator.reset()
        self.oscillator2.reset()
    
    def note_off(self):
        """Relâche une note"""
        self.playing = False
        self.envelope.note_off()


class Knob(tk.Canvas):
    """Widget personnalisé pour un potentiomètre rotatif"""
    
    def __init__(self, parent, label, min_val=0, max_val=100, initial=50,
                 command=None, **kwargs):
        super().__init__(parent, width=80, height=100, bg=COLORS['panel'],
                        highlightthickness=0, **kwargs)
        
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.command = command
        self.label = label
        self.dragging = False
        self.last_y = 0
        
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<MouseWheel>', self.on_scroll)
        self.bind('<Button-4>', lambda e: self.on_scroll_linux(1))
        self.bind('<Button-5>', lambda e: self.on_scroll_linux(-1))
        
        self.draw()
    
    def draw(self):
        self.delete('all')
        
        cx, cy = 40, 40
        radius = 28
        
        # Fond du knob
        self.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                        fill=COLORS['knob'], outline=COLORS['highlight'], width=2)
        
        # Indicateur de position
        angle = -135 + (self.value - self.min_val) / (self.max_val - self.min_val) * 270
        angle_rad = math.radians(angle)
        
        x1 = cx + (radius - 8) * math.cos(angle_rad)
        y1 = cy - (radius - 8) * math.sin(angle_rad)
        x2 = cx + (radius - 18) * math.cos(angle_rad)
        y2 = cy - (radius - 18) * math.sin(angle_rad)
        
        self.create_line(x2, y2, x1, y1, fill=COLORS['highlight'], width=3, capstyle='round')
        
        # Arc de progression
        self.create_arc(cx - radius - 5, cy - radius - 5, cx + radius + 5, cy + radius + 5,
                       start=225, extent=-270 * (self.value - self.min_val) / (self.max_val - self.min_val),
                       style='arc', outline=COLORS['led_on'], width=3)
        
        # Label
        self.create_text(cx, 80, text=self.label, fill=COLORS['text'],
                        font=('Arial', 9, 'bold'))
        
        # Valeur
        if self.max_val >= 1000:
            val_text = f"{self.value:.0f}"
        elif self.max_val >= 10:
            val_text = f"{self.value:.1f}"
        else:
            val_text = f"{self.value:.2f}"
        self.create_text(cx, 95, text=val_text, fill=COLORS['highlight'],
                        font=('Arial', 8))
    
    def on_click(self, event):
        self.dragging = True
        self.last_y = event.y
    
    def on_drag(self, event):
        if self.dragging:
            delta = (self.last_y - event.y) * (self.max_val - self.min_val) / 200
            self.value = max(self.min_val, min(self.max_val, self.value + delta))
            self.last_y = event.y
            self.draw()
            if self.command:
                self.command(self.value)
    
    def on_release(self, event):
        self.dragging = False
    
    def on_scroll(self, event):
        delta = (self.max_val - self.min_val) / 50
        if event.delta > 0:
            self.value = min(self.max_val, self.value + delta)
        else:
            self.value = max(self.min_val, self.value - delta)
        self.draw()
        if self.command:
            self.command(self.value)
    
    def on_scroll_linux(self, direction):
        delta = (self.max_val - self.min_val) / 50 * direction
        self.value = max(self.min_val, min(self.max_val, self.value + delta))
        self.draw()
        if self.command:
            self.command(self.value)
    
    def set_value(self, value):
        self.value = max(self.min_val, min(self.max_val, value))
        self.draw()
        if self.command:
            self.command(self.value)
    
    def get_value(self):
        return self.value


class WaveformSelector(tk.Canvas):
    """Sélecteur de forme d'onde visuel"""
    
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(parent, width=200, height=60, bg=COLORS['panel'],
                        highlightthickness=0, **kwargs)
        
        self.waveforms = ['sine', 'square', 'sawtooth', 'triangle', 'noise']
        self.selected = 0
        self.command = command
        
        self.bind('<Button-1>', self.on_click)
        self.draw()
    
    def draw(self):
        self.delete('all')
        
        btn_width = 38
        spacing = 2
        
        for i, wf in enumerate(self.waveforms):
            x = i * (btn_width + spacing) + 5
            y = 5
            
            # Fond du bouton
            color = COLORS['highlight'] if i == self.selected else COLORS['accent']
            self.create_rectangle(x, y, x + btn_width, y + 40,
                                 fill=color, outline=COLORS['text'])
            
            # Dessiner la forme d'onde
            cx = x + btn_width // 2
            cy = y + 20
            
            if wf == 'sine':
                points = [(x + 5 + j, cy - 12 * math.sin(j * math.pi / 14))
                         for j in range(29)]
                self.create_line(*[c for p in points for c in p],
                               fill=COLORS['text'], width=2)
            
            elif wf == 'square':
                self.create_line(x + 5, cy + 10, x + 5, cy - 10,
                               x + 19, cy - 10, x + 19, cy + 10,
                               x + 33, cy + 10, fill=COLORS['text'], width=2)
            
            elif wf == 'sawtooth':
                self.create_line(x + 5, cy + 10, x + 19, cy - 10,
                               x + 19, cy + 10, x + 33, cy - 10,
                               fill=COLORS['text'], width=2)
            
            elif wf == 'triangle':
                self.create_line(x + 5, cy, x + 12, cy - 10,
                               x + 19, cy, x + 26, cy + 10,
                               x + 33, cy, fill=COLORS['text'], width=2)
            
            elif wf == 'noise':
                import random
                points = [(x + 5 + j, cy + random.randint(-10, 10))
                         for j in range(0, 30, 3)]
                self.create_line(*[c for p in points for c in p],
                               fill=COLORS['text'], width=2)
        
        # Label
        self.create_text(100, 55, text=self.waveforms[self.selected].upper(),
                        fill=COLORS['text'], font=('Arial', 8))
    
    def on_click(self, event):
        btn_width = 38
        spacing = 2
        
        for i in range(len(self.waveforms)):
            x = i * (btn_width + spacing) + 5
            if x <= event.x <= x + btn_width and 5 <= event.y <= 45:
                self.selected = i
                self.draw()
                if self.command:
                    self.command(self.waveforms[i])
                break
    
    def get_waveform(self):
        return self.waveforms[self.selected]


class Piano(tk.Canvas):
    """Clavier piano virtuel"""
    
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(parent, width=560, height=120, bg=COLORS['panel'],
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.pressed_key = None
        
        # Notes (2 octaves)
        self.white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] * 2
        self.black_keys = ['C#', 'D#', None, 'F#', 'G#', 'A#', None] * 2
        
        # Fréquences de base (C4 = 261.63 Hz)
        self.base_freq = 261.63
        
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<B1-Motion>', self.on_motion)
        
        self.draw()
    
    def note_to_freq(self, note, octave_offset=0):
        """Convertit une note en fréquence"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        semitone = notes.index(note) + octave_offset * 12
        return self.base_freq * (2 ** (semitone / 12))
    
    def draw(self):
        self.delete('all')
        
        white_width = 40
        white_height = 100
        black_width = 24
        black_height = 60
        
        self.key_rects = []
        
        # Touches blanches
        for i in range(14):
            x = i * white_width
            is_pressed = self.pressed_key == ('white', i)
            color = '#cccccc' if is_pressed else 'white'
            
            self.create_rectangle(x, 10, x + white_width - 2, white_height + 10,
                                 fill=color, outline='#333333', width=1)
            
            note = self.white_keys[i]
            octave = 4 + i // 7
            self.create_text(x + white_width // 2, white_height,
                           text=f"{note}{octave}", fill='#333333',
                           font=('Arial', 8))
            
            self.key_rects.append(('white', i, x, 10, x + white_width - 2, white_height + 10))
        
        # Touches noires
        black_positions = [0, 1, 3, 4, 5]  # Positions relatives dans l'octave
        for i in range(14):
            if self.black_keys[i] is not None:
                x = i * white_width + white_width - black_width // 2
                is_pressed = self.pressed_key == ('black', i)
                color = '#222222' if is_pressed else '#1a1a1a'
                
                self.create_rectangle(x, 10, x + black_width, black_height + 10,
                                     fill=color, outline='#000000', width=1)
                
                self.key_rects.append(('black', i, x, 10, x + black_width, black_height + 10))
    
    def get_key_at(self, x, y):
        """Trouve la touche à une position donnée"""
        # Vérifier d'abord les touches noires (au-dessus)
        for key_type, idx, x1, y1, x2, y2 in reversed(self.key_rects):
            if key_type == 'black' and x1 <= x <= x2 and y1 <= y <= y2:
                return key_type, idx
        
        # Puis les touches blanches
        for key_type, idx, x1, y1, x2, y2 in self.key_rects:
            if key_type == 'white' and x1 <= x <= x2 and y1 <= y <= y2:
                return key_type, idx
        
        return None, None
    
    def on_press(self, event):
        key_type, idx = self.get_key_at(event.x, event.y)
        if key_type is not None:
            self.pressed_key = (key_type, idx)
            self.draw()
            
            if self.command:
                if key_type == 'white':
                    note = self.white_keys[idx]
                    octave_offset = idx // 7
                else:
                    note = self.black_keys[idx]
                    octave_offset = idx // 7
                
                freq = self.note_to_freq(note, octave_offset)
                self.command('note_on', freq)
    
    def on_release(self, event):
        if self.pressed_key is not None:
            self.pressed_key = None
            self.draw()
            if self.command:
                self.command('note_off', 0)
    
    def on_motion(self, event):
        key_type, idx = self.get_key_at(event.x, event.y)
        if key_type is not None and self.pressed_key != (key_type, idx):
            self.pressed_key = (key_type, idx)
            self.draw()
            
            if self.command:
                if key_type == 'white':
                    note = self.white_keys[idx]
                    octave_offset = idx // 7
                else:
                    note = self.black_keys[idx]
                    octave_offset = idx // 7
                
                freq = self.note_to_freq(note, octave_offset)
                self.command('note_on', freq)


class Visualizer(tk.Canvas):
    """Visualiseur d'onde"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=200, height=100, bg='#000000',
                        highlightthickness=1, highlightbackground=COLORS['accent'],
                        **kwargs)
        
        self.data = np.zeros(100)
    
    def update_data(self, synth):
        """Met à jour avec les données du synthétiseur"""
        if synth.playing or synth.envelope.state != 'idle':
            # Générer un aperçu de l'onde
            samples = synth.oscillator.generate(synth.frequency, 100, synth.waveform)
            self.data = samples * synth.envelope.level * synth.volume
        else:
            self.data = np.zeros(100)
        
        self.draw()
    
    def draw(self):
        self.delete('all')
        
        # Grille
        self.create_line(0, 50, 200, 50, fill='#333333', dash=(2, 2))
        
        # Onde
        if np.any(self.data != 0):
            points = []
            for i, sample in enumerate(self.data):
                x = i * 2
                y = 50 - sample * 40
                points.extend([x, y])
            
            if len(points) >= 4:
                self.create_line(*points, fill=COLORS['led_on'], width=2, smooth=True)


class SynthesizerApp:
    """Application principale du synthétiseur"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎹 Python Synthesizer")
        self.root.configure(bg=COLORS['bg'])
        self.root.resizable(False, False)
        
        # Créer le synthétiseur
        self.synth = Synthesizer()
        
        # Interface
        self.create_ui()
        
        # Démarrer le moteur audio
        if AUDIO_BACKEND:
            self.synth.start()
        
        # Mise à jour du visualiseur
        self.update_visualizer()
        
        # Bindings clavier
        self.setup_keyboard()
        
        # Nettoyage à la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COLORS['bg'])
        main_frame.pack(padx=10, pady=10)
        
        # Titre
        title_label = tk.Label(main_frame, text="🎹 PYTHON SYNTHESIZER",
                              bg=COLORS['bg'], fg=COLORS['highlight'],
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 5))
        
        # ===== RANGÉE DU HAUT: OSC + ADSR + FILTER + LFO + OUTPUT =====
        top_row = tk.Frame(main_frame, bg=COLORS['bg'])
        top_row.pack(fill='x', pady=5)
        
        # Section OSC 1
        osc1_frame = tk.LabelFrame(top_row, text="OSC 1",
                                  bg=COLORS['panel'], fg=COLORS['text'],
                                  font=('Arial', 9, 'bold'))
        osc1_frame.pack(side='left', fill='y', padx=2)
        
        self.waveform1 = WaveformSelector(osc1_frame, command=self.on_waveform1_change)
        self.waveform1.pack(padx=5, pady=5)
        
        # Section OSC 2
        osc2_frame = tk.LabelFrame(top_row, text="OSC 2",
                                  bg=COLORS['panel'], fg=COLORS['text'],
                                  font=('Arial', 9, 'bold'))
        osc2_frame.pack(side='left', fill='y', padx=2)
        
        osc2_top = tk.Frame(osc2_frame, bg=COLORS['panel'])
        osc2_top.pack()
        
        self.osc2_var = tk.BooleanVar(value=False)
        self.osc2_check = tk.Checkbutton(osc2_top, text="ON", variable=self.osc2_var,
                                         bg=COLORS['panel'], fg=COLORS['text'],
                                         selectcolor=COLORS['accent'],
                                         font=('Arial', 8),
                                         command=self.on_osc2_toggle)
        self.osc2_check.pack(side='left')
        
        self.waveform2 = WaveformSelector(osc2_frame, command=self.on_waveform2_change)
        self.waveform2.pack(padx=5, pady=2)
        
        osc2_knobs = tk.Frame(osc2_frame, bg=COLORS['panel'])
        osc2_knobs.pack()
        
        self.detune_knob = Knob(osc2_knobs, "Detune", -100, 100, 0,
                               command=self.on_detune_change)
        self.detune_knob.pack(side='left')
        
        self.mix_knob = Knob(osc2_knobs, "Mix", 0, 1, 0.5,
                            command=self.on_mix_change)
        self.mix_knob.pack(side='left')
        
        # Section ADSR
        adsr_frame = tk.LabelFrame(top_row, text="ADSR",
                                  bg=COLORS['panel'], fg=COLORS['text'],
                                  font=('Arial', 9, 'bold'))
        adsr_frame.pack(side='left', fill='y', padx=2)
        
        adsr_knobs = tk.Frame(adsr_frame, bg=COLORS['panel'])
        adsr_knobs.pack(padx=5, pady=5)
        
        self.attack_knob = Knob(adsr_knobs, "A", 0.001, 2, 0.01,
                               command=self.on_attack_change)
        self.attack_knob.pack(side='left', padx=2)
        
        self.decay_knob = Knob(adsr_knobs, "D", 0.001, 2, 0.1,
                              command=self.on_decay_change)
        self.decay_knob.pack(side='left', padx=2)
        
        self.sustain_knob = Knob(adsr_knobs, "S", 0, 1, 0.7,
                                command=self.on_sustain_change)
        self.sustain_knob.pack(side='left', padx=2)
        
        self.release_knob = Knob(adsr_knobs, "R", 0.001, 3, 0.3,
                                command=self.on_release_change)
        self.release_knob.pack(side='left', padx=2)
        
        # Visualiseur ADSR
        self.adsr_viz = tk.Canvas(adsr_frame, width=120, height=60,
                                  bg='#000000', highlightthickness=1,
                                  highlightbackground=COLORS['accent'])
        self.adsr_viz.pack(padx=5, pady=5)
        self.draw_adsr_viz()
        
        # Section Filtre
        filter_frame = tk.LabelFrame(top_row, text="FILTER",
                                    bg=COLORS['panel'], fg=COLORS['text'],
                                    font=('Arial', 9, 'bold'))
        filter_frame.pack(side='left', fill='y', padx=2)
        
        filter_knobs = tk.Frame(filter_frame, bg=COLORS['panel'])
        filter_knobs.pack(padx=5, pady=5)
        
        self.cutoff_knob = Knob(filter_knobs, "Cutoff", 100, 10000, 5000,
                               command=self.on_cutoff_change)
        self.cutoff_knob.pack(side='left', padx=2)
        
        self.resonance_knob = Knob(filter_knobs, "Reso", 0, 1, 0.5,
                                  command=self.on_resonance_change)
        self.resonance_knob.pack(side='left', padx=2)
        
        # Section LFO
        lfo_frame = tk.LabelFrame(top_row, text="LFO",
                                 bg=COLORS['panel'], fg=COLORS['text'],
                                 font=('Arial', 9, 'bold'))
        lfo_frame.pack(side='left', fill='y', padx=2)
        
        lfo_knobs = tk.Frame(lfo_frame, bg=COLORS['panel'])
        lfo_knobs.pack(padx=5, pady=5)
        
        self.lfo_rate_knob = Knob(lfo_knobs, "Rate", 0.1, 20, 5,
                                 command=self.on_lfo_rate_change)
        self.lfo_rate_knob.pack(side='left', padx=2)
        
        self.lfo_depth_knob = Knob(lfo_knobs, "Depth", 0, 0.5, 0,
                                  command=self.on_lfo_depth_change)
        self.lfo_depth_knob.pack(side='left', padx=2)
        
        # Section Output + Visualiseur
        output_frame = tk.LabelFrame(top_row, text="OUTPUT",
                                    bg=COLORS['panel'], fg=COLORS['text'],
                                    font=('Arial', 9, 'bold'))
        output_frame.pack(side='left', fill='y', padx=2)
        
        output_inner = tk.Frame(output_frame, bg=COLORS['panel'])
        output_inner.pack(padx=5, pady=5)
        
        self.volume_knob = Knob(output_inner, "Vol", 0, 1, 0.5,
                               command=self.on_volume_change)
        self.volume_knob.pack(side='left', padx=2)
        
        self.freq_knob = Knob(output_inner, "Freq", 20, 2000, 440,
                             command=self.on_freq_change)
        self.freq_knob.pack(side='left', padx=2)
        
        # Visualiseur
        self.visualizer = Visualizer(output_frame)
        self.visualizer.pack(padx=5, pady=5)
        
        # ===== RANGÉE 2: DELAY + ARPEGGIATOR + PRESETS =====
        fx_row = tk.Frame(main_frame, bg=COLORS['bg'])
        fx_row.pack(fill='x', pady=5)
        
        # Delay
        delay_frame = tk.LabelFrame(fx_row, text="DELAY",
                                   bg=COLORS['panel'], fg=COLORS['text'],
                                   font=('Arial', 9, 'bold'))
        delay_frame.pack(side='left', fill='y', padx=2)
        
        delay_knobs = tk.Frame(delay_frame, bg=COLORS['panel'])
        delay_knobs.pack(padx=5, pady=5)
        
        self.delay_time_knob = Knob(delay_knobs, "Time", 0.05, 1.0, 0.3,
                                   command=self.on_delay_time_change)
        self.delay_time_knob.pack(side='left', padx=2)
        
        self.delay_fb_knob = Knob(delay_knobs, "Feedbk", 0, 0.9, 0.4,
                                 command=self.on_delay_feedback_change)
        self.delay_fb_knob.pack(side='left', padx=2)
        
        self.delay_mix_knob = Knob(delay_knobs, "Mix", 0, 1, 0,
                                  command=self.on_delay_mix_change)
        self.delay_mix_knob.pack(side='left', padx=2)
        
        # Arpeggiator
        arp_frame = tk.LabelFrame(fx_row, text="ARPEGGIATOR",
                                 bg=COLORS['panel'], fg=COLORS['text'],
                                 font=('Arial', 9, 'bold'))
        arp_frame.pack(side='left', fill='y', padx=2)
        
        arp_top = tk.Frame(arp_frame, bg=COLORS['panel'])
        arp_top.pack(pady=2)
        
        self.arp_var = tk.BooleanVar(value=False)
        self.arp_check = tk.Checkbutton(arp_top, text="ON", variable=self.arp_var,
                                        bg=COLORS['panel'], fg=COLORS['led_on'],
                                        selectcolor=COLORS['accent'],
                                        font=('Arial', 9, 'bold'),
                                        command=self.on_arp_toggle)
        self.arp_check.pack(side='left', padx=5)
        
        self.arp_pattern = tk.StringVar(value='up')
        patterns = ['up', 'down', 'updown']
        for p in patterns:
            tk.Radiobutton(arp_top, text=p.upper(), variable=self.arp_pattern, value=p,
                          bg=COLORS['panel'], fg=COLORS['text'], selectcolor=COLORS['accent'],
                          font=('Arial', 8), command=self.on_arp_pattern_change).pack(side='left')
        
        arp_knobs = tk.Frame(arp_frame, bg=COLORS['panel'])
        arp_knobs.pack(padx=5, pady=5)
        
        self.arp_speed_knob = Knob(arp_knobs, "Speed", 1, 20, 8,
                                  command=self.on_arp_speed_change)
        self.arp_speed_knob.pack(side='left', padx=2)
        
        self.arp_oct_knob = Knob(arp_knobs, "Octaves", 1, 4, 1,
                                command=self.on_arp_octaves_change)
        self.arp_oct_knob.pack(side='left', padx=2)
        
        # Presets
        preset_frame = tk.LabelFrame(fx_row, text="PRESETS",
                                    bg=COLORS['panel'], fg=COLORS['text'],
                                    font=('Arial', 9, 'bold'))
        preset_frame.pack(side='left', fill='both', expand=True, padx=2)
        
        preset_inner = tk.Frame(preset_frame, bg=COLORS['panel'])
        preset_inner.pack(padx=10, pady=10)
        
        for preset_name in PRESETS.keys():
            btn = tk.Button(preset_inner, text=preset_name, width=8,
                           bg=COLORS['accent'], fg=COLORS['text'],
                           activebackground=COLORS['highlight'],
                           font=('Arial', 9),
                           command=lambda p=preset_name: self.load_preset(p))
            btn.pack(side='left', padx=3, pady=3)
        
        # ===== RANGÉE DU BAS: CLAVIER PIANO =====
        piano_frame = tk.LabelFrame(main_frame, text="KEYBOARD (A-L keys or click)",
                                   bg=COLORS['panel'], fg=COLORS['text'],
                                   font=('Arial', 9, 'bold'))
        piano_frame.pack(fill='x', pady=5)
        
        self.piano = Piano(piano_frame, command=self.on_piano_event)
        self.piano.pack(padx=5, pady=5)
        
        # Status
        if not AUDIO_BACKEND:
            status = tk.Label(main_frame, 
                            text="⚠️ Audio désactivé - Installez pyaudio ou sounddevice",
                            bg=COLORS['bg'], fg='#ff6b6b', font=('Arial', 9))
            status.pack(pady=2)
    
    def draw_adsr_viz(self):
        """Dessine la visualisation de l'enveloppe ADSR"""
        self.adsr_viz.delete('all')
        
        a = self.synth.envelope.attack
        d = self.synth.envelope.decay
        s = self.synth.envelope.sustain
        r = self.synth.envelope.release
        
        total_time = a + d + 0.3 + r  # 0.3 pour le sustain visible
        
        # Normaliser les temps
        w = 120
        h = 60
        
        ax = int(a / total_time * w)
        dx = int(d / total_time * w)
        sx = int(0.3 / total_time * w)
        rx = int(r / total_time * w)
        
        # Points de l'enveloppe
        points = [
            0, h - 5,  # Début
            ax, 10,  # Fin attack (haut)
            ax + dx, h - 5 - s * (h - 15),  # Fin decay
            ax + dx + sx, h - 5 - s * (h - 15),  # Fin sustain
            w - 5, h - 5  # Fin release
        ]
        
        self.adsr_viz.create_line(*points, fill=COLORS['led_on'], width=2)
        
        # Labels
        self.adsr_viz.create_text(ax // 2, h - 2, text="A", fill=COLORS['text'], font=('Arial', 7))
        self.adsr_viz.create_text(ax + dx // 2, h - 2, text="D", fill=COLORS['text'], font=('Arial', 7))
        self.adsr_viz.create_text(ax + dx + sx // 2, h - 2, text="S", fill=COLORS['text'], font=('Arial', 7))
        self.adsr_viz.create_text(w - rx // 2 - 5, h - 2, text="R", fill=COLORS['text'], font=('Arial', 7))
    
    def setup_keyboard(self):
        """Configure les raccourcis clavier"""
        # Touches pour le piano (AZERTY)
        key_map = {
            'q': ('C', 0), 'z': ('C#', 0), 's': ('D', 0), 'e': ('D#', 0),
            'd': ('E', 0), 'f': ('F', 0), 't': ('F#', 0), 'g': ('G', 0),
            'y': ('G#', 0), 'h': ('A', 0), 'u': ('A#', 0), 'j': ('B', 0),
            'k': ('C', 1), 'o': ('C#', 1), 'l': ('D', 1)
        }
        
        # QWERTY fallback
        key_map.update({
            'a': ('C', 0), 'w': ('C#', 0), 's': ('D', 0), 'e': ('D#', 0),
            'd': ('E', 0), 'f': ('F', 0), 't': ('F#', 0), 'g': ('G', 0),
            'y': ('G#', 0), 'h': ('A', 0), 'u': ('A#', 0), 'j': ('B', 0),
            'k': ('C', 1), 'o': ('C#', 1), 'l': ('D', 1)
        })
        
        self.key_map = key_map
        self.pressed_keys = set()
        
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
    
    def on_key_press(self, event):
        key = event.char.lower()
        if key in self.key_map and key not in self.pressed_keys:
            self.pressed_keys.add(key)
            note, octave = self.key_map[key]
            freq = self.piano.note_to_freq(note, octave)
            self.synth.frequency = freq
            self.freq_knob.set_value(freq)
            self.synth.note_on()
    
    def on_key_release(self, event):
        key = event.char.lower()
        if key in self.pressed_keys:
            self.pressed_keys.discard(key)
            if not self.pressed_keys:
                self.synth.note_off()
    
    # Callbacks pour les contrôles
    def on_waveform1_change(self, waveform):
        self.synth.waveform = waveform
    
    def on_waveform2_change(self, waveform):
        self.synth.waveform2 = waveform
    
    def on_osc2_toggle(self):
        self.synth.osc2_enabled = self.osc2_var.get()
    
    def on_detune_change(self, value):
        self.synth.osc2_detune = value
    
    def on_mix_change(self, value):
        self.synth.osc2_mix = value
    
    def on_attack_change(self, value):
        self.synth.envelope.attack = value
        self.draw_adsr_viz()
    
    def on_decay_change(self, value):
        self.synth.envelope.decay = value
        self.draw_adsr_viz()
    
    def on_sustain_change(self, value):
        self.synth.envelope.sustain = value
        self.draw_adsr_viz()
    
    def on_release_change(self, value):
        self.synth.envelope.release = value
        self.draw_adsr_viz()
    
    def on_cutoff_change(self, value):
        self.synth.filter.cutoff = value
    
    def on_resonance_change(self, value):
        self.synth.filter.resonance = value
    
    def on_lfo_rate_change(self, value):
        self.synth.lfo.frequency = value
    
    def on_lfo_depth_change(self, value):
        self.synth.lfo.depth = value
    
    def on_volume_change(self, value):
        self.synth.volume = value
    
    def on_freq_change(self, value):
        self.synth.frequency = value
    
    def on_piano_event(self, event_type, freq):
        if event_type == 'note_on':
            self.synth.frequency = freq
            self.synth.arpeggiator.base_freq = freq
            self.freq_knob.set_value(freq)
            self.synth.note_on()
        else:
            self.synth.note_off()
    
    # Callbacks pour Delay
    def on_delay_time_change(self, value):
        self.synth.delay.time = value
    
    def on_delay_feedback_change(self, value):
        self.synth.delay.feedback = value
    
    def on_delay_mix_change(self, value):
        self.synth.delay.mix = value
    
    # Callbacks pour Arpeggiator
    def on_arp_toggle(self):
        self.synth.arpeggiator.enabled = self.arp_var.get()
    
    def on_arp_pattern_change(self):
        self.synth.arpeggiator.pattern = self.arp_pattern.get()
    
    def on_arp_speed_change(self, value):
        self.synth.arpeggiator.speed = int(value)
    
    def on_arp_octaves_change(self, value):
        self.synth.arpeggiator.octaves = int(value)
    
    # Presets
    def load_preset(self, preset_name):
        p = PRESETS[preset_name]
        
        # Waveform
        waves = ['sine', 'square', 'sawtooth', 'triangle', 'noise']
        self.waveform1.selected = waves.index(p['wave'])
        self.waveform1.draw()
        self.synth.waveform = p['wave']
        
        # ADSR
        self.attack_knob.set_value(p['attack'])
        self.decay_knob.set_value(p['decay'])
        self.sustain_knob.set_value(p['sustain'])
        self.release_knob.set_value(p['release'])
        
        # Filter
        self.cutoff_knob.set_value(p['cutoff'])
        self.resonance_knob.set_value(p['resonance'])
        
        # Delay
        self.delay_mix_knob.set_value(p['delay_mix'])
        self.delay_time_knob.set_value(p['delay_time'])
        
        self.draw_adsr_viz()
    
    def update_visualizer(self):
        """Met à jour le visualiseur"""
        self.visualizer.update_data(self.synth)
        self.root.after(50, self.update_visualizer)
    
    def on_close(self):
        """Nettoyage à la fermeture"""
        self.synth.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SynthesizerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
