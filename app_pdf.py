import streamlit as st
import pandas as pd
import PyPDF2
import re

st.set_page_config(page_title="Bulk PDF ke Scopus", layout="wide")
st.title("📑 Konverter Banyak PDF Standar ke CSV Scopus")
st.write("Aplikasi ini membaca banyak file PDF sekaligus dan **otomatis mendeteksi Tahun & Penerbit** dari halaman sampulnya untuk format Biblioshiny (R-Studio).")

# 1. Upload Multiple Files
uploaded_files = st.file_uploader("Upload Dokumen Standar (PDF)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.info(f"{len(uploaded_files)} file PDF berhasil dimuat. Sistem telah mendeteksi metadatanya secara otomatis. Silakan periksa di bawah ini:")
    
    metadata_dict = {}
    
    for index, file in enumerate(uploaded_files):
        detected_year = "2024"
        detected_pub = "ISO"
        detected_kom = "ISO/TC"
        
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            if len(pdf_reader.pages) > 0:
                text_sampul = pdf_reader.pages[0].extract_text()
                tahun_match = re.search(r'\b(20\d{2}|19\d{2})\b', text_sampul)
                if tahun_match:
                    detected_year = tahun_match.group(1)
                if "IEC" in text_sampul: 
                    detected_pub = "IEC"
                elif "UNECE" in text_sampul or "UN/ECE" in text_sampul: 
                    detected_pub = "UNECE"
                tc_match = re.search(r'(TC\s*\d+|SC\s*\d+)', text_sampul, re.IGNORECASE)
                if tc_match:
                    detected_kom = f"{detected_pub}/{tc_match.group(1).upper()}"
        except:
            pass 
        
        file.seek(0)
        default_title = file.name.replace(".pdf", "").replace(".PDF", "")
        
        with st.expander(f"📄 File {index+1}: {file.name}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            ti = col1.text_input("Judul (TI)", value=default_title, key=f"ti_{index}")
            py = col2.text_input("Tahun (PY)", value=detected_year, key=f"py_{index}")
            so = col3.text_input("Penerbit (SO)", value=detected_pub, key=f"so_{index}")
            au = col4.text_input("Komite (AU)", value=detected_kom, key=f"au_{index}")
            
            metadata_dict[file.name] = {"TI": ti, "PY": py, "SO": so, "AU": au}
            
    # Tombol Eksekusi
    if st.button("🚀 Ekstrak & Gabungkan Semua ke CSV", use_container_width=True):
        data_scopus = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, file in enumerate(uploaded_files):
            file.seek(0) 
            meta = metadata_dict[file.name]
            
            status_text.text(f"Sedang memproses file {index + 1} dari {len(uploaded_files)}: {meta['TI']}...")
            
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                jumlah_halaman = len(pdf_reader.pages)
                
                for i in range(jumlah_halaman):
                    page = pdf_reader.pages[i]
                    text = page.extract_text()
                    
                    if text:
                        clean_text = text.replace('\n', ' ').strip()
                        clean_text = re.sub(r'Penanggung jawab penggunaan: Direktur Pengembangan Standar Mekanika, Energi, Infrastruktur dan Teknologi Informasi BSN', '', clean_text, flags=re.IGNORECASE)
                        clean_text = re.sub(r"'Copy standar ini dibuat oleh BSN untuk Kegiatan Perumusan SNI dan tidak untuk di komersialkan'", '', clean_text, flags=re.IGNORECASE)
                        clean_text = re.sub(r'ISO\s\d+(-\d+)?:\d{4}\([a-z]{2}\)', '', clean_text, flags=re.IGNORECASE)
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                        
                        if len(clean_text) > 50:
                            data_scopus.append({
                                'TI': f"{meta['TI']} - Halaman {i+1}", 
                                'AB': clean_text,                   
                                'PY': meta['PY'],
                                'SO': meta['SO'],
                                'AU': meta['AU'],
                                'DT': 'Article',
                                # --- TAMBAHAN KOLOM PENGECOH UNTUK MENCEGAH ERROR BIBLIOSHINY ---
                                'TC': '0',                        # Total Citations (Sitasi)
                                'CR': 'Tidak ada referensi',      # Cited References (Daftar Pustaka)
                                'DE': 'Standard',                 # Author Keywords
                                'ID': 'Electric Vehicle',         # Keywords Plus
                                'C1': meta['SO'],                 # Affiliation
                                'RP': meta['SO']                  # Reprint Address
                            })
            except Exception as e:
                st.error(f"Gagal memproses file {file.name}: {e}")
            
            progress_bar.progress((index + 1) / len(uploaded_files))
            
        status_text.text("Selesai memproses semua file!")
        
        if len(data_scopus) > 0:
            df_scopus = pd.DataFrame(data_scopus)
            st.success(f"✅ Selesai! Berhasil menggabungkan {len(df_scopus)} halaman teks menjadi 1 file CSV format Scopus.")
            
            csv = df_scopus.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Download 1 CSV Gabungan untuk Biblioshiny",
                data=csv,
                file_name="Gabungan_Standar_EV_Final.csv",
                mime="text/csv",
                type="primary"
            )
