import streamlit as st
import pandas as pd
import PyPDF2
import re

st.set_page_config(page_title="Konverter Standar WoS", layout="wide")
st.title("📑 Konverter PDF Standar ke Format WoS (Clean CSV)")
uploaded_files = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    data_list = []
    for file in uploaded_files:
        judul = file.name.replace(".pdf", "").replace(".PDF", "")
        try:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt:
                    # Bersihkan teks dari simbol aneh pemicu error R
                    clean = txt.replace('\n', ' ').replace('"', '').strip()
                    clean = re.sub(r'\s+', ' ', clean)
                    if len(clean) > 30:
                        data_list.append({
                            'AU': 'ISO/IEC',
                            'TI': f"{judul} - Hal {i+1}",
                            'PY': '2024',
                            'SO': 'ISO',
                            'AB': clean,
                            'DT': 'Article'
                        })
        except:
            pass
            
    if data_list:
        df_final = pd.DataFrame(data_list)
        csv_data = df_final.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="📥 Download CSV Bersih untuk WoS",
            data=csv_data,
            file_name="Standar_EV_Clean.csv",
            mime="text/csv",
            type="primary"
        )
