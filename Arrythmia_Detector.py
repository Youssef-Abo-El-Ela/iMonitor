import numpy as np
import scipy.signal as signal
import scipy.fftpack as fft
import pandas as pd


class ArrythmiaDetector:
    def __init__(self):
        pass

    def detect_flutter(self, file_path, target_range=(200, 1000), sampling_rate=1000):
        data = pd.read_csv(file_path, header=None).values
        time = data[:, 0]
        amplitude = data[:, 1]
        n = len(amplitude)
        freq = np.fft.fftfreq(n, d=(time[1] - time[0]))
        spectrum = np.abs(fft.fft(amplitude))

        peaks, _ = signal.find_peaks(spectrum, height=np.max(spectrum) * 0.1, width=5)
        peak_freqs = freq[peaks]
        detected_peaks = [f for f in peak_freqs if target_range[0] <= abs(f) <= target_range[1]]

        if detected_peaks:
            print("Flutter detected")
        else:
            print("No flutter detected")


file_path = "Data/Ventricular Tachycardia.csv"
detector = ArrythmiaDetector()
detector.detect_flutter(file_path)
