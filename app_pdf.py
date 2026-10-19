import streamlit as st
import pandas as pd
import PyPDF2
import re
import io

st.set_page_config(page_title="PDF Standar ke Scopus", layout="wide")
st.title("📑 Konverter PDF Dokumen Standar ke CSV Scopus")
st.write("Aplikasi ini membaca file PDF ISO/IEC/UNECE, membersihkan *watermark* BSN, dan mengubah teksnya menjadi format Scopus untuk **Biblioshiny (R-Studio)**.")

# 1. Upload File PDF
uploaded_file = st.file_uploader("Upload Dokumen Standar (PDF)", type=["pdf"])

if uploaded_file is not None:
    st.info("Membaca dan mengekstrak teks dari PDF...")
    
    try:
        # Membaca PDF
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        jumlah_halaman = len(pdf_reader.pages)
        
        # Pengaturan Metadata
        st.markdown("### ⚙️ Isi Metadata Standar")
        col1, col2, col3, col4 = st.columns(4)
        ti_input = col1.text_input("Judul Standar (TI)", value="ISO 5474-2")
        py_input = col2.text_input("Tahun Terbit (PY)", value="2024")
        so_input = col3.text_input("Penerbit (SO)", value="ISO")
        au_input = col4.text_input("Komite/Penulis (AU)", value="ISO/TC 22")
        
        if st.button("🚀 Ekstrak & Konversi ke Format Scopus", use_container_width=True):
            data_scopus = []
            
            # Looping per halaman
            for i in range(jumlah_halaman):
                page = pdf_reader.pages[i]
                text = page.extract_text()
                
                if text:
                    # PROSES PEMBERSIHAN (CLEANING) WATERMARK BSN & TEKS SAMPAH
                    # Hapus spasi berlebih dan enter baru
                    clean_text = text.replace('\n', ' ').strip()
                    
                    # Hapus kalimat watermark BSN (Gunakan regex agar case-insensitive)
                    clean_text = re.sub(r'Penanggung jawab penggunaan: Direktur Pengembangan Standar Mekanika, Energi, Infrastruktur dan Teknologi Informasi BSN', '', clean_text, flags=re.IGNORECASE)
                    clean_text = re.sub(r"'Copy standar ini dibuat oleh BSN untuk Kegiatan Perumusan SNI dan tidak untuk di komersialkan'", '', clean_text, flags=re.IGNORECASE)
                    clean_text = re.sub(r'ISO 5474-2:2024\(en\)', '', clean_text, flags=re.IGNORECASE)
                    
                    # Membersihkan spasi ganda akibat penghapusan kata
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    
                    # Jika setelah dibersihkan teksnya masih panjang (bukan halaman kosong/hanya angka)
                    if len(clean_text) > 50:
                        data_scopus.append({
                            'TI': f"{ti_input} - Halaman {i+1}", # Membedakan judul tiap baris
                            'AB': clean_text,                   # Teks halaman jadi Abstrak
                            'PY': py_input,
                            'SO': so_input,
                            'AU': au_input,
                            'DT': 'Article'                     # Wajib Article untuk Biblioshiny
                        })
            
            # Membuat DataFrame
            df_scopus = pd.DataFrame(data_scopus)
            
            st.success(f"✅ Selesai! Berhasil mengekstrak {len(df_scopus)} halaman teks valid menjadi format Scopus.")
            
            st.write("🎯 **Preview Hasil Akhir (Perhatikan teks BSN sudah hilang di kolom AB):**")
            st.dataframe(df_scopus.head(5))
            
            # Tombol Download
            csv = df_scopus.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Download CSV Scopus",
                data=csv,
                file_name=f"Scopus_{ti_input}.csv",
                mime="text/csv",
                type="primary"
            )
            
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses PDF: {e}")