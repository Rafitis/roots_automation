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
    workbook = writer.book
    ws = writer.sheets["Facturas"]

    format_cell_no_spain = workbook.add_format({"bg_color": "#92D050"})
    format_cell_no_data = workbook.add_format({"bg_color": "#db1e13"})
    columns_format = workbook.add_format().set_text_wrap()
    i = 1
    for index, _ in df.iterrows():
        # Si algún campo es nulo, poner la linea en rojo.
        if df.loc[index, "Nombre Cliente"] == "":
            ws.set_row(i, 18, format_cell_no_data)

        # Seleccionar las filas donde "País de venta" es diferente de "ES"
        if df.loc[index, "País de venta"] != "ES":
            ws.set_row(i, 18, format_cell_no_spain)

        i += 1

    ws.set_default_row(18)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 7, 10, cell_format=columns_format)
    ws.set_column(8, 8, 30)
    ws.set_column(9, 9, 10, cell_format=columns_format)
    writer._save()
    processed_data = output.getvalue()
    return processed_data


st.set_page_config(
    page_title="Shopify Orders to Excel",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="expanded",
)

password = st.text_input("Password", type="password")


if password == st.secrets["MAIN_PASSWORD"]:
    st.title("Shopify Orders to Excel")

    spectra = st.file_uploader("upload file", type={"csv"})
    if spectra is not None:
        number = st.number_input(
            "Último pedido", value=None, placeholder="Type a number...", format="%0.0f"
        )
        if not number:
            number = 1

        spectra_df = pd.read_csv(spectra)
        final_data = transform_data(spectra_df, last_order=int(number))

        st.dataframe(final_data)

        doc = convert_df(final_data)

        st.download_button(
            label="Download as Excel",
            data=doc,
            file_name="Listado Facturas.xlsx",
            mime="application/vnd.ms-excel",
        )
