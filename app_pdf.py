import streamlit as st
import pandas as pd
import PyPDF2
import re

st.set_page_config(page_title="Bulk PDF ke Scopus", layout="wide")
st.title("📑 Konverter Banyak PDF Standar ke CSV Scopus")
st.write("Aplikasi ini membaca banyak file PDF sekaligus, membersihkan watermark BSN, dan menggabungkannya menjadi 1 file CSV. **Anda bisa mengatur Tahun Terbit yang berbeda untuk setiap file.**")

# 1. Upload Multiple Files
uploaded_files = st.file_uploader("Upload Dokumen Standar (PDF)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.info(f"{len(uploaded_files)} file PDF berhasil dimuat. Silakan atur metadatanya di bawah ini:")
    
    st.markdown("### ⚙️ Pengaturan Metadata per File")
    
    # Dictionary untuk menyimpan pengaturan tiap-tiap file
    metadata_dict = {}
    
    # Memunculkan kotak input (kolom) untuk SETIAP file yang diunggah
    for index, file in enumerate(uploaded_files):
        default_title = file.name.replace(".pdf", "").replace(".PDF", "")
        
        # Membuat kotak expander untuk masing-masing file
        with st.expander(f"📄 File {index+1}: {file.name}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            ti = col1.text_input("Judul (TI)", value=default_title, key=f"ti_{index}")
            py = col2.text_input("Tahun (PY)", value="2024", key=f"py_{index}")
            so = col3.text_input("Penerbit (SO)", value="ISO", key=f"so_{index}")
            au = col4.text_input("Komite (AU)", value="ISO/TC", key=f"au_{index}")
            
            # Menyimpan isian user ke dalam memori
            metadata_dict[file.name] = {"TI": ti, "PY": py, "SO": so, "AU": au}
            
    # Tombol Eksekusi
    if st.button("🚀 Ekstrak & Gabungkan Semua ke CSV", use_container_width=True):
        data_scopus = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, file in enumerate(uploaded_files):
            # Mengambil metadata spesifik (Tahun, Judul) yang tadi diketik untuk file INI
            meta = metadata_dict[file.name]
            judul_file = meta["TI"]
            tahun_file = meta["PY"]
            penerbit_file = meta["SO"]
            komite_file = meta["AU"]
            
            status_text.text(f"Sedang memproses file {index + 1} dari {len(uploaded_files)}: {judul_file}...")
            
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
                                'TI': f"{judul_file} - Halaman {i+1}", 
                                'AB': clean_text,                   
                                'PY': tahun_file,  # Menggunakan tahun spesifik file tersebut
                                'SO': penerbit_file,
                                'AU': komite_file,
                                'DT': 'Article'                     
                            })
            except Exception as e:
                st.error(f"Gagal memproses file {file.name}: {e}")
            
            progress_bar.progress((index + 1) / len(uploaded_files))
            
        status_text.text("Selesai memproses semua file!")
        
        if len(data_scopus) > 0:
            df_scopus = pd.DataFrame(data_scopus)
            st.success(f"✅ Selesai! Berhasil menggabungkan {len(df_scopus)} halaman teks menjadi 1 file CSV format Scopus.")
            
            # Preview tabel
            st.dataframe(df_scopus.head(5))
            
            # Download
            csv = df_scopus.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Download 1 CSV Gabungan untuk Biblioshiny",
                data=csv,
                file_name="Gabungan_Standar_EV.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.warning("Tidak ada teks yang dapat diekstrak. Pastikan PDF yang diunggah berisi teks.")
