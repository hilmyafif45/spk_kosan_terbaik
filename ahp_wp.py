import numpy as np
import pandas as pd

class AHPWP:
    def __init__(self):
        self.kriteria = ['Biaya', 'Jarak', 'Fasilitas', 'Keamanan', 'Akses']
        self.n = len(self.kriteria)
        self.bobot = None
        self.lambda_max = None
        self.ci = None
        self.cr = None
        self.konsisten = False
        self.alternatif = None

    def create_pairwise_matrix(self):
        """Membuat matriks perbandingan berpasangan AHP"""
        # Matriks perbandingan berpasangan
        A = np.array([
            [1, 1/3, 1/5, 1/7, 1/9],
            [3, 1, 1/3, 1/5, 1/7],
            [5, 3, 1, 1/3, 1/5],
            [7, 5, 3, 1, 1/3],
            [9, 7, 5, 3, 1]
        ])
        return A

    def calculate_weights(self, A):
        """Menghitung bobot menggunakan AHP"""
        # Normalisasi matriks
        normal = A / A.sum(axis=0)
        
        # Menghitung bobot
        self.bobot = normal.mean(axis=1)
        
        return self.bobot

    def check_consistency(self, A):
        """Memeriksa konsistensi matriks AHP"""
        # Menghitung lambda max
        hasil = np.dot(A, self.bobot)
        self.lambda_max = np.mean(hasil / self.bobot)
        
        # Menghitung CI
        self.ci = (self.lambda_max - self.n) / (self.n - 1)
        
        # Menghitung CR dengan RI untuk n=5
        ri = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        self.cr = self.ci / ri.get(self.n, 1.12)
        
        # Cek konsistensi
        self.konsisten = self.cr < 0.1
        
        return self.konsisten

    def calculate_wp(self, alternatif):
        """Menghitung Weighted Product"""
        self.alternatif = alternatif.copy()
        
        # Bobot untuk WP (Biaya adalah cost, lainnya benefit)
        w = self.bobot.copy()
        w[0] = -w[0]  # Biaya sebagai cost
        
        # Menghitung vektor S
        S = []
        for i in range(len(alternatif)):
            nilai = 1
            for j in range(self.n):
                nilai *= alternatif.iloc[i, j] ** w[j]
            S.append(nilai)
        
        self.alternatif['Vektor S'] = S
        
        # Menghitung nilai WP
        self.alternatif['Nilai WP'] = self.alternatif['Vektor S'] / self.alternatif['Vektor S'].sum()
        
        return self.alternatif

    def get_ranking(self):
        """Mendapatkan ranking berdasarkan nilai WP"""
        ranking = self.alternatif.sort_values(
            by='Nilai WP',
            ascending=False
        ).copy()
        
        ranking['Ranking'] = range(1, len(ranking) + 1)
        ranking = ranking.reset_index()
        
        return ranking

    def get_top_n(self, n=3):
        """Mendapatkan N kos terbaik"""
        ranking = self.get_ranking()
        return ranking.head(n)