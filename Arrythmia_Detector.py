import numpy as np
import scipy.signal as signal
import scipy.fftpack as fft
import pandas as pd
from scipy.signal import find_peaks


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

    def detect_couplets(self, file_path, peak_threshold=0.7, window_size=5, rr_threshold=0.8):
        try:
            data = pd.read_csv(file_path, header=None).values
            time = data[:, 0]
            amplitude = data[:, 1]
            norm_amplitude = (amplitude - np.min(amplitude)) / (np.max(amplitude) - np.min(amplitude))
            peaks = []
            for i in range(window_size, len(norm_amplitude) - window_size):
                window = norm_amplitude[i - window_size:i + window_size + 1]
                if norm_amplitude[i] == max(window) and norm_amplitude[i] > peak_threshold:
                    peaks.append(i)
            peaks = np.array(peaks)
            rr_intervals = np.diff(time[peaks])
            couplet_count = 0
            i = 0
            while i < len(rr_intervals) - 2:
                if rr_intervals[i] < rr_threshold and rr_intervals[i+1] < rr_threshold and rr_intervals[i+2] >= rr_threshold:
                    couplet_count += 1
                    i += 3 
                else:
                    i += 1

            if couplet_count > 0:
                    print("Couplets detected")
            else:
                    print("No couplets detected")
        

    

        except Exception as e:
            return f"Error: {str(e)}"       


file_path = "Data/Ventricular Tachycardia.csv"
detector = ArrythmiaDetector()
detector.detect_flutter(file_path)
