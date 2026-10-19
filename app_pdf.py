import streamlit as st
import PyPDF2
import re

st.set_page_config(page_title="Konverter Standar ke BibTeX", layout="wide")
st.title("📑 Konverter PDF Standar ke Format BibTeX (Anti-Error Biblioshiny)")
uploaded_files = st.file_uploader("Upload PDF Standar", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    bibtex_output = ""
    
    for file in uploaded_files:
        judul = file.name.replace(".pdf", "").replace(".PDF", "")
        try:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt:
                    # Bersihkan teks agar aman untuk format BibTeX
                    clean = txt.replace('\n', ' ').replace('"', '').replace('{', '(').replace('}', ')').strip()
                    clean = re.sub(r'\s+', ' ', clean)
                    
                    if len(clean) > 30:
                        # Format standar BibTeX (Article) yang pasti dibaca Biblioshiny
                        bibtex_item = f"""@article{{standard_{judul}_page_{i+1},
  author = {{ISO/IEC}},
  title = {{{judul} - Hal {i+1}}},
  journal = {{ISO Standard}},
  year = {{2024}},
  abstract = {{{clean}}}
}}\n\n"""
                        bibtex_output += bibtex_item
        except:
            pass
            
    if bibtex_output:
        st.success("✅ Berhasil dikonversi ke format BibTeX!")
        st.download_button(
            label="📥 Download File .bib untuk Biblioshiny",
            data=bibtex_output,
            file_name="Standar_EV.bib",
            mime="text/plain",
            type="primary"
        )
