from io import BytesIO

import pandas as pd
import streamlit as st

from transform_csv import transform_data


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Facturas")
    writer._save()
    processed_data = output.getvalue()
    return processed_data


st.set_page_config(
    page_title="Shopify Orders to Excel",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("Shopify Orders to Excel")

spectra = st.file_uploader("upload file", type={"csv", "txt"})
if spectra is not None:
    number = st.number_input(
        "Último pedido", value=None, placeholder="Type a number..."
    )
    if not number:
        number = 1

    spectra_df = pd.read_csv(spectra)
    final_data = transform_data(spectra_df, last_order=number)

    st.dataframe(final_data)

    doc = convert_df(final_data)

    st.download_button(
        label="Download as Excel",
        data=doc,
        file_name="Listado Facturas.xlsx",
        mime="application/vnd.ms-excel",
    )
