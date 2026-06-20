import pandas as pd
import numpy as np
import re

class DataProcessor:
    def __init__(self, df):
        self.df = df

    def map_data(self):
        """Mapping data kuesioner ke nilai numerik dengan fleksibilitas tinggi"""
        df_mapped = self.df.copy()
        
        # ==========================================
        # MAPPING BIAYA
        # ==========================================
        biaya_col = None
        for col in df_mapped.columns:
            if 'Biaya' in col and 'Sewa' in col:
                biaya_col = col
                break
        
        if biaya_col:
            def map_biaya(value):
                if pd.isna(value):
                    return np.nan
                value_str = str(value).strip()
                if 'Sangat Murah' in value_str:
                    return 5
                elif 'Murah' in value_str and 'Sangat' not in value_str:
                    return 4
                elif 'Cukup' in value_str:
                    return 3
                elif 'Mahal' in value_str and 'Sangat' not in value_str:
                    return 2
                elif 'Sangat Mahal' in value_str:
                    return 1
                # Fallback: coba deteksi dari angka
                if '500.000' in value_str and '750.000' in value_str:
                    return 4
                elif '751.000' in value_str and '1.000.000' in value_str:
                    return 3
                elif '1.001.000' in value_str and '1.500.000' in value_str:
                    return 2
                return np.nan
            df_mapped['Biaya'] = df_mapped[biaya_col].apply(map_biaya)
        
        # ==========================================
        # MAPPING JARAK
        # ==========================================
        jarak_col = None
        for col in df_mapped.columns:
            if 'Jarak' in col and 'Kampus' in col:
                jarak_col = col
                break
        
        if jarak_col:
            def map_jarak(value):
                if pd.isna(value):
                    return np.nan
                value_str = str(value).strip()
                if 'Sangat Dekat' in value_str:
                    return 5
                elif 'Dekat' in value_str and 'Sangat' not in value_str:
                    return 4
                elif 'Cukup' in value_str:
                    return 3
                elif 'Jauh' in value_str and 'Sangat' not in value_str:
                    return 2
                elif 'Sangat Jauh' in value_str:
                    return 1
                # Fallback: coba deteksi dari jarak
                if '500 m' in value_str or '1.5 km' in value_str:
                    return 4
                elif '1.6 km' in value_str or '3 km' in value_str:
                    return 3
                elif '3.1 km' in value_str or '5 km' in value_str:
                    return 2
                elif '5 km' in value_str and 'Sangat' in value_str:
                    return 1
                return np.nan
            df_mapped['Jarak'] = df_mapped[jarak_col].apply(map_jarak)
        
        # ==========================================
        # MAPPING FASILITAS
        # ==========================================
        fasilitas_col = None
        for col in df_mapped.columns:
            if 'Fasilitas' in col:
                fasilitas_col = col
                break
        
        if fasilitas_col:
            def map_fasilitas(value):
                if pd.isna(value):
                    return np.nan
                value_str = str(value).strip().lower()
                
                # Mapping berdasarkan kata kunci
                if 'pendingin ruangan' in value_str or 'ac' in value_str:
                    return 5
                elif 'kipas angin' in value_str and 'wi-fi' in value_str:
                    return 4
                elif 'wi-fi' in value_str and 'kipas' not in value_str:
                    return 3
                elif 'kamar mandi luar' in value_str and 'kasur' in value_str:
                    return 2
                elif 'kamar kosong' in value_str or 'tanpa perabotan' in value_str:
                    return 1
                elif 'kasur dan lemari' in value_str and 'wi-fi' not in value_str:
                    return 3
                # Fallback
                if 'kasur' in value_str and 'lemari' in value_str:
                    if 'ac' in value_str or 'pendingin' in value_str:
                        return 5
                    elif 'kipas' in value_str:
                        return 4
                    else:
                        return 3
                return np.nan
            df_mapped['Fasilitas'] = df_mapped[fasilitas_col].apply(map_fasilitas)
        
        # ==========================================
        # MAPPING KEAMANAN - MENGGUNAKAN REGEX
        # ==========================================
        keamanan_col = None
        for col in df_mapped.columns:
            if 'Keamanan' in col or 'Lingkungan' in col:
                keamanan_col = col
                break
        
        if keamanan_col:
            def map_keamanan(value):
                if pd.isna(value):
                    return np.nan
                
                value_str = str(value).strip()
                value_lower = value_str.lower()
                
                # Mapping dengan kata kunci
                if 'sangat kondusif' in value_lower:
                    return 5
                elif 'kondusif' in value_lower and 'sangat' not in value_lower and 'cukup' not in value_lower and 'kurang' not in value_lower and 'tidak' not in value_lower:
                    return 4
                elif 'cukup kondusif' in value_lower:
                    return 3
                elif 'kurang kondusif' in value_lower:
                    return 2
                elif 'tidak kondusif' in value_lower:
                    return 1
                
                # Fallback: cek kata kunci individual
                if 'sangat' in value_lower and ('kondusif' in value_lower or 'aman' in value_lower or 'cctv' in value_lower):
                    return 5
                elif 'kondusif' in value_lower and 'cukup' not in value_lower and 'kurang' not in value_lower and 'tidak' not in value_lower:
                    return 4
                elif 'cukup' in value_lower and 'kondusif' in value_lower:
                    return 3
                elif 'kurang' in value_lower and 'kondusif' in value_lower:
                    return 2
                elif 'tidak' in value_lower and 'kondusif' in value_lower:
                    return 1
                elif 'rawan' in value_lower or 'kriminal' in value_lower:
                    return 1
                elif 'cctv' in value_lower or 'penjaga' in value_lower:
                    return 5
                elif 'pagar' in value_lower:
                    return 4
                elif 'banjir' in value_lower and 'bebas' not in value_lower:
                    return 2
                
                # Jika semua gagal, print untuk debugging
                print(f"⚠️ WARNING: Tidak bisa mapping nilai Keamanan: '{value_str}'")
                return np.nan
            
            df_mapped['Keamanan'] = df_mapped[keamanan_col].apply(map_keamanan)
        
        # ==========================================
        # MAPPING AKSES
        # ==========================================
        akses_col = None
        for col in df_mapped.columns:
            if 'Akses' in col or 'Fasilitas Umum' in col:
                akses_col = col
                break
        
        if akses_col:
            def map_akses(value):
                if pd.isna(value):
                    return np.nan
                value_str = str(value).strip()
                if 'Sangat Dekat' in value_str and '100 meter' in value_str:
                    return 5
                elif 'Dekat' in value_str and '100 meter' in value_str:
                    return 4
                elif 'Cukup' in value_str and '301 meter' in value_str:
                    return 3
                elif 'Jauh' in value_str and '501 meter' in value_str:
                    return 2
                elif 'Sangat Jauh' in value_str:
                    return 1
                # Fallback
                if '100 meter' in value_str and 'Sangat' in value_str:
                    return 5
                elif '100 meter' in value_str:
                    return 4
                elif '301 meter' in value_str:
                    return 3
                elif '501 meter' in value_str:
                    return 2
                elif '1 km' in value_str and 'Sangat' in value_str:
                    return 1
                return np.nan
            df_mapped['Akses'] = df_mapped[akses_col].apply(map_akses)
        
        # ==========================================
        # CEK JUMLAH DATA YANG BERHASIL DI-MAPPING
        # ==========================================
        print("\n" + "="*50)
        print("HASIL MAPPING DATA:")
        print("="*50)
        for col in ['Biaya', 'Jarak', 'Fasilitas', 'Keamanan', 'Akses']:
            if col in df_mapped.columns:
                count = df_mapped[col].notna().sum()
                total = len(df_mapped)
                print(f"{col}: {count}/{total} ({count/total*100:.1f}%)")
        print("="*50 + "\n")
        
        return df_mapped

    def get_alternatives(self, df_mapped):
        """Menghitung rata-rata nilai per alternatif"""
        alternatif = df_mapped.groupby('Nama Kos')[
            ['Biaya', 'Jarak', 'Fasilitas', 'Keamanan', 'Akses']
        ].mean()
        return alternatif

    def get_statistics(self):
        """Mendapatkan statistik data"""
        stats = {
            'total_responden': len(self.df),
            'total_kos': self.df['Nama Kos'].nunique(),
            'total_kriteria': 5,
            'nama_kos': self.df['Nama Kos'].unique().tolist(),
            'distribusi_kos': self.df['Nama Kos'].value_counts().to_dict()
        }
        return stats