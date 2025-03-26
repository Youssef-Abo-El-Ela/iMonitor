import numpy as np
import scipy.signal as signal
from scipy.signal import find_peaks
import scipy.fftpack as fft

class ArrythmiaDetector:
    def __init__(self):
        pass

    def detect_flutter(self, time, amplitude, target_range=(200, 1000), sampling_rate=1000):
        n = len(amplitude)
        freq = np.fft.fftfreq(n, d=(time[1] - time[0]))
        spectrum = np.abs(fft.fft(amplitude))

        peaks, _ = signal.find_peaks(spectrum, height=np.max(spectrum) * 0.1, width=5)
        peak_freqs = freq[peaks]
        detected_peaks = [f for f in peak_freqs if target_range[0] <= abs(f) <= target_range[1]]

        return bool(detected_peaks)  # Return True if flutter is detected

    def detect_ventricular_tachycardia(self, amplitude):
        p_wave_peaks, _ = find_peaks(amplitude, height=(0.1, 0.25))
        return len(p_wave_peaks) == 0  # Return True if no P-waves (indicating atrial fibrillation)