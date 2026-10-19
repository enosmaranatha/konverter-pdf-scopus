import streamlit as st
import pandas as pd
import PyPDF2
import re
import io

st.set_page_config(page_title="Bulk PDF ke Scopus", layout="wide")
st.title("📑 Konverter Banyak PDF Standar ke CSV Scopus")
st.write("Aplikasi ini membaca banyak file PDF ISO/IEC/UNECE sekaligus, membersihkan *watermark* BSN, dan menggabungkannya menjadi 1 file CSV untuk **Biblioshiny (R-Studio)**.")

# 1. Upload Multiple Files (Bisa blok banyak file sekaligus)
uploaded_files = st.file_uploader("Upload Dokumen Standar (PDF)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.info(f"{len(uploaded_files)} file PDF berhasil dimuat. Siap diproses!")
    
    # Pengaturan Metadata Umum
    st.markdown("### ⚙️ Isi Metadata Standar (Umum)")
    st.write("Isian di bawah ini akan diterapkan ke semua file yang diunggah. **Judul (TI) akan otomatis diambil dari nama masing-masing file.**")
    
    col1, col2, col3 = st.columns(3)
    py_input = col1.text_input("Tahun Terbit (PY)", value="2024")
    so_input = col2.text_input("Penerbit (SO)", value="ISO/IEC")
    au_input = col3.text_input("Komite/Penulis (AU)", value="Technical Committee")
    
    if st.button("🚀 Ekstrak & Gabungkan Semua ke CSV", use_container_width=True):
        data_scopus = []
        
        # Tampilan indikator progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Looping setiap file PDF yang diunggah
        for index, file in enumerate(uploaded_files):
            # Ambil nama file untuk dijadikan Judul, buang akhiran .pdf
            judul_file = file.name.replace(".pdf", "").replace(".PDF", "")
            
            status_text.text(f"Sedang memproses file {index + 1} dari {len(uploaded_files)}: {judul_file}...")
            
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                jumlah_halaman = len(pdf_reader.pages)
                
                # Looping per halaman dalam 1 file
                for i in range(jumlah_halaman):
                    page = pdf_reader.pages[i]
                    text = page.extract_text()
                    
                    if text:
                        # PROSES PEMBERSIHAN (CLEANING) WATERMARK BSN & TEKS SAMPAH
                        clean_text = text.replace('\n', ' ').strip()
                        
                        clean_text = re.sub(r'Penanggung jawab penggunaan: Direktur Pengembangan Standar Mekanika, Energi, Infrastruktur dan Teknologi Informasi BSN', '', clean_text, flags=re.IGNORECASE)
                        clean_text = re.sub(r"'Copy standar ini dibuat oleh BSN untuk Kegiatan Perumusan SNI dan tidak untuk di komersialkan'", '', clean_text, flags=re.IGNORECASE)
                        clean_text = re.sub(r'ISO\s\d+(-\d+)?:\d{4}\([a-z]{2}\)', '', clean_text, flags=re.IGNORECASE)
                        
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                        
                        # Jika teks valid (bukan halaman kosong)
                        if len(clean_text) > 50:
                            data_scopus.append({
                                'TI': f"{judul_file} - Halaman {i+1}", 
                                'AB': clean_text,                   
                                'PY': py_input,
                                'SO': so_input,
                                'AU': au_input,
                                'DT': 'Article'                     
                            })
            except Exception as e:
                st.error(f"Gagal memproses file {file.name}: {e}")
            
            # Update bar progress
            progress_bar.progress((index + 1) / len(uploaded_files))
            
        status_text.text("Selesai memproses semua file!")
        
        # Jika ada data yang berhasil diekstrak
        if len(data_scopus) > 0:
            df_scopus = pd.DataFrame(data_scopus)
            
            st.success(f"✅ Selesai! Berhasil menggabungkan {len(df_scopus)} halaman teks dari {len(uploaded_files)} dokumen menjadi 1 file CSV format Scopus.")
            
            st.write("🎯 **Preview Hasil Gabungan (Perhatikan kolom TI otomatis berubah sesuai nama file):**")
            st.dataframe(df_scopus.head(10))
            
            # Tombol Download 1 File CSV
            csv = df_scopus.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Download 1 CSV Gabungan untuk Biblioshiny",
                data=csv,
                file_name="Gabungan_Standar_EV.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.warning("Tidak ada teks yang dapat diekstrak. Pastikan PDF yang diunggah berisi teks, bukan hasil *scan* gambar.")
