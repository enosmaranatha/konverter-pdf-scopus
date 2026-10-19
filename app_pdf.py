import streamlit as st
import PyPDF2
import re

st.set_page_config(page_title="Konverter Standar ke BibTeX Sempurna", layout="wide")
st.title("📑 Konverter PDF Standar ke BibTeX (Format Baku Bibliometrix)")
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
                        # Format BibTeX baku dengan menyertakan field lengkap agar tidak missing
                        bibtex_item = f"""@article{{standard_{judul}_{i+1},
  AUTHOR = {{ISO/IEC}},
  TITLE = {{{judul} - Hal {i+1}}},
  JOURNAL = {{ISO Standard}},
  YEAR = {{2024}},
  ABSTRACT = {{{clean}}},
  KEYWORDS = {{Electric Vehicle; Standard}},
  C1 = {{ISO Technical Committee}}
}}\n\n"""
                        bibtex_output += bibtex_item
        except:
            pass
            
    if bibtex_output:
        st.success("✅ Berhasil dikonversi ke format BibTeX Sempurna!")
        st.download_button(
            label="📥 Download File .bib Terbaru",
            data=bibtex_output,
            file_name="Standar_EV.bib",
            mime="text/plain",
            type="primary"
        )
