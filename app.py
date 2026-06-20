import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

from utils.data_processor import DataProcessor
from utils.ahp_wp import AHPWP
from utils.visualizations import Visualizations

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="SPK Pemilihan Kos Terbaik",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS CUSTOM
# ==========================================
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .top-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/student-center.png", width=80)
    st.title("🏠 SPK KOSAN")
    st.markdown("---")
    
    menu = st.radio(
        "📋 Menu Navigasi",
        [
            "🏠 Dashboard",
            "📊 Data Kuesioner",
            "⚙️ Perhitungan AHP-WP",
            "📈 Hasil & Ranking",
            "ℹ️ Tentang"
        ],
        index=0
    )
    
    st.markdown("---")
    st.info("**Metode:** AHP - Weighted Product")
    st.info("**Versi:** 1.0.0")
    
    # Tampilkan status data
    if 'df' in st.session_state:
        st.success("✅ Data sudah diupload")
    else:
        st.warning("⚠️ Belum ada data")

# ==========================================
# MAIN CONTENT
# ==========================================

# Header
st.markdown("""
    <div class="main-header">
        <h1>🏠 Sistem Pendukung Keputusan</h1>
        <h3>Pemilihan Kos Terbaik Menggunakan Metode AHP - WP</h3>
        <p style="opacity: 0.9;">Universitas Pamulang - Viktor</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# FUNGSI UNTUK NORMALISASI KOLOM
# ==========================================
def normalize_columns(df):
    """Normalisasi dan mapping nama kolom"""
    # Hapus kolom duplikat
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Bersihkan nama kolom
    df.columns = df.columns.str.replace('\n', ' ', regex=False)
    df.columns = df.columns.str.strip()
    
    # Mapping nama kolom - lebih spesifik
    column_mapping = {}
    for col in df.columns:
        col_clean = col.replace('\n', ' ').strip()
        
        if 'Biaya' in col_clean and 'Sewa' in col_clean:
            column_mapping[col] = 'Biaya Sewa'
        elif 'Jarak' in col_clean and 'Kampus' in col_clean:
            column_mapping[col] = 'Jarak ke Kampus UNPAM Viktor'
        elif 'Fasilitas' in col_clean and ('interior' in col_clean or 'kelengkapan' in col_clean):
            column_mapping[col] = 'Fasilitas Kos'
        elif 'Keamanan' in col_clean or 'Lingkungan' in col_clean:
            column_mapping[col] = 'Keamanan & Lingkungan'
        elif 'Akses' in col_clean or 'Fasilitas Umum' in col_clean:
            column_mapping[col] = 'Akses Fasilitas Umum'
    
    df.rename(columns=column_mapping, inplace=True)
    
    return df

def load_and_process_data(uploaded_file):
    """Load dan proses data dari file yang diupload"""
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df = normalize_columns(df)
        
        # Simpan ke session state
        st.session_state['df'] = df
        st.session_state['data_loaded'] = True
        
        return df
    return None

# ==========================================
# DASHBOARD
# ==========================================

if menu == "🏠 Dashboard":
    
    st.markdown("### 📂 Upload Data Kuesioner")
    
    uploaded_file = st.file_uploader(
        "Upload file Excel hasil kuesioner",
        type=["xlsx", "xls"],
        help="Upload file dengan format .xlsx atau .xls"
    )
    
    # Proses upload
    if uploaded_file is not None:
        df = load_and_process_data(uploaded_file)
        
        if df is not None:
            # Cek apakah kolom yang dibutuhkan ada
            required_cols = ['Nama Kos', 'Biaya Sewa', 'Jarak ke Kampus UNPAM Viktor', 
                           'Fasilitas Kos', 'Keamanan & Lingkungan', 'Akses Fasilitas Umum']
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Kolom yang hilang: {missing_cols}")
                st.write("Kolom yang tersedia:", df.columns.tolist())
            else:
                # Proses data
                processor = DataProcessor(df)
                stats = processor.get_statistics()
                
                # Menampilkan statistik
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>📝 Responden</h3>
                            <h2>{stats['total_responden']}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>🏘️ Kos</h3>
                            <h2>{stats['total_kos']}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>📊 Kriteria</h3>
                            <h2>{stats['total_kriteria']}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown("""
                        <div class="metric-card">
                            <h3>📈 Metode</h3>
                            <h2 style="font-size: 1.2rem;">AHP-WP</h2>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Distribusi kos
                st.subheader("📊 Distribusi Data Kuesioner")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Distribusi kos
                    dist_data = pd.DataFrame({
                        'Nama Kos': list(stats['distribusi_kos'].keys()),
                        'Jumlah': list(stats['distribusi_kos'].values())
                    })
                    fig = px.pie(
                        dist_data,
                        values='Jumlah',
                        names='Nama Kos',
                        title='Distribusi Responden per Kos',
                        hole=0.3
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Preview data
                    st.markdown("### 📋 Preview Data")
                    preview_cols = ['Nama Kos', 'Biaya Sewa', 'Jarak ke Kampus UNPAM Viktor']
                    available_preview = [col for col in preview_cols if col in df.columns]
                    st.dataframe(
                        df[available_preview].head(),
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Informasi data
                with st.expander("📋 Lihat Data Lengkap"):
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Tombol mulai perhitungan
                if st.button("🚀 Mulai Perhitungan AHP-WP", use_container_width=True):
                    st.success("✅ Data siap diproses! Silahkan pilih menu 'Perhitungan AHP-WP'")
                    st.balloons()
    else:
        # Jika belum ada data di session state, tampilkan info
        if 'df' not in st.session_state:
            st.info("👆 Silahkan upload file Excel untuk memulai analisis.")
        else:
            st.success("✅ Data sudah diupload! Silahkan lanjut ke menu lain.")
            
            # Tampilkan preview data yang sudah ada
            df = st.session_state['df']
            st.markdown("### 📋 Preview Data Saat Ini")
            st.dataframe(df.head(), use_container_width=True, hide_index=True)
        
        # Contoh format
        with st.expander("📖 Format File yang Diharapkan"):
            st.markdown("""
                File Excel harus memiliki kolom-kolom berikut:
                - **Nama Kos**: Nama kos
                - **Biaya Sewa**: Kategori biaya
                - **Jarak ke Kampus UNPAM Viktor**: Kategori jarak
                - **Fasilitas Kos**: Kategori fasilitas
                - **Keamanan & Lingkungan**: Kategori keamanan
                - **Akses Fasilitas Umum**: Kategori akses
            """)

# ==========================================
# DATA KUESIONER
# ==========================================

elif menu == "📊 Data Kuesioner":
    
    st.header("📊 Data Kuesioner")
    
    # Cek apakah data sudah ada di session state
    if 'df' in st.session_state:
        df = st.session_state['df']
        
        st.success(f"✅ Menampilkan data dari {len(df)} responden")
        
        # Tampilkan data original
        st.markdown("### 📋 Data Original (Kategorikal)")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # ==========================================
        # DEBUG - LIHAT NILAI UNIK UNTUK KEAMANAN
        # ==========================================
        st.markdown("---")
        st.markdown("### 🔍 Debug - Nilai Unik Kolom Keamanan")
        
        # Cari kolom Keamanan
        keamanan_col = None
        for col in df.columns:
            if 'Keamanan' in col or 'Lingkungan' in col:
                keamanan_col = col
                break
        
        if keamanan_col:
            st.write(f"Nilai unik di kolom '{keamanan_col}':")
            st.write(df[keamanan_col].unique())
            
            # Tampilkan jumlah masing-masing nilai
            st.write("Jumlah masing-masing nilai:")
            st.write(df[keamanan_col].value_counts())
        else:
            st.warning("⚠️ Kolom Keamanan tidak ditemukan!")
            st.write("Kolom yang tersedia:", df.columns.tolist())
        
        # ==========================================
        # PROSES MAPPING UNTUK STATISTIK
        # ==========================================
        st.markdown("---")
        st.markdown("### 📊 Data Setelah Mapping (Numerik)")
        
        processor = DataProcessor(df)
        df_mapped = processor.map_data()
        
        st.dataframe(df_mapped, use_container_width=True, hide_index=True)
        
        # ==========================================
        # STATISTIK DESKRIPTIF - DATA NUMERIK
        # ==========================================
        st.markdown("---")
        st.markdown("### 📊 Statistik Deskriptif (Data Numerik)")
        
        numeric_cols = ['Biaya', 'Jarak', 'Fasilitas', 'Keamanan', 'Akses']
        available_numeric = [col for col in numeric_cols if col in df_mapped.columns]
        
        if available_numeric:
            # Tampilkan statistik
            st.dataframe(df_mapped[available_numeric].describe(), use_container_width=True)
            
            # Tambahan: Box plot untuk visualisasi
            st.markdown("#### 📈 Visualisasi Distribusi Data Numerik")
            
            # Reshape data untuk boxplot
            df_melted = df_mapped[available_numeric].melt(var_name='Kriteria', value_name='Nilai')
            
            fig = px.box(
                df_melted,
                x='Kriteria',
                y='Nilai',
                title='Distribusi Nilai per Kriteria',
                color='Kriteria',
                points='all'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap korelasi
            st.markdown("#### 🔥 Korelasi Antar Kriteria")
            corr_matrix = df_mapped[available_numeric].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                title='Matriks Korelasi',
                color_continuous_scale='RdBu_r',
                aspect='auto'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("⚠️ Tidak ada data numerik untuk ditampilkan")
        
        # ==========================================
        # STATISTIK DESKRIPTIF - DATA KATEGORIKAL
        # ==========================================
        st.markdown("---")
        st.markdown("### 📊 Statistik Data Kategorikal")
        
        categorical_cols = ['Nama Kos', 'Biaya Sewa', 'Jarak ke Kampus UNPAM Viktor', 
                           'Fasilitas Kos', 'Keamanan & Lingkungan', 'Akses Fasilitas Umum']
        available_cat = [col for col in categorical_cols if col in df.columns]
        
        if available_cat:
            st.dataframe(df[available_cat].describe(include=['object']), use_container_width=True)
            
            # Visualisasi distribusi kategorikal
            st.markdown("#### 📊 Distribusi Data Kategorikal")
            
            # Pilih kolom untuk divisualisasikan
            selected_col = st.selectbox(
                "Pilih kolom untuk melihat distribusi:",
                available_cat
            )
            
            if selected_col:
                fig = px.histogram(
                    df,
                    x=selected_col,
                    title=f'Distribusi {selected_col}',
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data kategorikal untuk ditampilkan")
        
        # ==========================================
        # DOWNLOAD DATA
        # ==========================================
        st.markdown("---")
        st.markdown("### 📥 Download Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download Original Excel", use_container_width=True):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data Original')
                    df_mapped.to_excel(writer, index=False, sheet_name='Data Mapped')
                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name="data_kuesioner.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            csv_original = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Original CSV",
                data=csv_original,
                file_name="data_original.csv",
                mime="text/csv"
            )
        
        with col3:
            csv_mapped = df_mapped.to_csv(index=False)
            st.download_button(
                label="📥 Download Mapped CSV",
                data=csv_mapped,
                file_name="data_mapped.csv",
                mime="text/csv"
            )
            
    else:
        st.warning("⚠️ Belum ada data. Silahkan upload data di menu Dashboard.")
        
        # Upload langsung dari sini
        uploaded_file = st.file_uploader(
            "Upload file Excel",
            type=["xlsx", "xls"],
            key="data_uploader"
        )
        
        if uploaded_file:
            df = load_and_process_data(uploaded_file)
            if df is not None:
                st.success("✅ Data berhasil diupload!")
                st.rerun()

# ==========================================
# PERHITUNGAN AHP-WP
# ==========================================

elif menu == "⚙️ Perhitungan AHP-WP":
    
    st.header("⚙️ Perhitungan AHP dan Weighted Product")
    
    # Cek apakah data sudah ada di session state
    if 'df' not in st.session_state:
        st.warning("⚠️ Silahkan upload data terlebih dahulu di menu Dashboard.")
        
        # Upload langsung dari sini
        uploaded_file = st.file_uploader(
            "Upload file Excel",
            type=["xlsx", "xls"]
        )
        
        if uploaded_file:
            df = load_and_process_data(uploaded_file)
            if df is not None:
                st.success("✅ Data berhasil diupload!")
                st.rerun()
    else:
        df = st.session_state['df']
        
        st.success(f"✅ Menggunakan data dari {len(df)} responden")
        
        # Proses data
        processor = DataProcessor(df)
        df_mapped = processor.map_data()
        alternatif = processor.get_alternatives(df_mapped)
        
        # Tampilkan hasil mapping
        with st.expander("📊 Lihat Data Setelah Mapping"):
            st.dataframe(df_mapped, use_container_width=True, hide_index=True)
        
        # Tampilkan alternatif
        with st.expander("📊 Nilai Alternatif (Rata-rata per Kos)"):
            st.dataframe(alternatif, use_container_width=True)
            
            # Visualisasi alternatif
            fig = px.bar(
                alternatif.reset_index(),
                x='Nama Kos',
                y=['Biaya', 'Jarak', 'Fasilitas', 'Keamanan', 'Akses'],
                title='Perbandingan Nilai per Kos',
                barmode='group'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # AHP
        st.subheader("📊 Perhitungan AHP")
        
        ahp = AHPWP()
        A = ahp.create_pairwise_matrix()
        bobot = ahp.calculate_weights(A)
        konsisten = ahp.check_consistency(A)
        
        # Tampilkan matriks
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Matriks Perbandingan Berpasangan")
            matriks_df = pd.DataFrame(
                A,
                index=ahp.kriteria,
                columns=ahp.kriteria
            )
            st.dataframe(matriks_df, use_container_width=True)
            
            # Heatmap matriks
            fig = px.imshow(
                matriks_df,
                text_auto=True,
                title='Heatmap Matriks Perbandingan',
                color_continuous_scale='Blues',
                aspect='auto'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Bobot Kriteria")
            bobot_df = pd.DataFrame({
                'Kriteria': ahp.kriteria,
                'Bobot': bobot,
                'Persentase': [f"{b*100:.2f}%" for b in bobot]
            })
            st.dataframe(bobot_df, use_container_width=True, hide_index=True)
            
            # Visualisasi bobot
            fig = px.bar(
                bobot_df,
                x='Kriteria',
                y='Bobot',
                title='Bobot Kriteria',
                color='Kriteria',
                text_auto='.2f'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Konsistensi
        st.markdown("#### Uji Konsistensi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("λ max", f"{ahp.lambda_max:.4f}")
        
        with col2:
            st.metric("CI", f"{ahp.ci:.4f}")
        
        with col3:
            if konsisten:
                st.success(f"✅ Konsisten (CR = {ahp.cr:.4f})")
            else:
                st.error(f"❌ Tidak Konsisten (CR = {ahp.cr:.4f})")
        
        # Weighted Product
        st.subheader("📊 Perhitungan Weighted Product")
        
        if st.button("🧮 Hitung WP", use_container_width=True):
            with st.spinner("Menghitung..."):
                hasil_wp = ahp.calculate_wp(alternatif)
                
                # Tampilkan hasil
                st.markdown("#### Hasil Perhitungan WP")
                st.dataframe(hasil_wp, use_container_width=True)
                
                # Simpan ke session
                st.session_state['hasil_wp'] = hasil_wp
                st.success("✅ Perhitungan selesai! Silahkan ke menu 'Hasil & Ranking'")
                st.balloons()

# ==========================================
# HASIL & RANKING
# ==========================================

elif menu == "📈 Hasil & Ranking":
    
    st.header("📈 Hasil dan Ranking")
    
    if 'hasil_wp' not in st.session_state:
        st.warning("⚠️ Silahkan lakukan perhitungan terlebih dahulu di menu 'Perhitungan AHP-WP'")
        
        # Cek apakah data ada tapi belum dihitung
        if 'df' in st.session_state:
            st.info("💡 Data sudah diupload. Silahkan ke menu 'Perhitungan AHP-WP' untuk melakukan perhitungan.")
            
            # Tombol cepat ke perhitungan
            if st.button("🚀 Ke Menu Perhitungan", use_container_width=True):
                st.session_state['navigate_to'] = 'perhitungan'
                st.rerun()
        else:
            st.info("📂 Silahkan upload data terlebih dahulu di menu Dashboard.")
    else:
        hasil_wp = st.session_state['hasil_wp']
        
        # Ranking
        ranking = hasil_wp.sort_values('Nilai WP', ascending=False).copy()
        ranking['Ranking'] = range(1, len(ranking) + 1)
        ranking = ranking.reset_index()
        
        # Tampilkan ranking
        st.subheader("🏆 Ranking Kos")
        
        # Top 3
        st.markdown("### 🥇 Top 3 Kos Terbaik")
        
        top3 = ranking.head(3)
        cols = st.columns(3)
        
        emojis = ['🥇', '🥈', '🥉']
        colors = ['#FFD700', '#C0C0C0', '#CD7F32']
        
        for i, (idx, row) in enumerate(top3.iterrows()):
            with cols[i]:
                st.markdown(f"""
                    <div class="top-card" style="background: {colors[i]};">
                        <h1>{emojis[i]}</h1>
                        <h2>{row['Nama Kos']}</h2>
                        <h3>Nilai WP: {row['Nilai WP']:.4f}</h3>
                    </div>
                """, unsafe_allow_html=True)
        
        # Detail ranking
        st.subheader("📋 Detail Ranking")
        
        # Tambahkan kolom untuk tampilan yang lebih baik
        ranking_display = ranking.copy()
        ranking_display['Nilai WP'] = ranking_display['Nilai WP'].round(4)
        ranking_display['Vektor S'] = ranking_display['Vektor S'].round(4)
        
        st.dataframe(
            ranking_display[['Ranking', 'Nama Kos', 'Biaya', 'Jarak', 'Fasilitas', 'Keamanan', 'Akses', 'Vektor S', 'Nilai WP']],
            use_container_width=True,
            hide_index=True
        )
        
        # Visualisasi
        st.subheader("📊 Visualisasi Ranking")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig = px.bar(
                ranking,
                x='Nama Kos',
                y='Nilai WP',
                title='Nilai WP per Kos',
                color='Nilai WP',
                color_continuous_scale='Viridis',
                text_auto='.4f'
            )
            fig.update_layout(
                xaxis_title='Nama Kos',
                yaxis_title='Nilai WP',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Radar chart
            fig = px.line_polar(
                ranking.head(5),
                r='Nilai WP',
                theta='Nama Kos',
                line_close=True,
                title='Perbandingan Top 5 Kos',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Download hasil
        st.subheader("📥 Download Hasil")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Ranking (Excel)", use_container_width=True):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    ranking.to_excel(writer, index=False, sheet_name='Ranking')
                    hasil_wp.to_excel(writer, sheet_name='WP_Results')
                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name="hasil_ranking_kosan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            # Download CSV
            csv = ranking.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="hasil_ranking_kosan.csv",
                mime="text/csv"
            )

# ==========================================
# TENTANG
# ==========================================

elif menu == "ℹ️ Tentang":
    
    st.header("ℹ️ Tentang Aplikasi")
    
    st.markdown("""
        <div class="info-box">
            <h3>🎯 Tujuan</h3>
            <p>Aplikasi ini dibuat untuk membantu mahasiswa Universitas Pamulang dalam menentukan kos terbaik dengan mempertimbangkan berbagai kriteria penting.</p>
        </div>
        
        <div class="info-box">
            <h3>📊 Metode</h3>
            <p>Aplikasi menggunakan kombinasi dua metode:</p>
            <ul>
                <li><b>Analytical Hierarchy Process (AHP)</b> - Untuk menentukan bobot kepentingan setiap kriteria</li>
                <li><b>Weighted Product (WP)</b> - Untuk melakukan perankingan alternatif</li>
            </ul>
        </div>
        
        <div class="info-box">
            <h3>📋 Kriteria</h3>
            <p>Ada 5 kriteria yang digunakan:</p>
            <ol>
                <li><b>Biaya</b> - Harga sewa per bulan (Cost)</li>
                <li><b>Jarak</b> - Jarak ke kampus (Benefit)</li>
                <li><b>Fasilitas</b> - Kelengkapan fasilitas (Benefit)</li>
                <li><b>Keamanan</b> - Tingkat keamanan (Benefit)</li>
                <li><b>Akses</b> - Akses ke fasilitas umum (Benefit)</li>
            </ol>
        </div>
        
        <div class="info-box">
            <h3>👨‍💻 Pengembang</h3>
            <p>Dikembangkan oleh Tim SPK - Universitas Pamulang</p>
            <p>Versi: 1.0.0</p>
            <p>📅 2026</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# CEK NAVIGASI DARI SESSION STATE
# ==========================================
if 'navigate_to' in st.session_state:
    if st.session_state['navigate_to'] == 'perhitungan':
        st.session_state['navigate_to'] = None
        st.info("👈 Silahkan klik menu '⚙️ Perhitungan AHP-WP' di sidebar kiri.")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>© 2026 SPK Kosan UNPAM | Dibuat dengan ❤️ menggunakan Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)