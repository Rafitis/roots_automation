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
    i = 1
    for index, _ in df.iterrows():
        # Rojo: nombre vacío o país no-ES con IVA 0% (exportación)
        if df.loc[index, "Nombre Cliente"] == "" or (
            df.loc[index, "IVA (%)"] == 0 and df.loc[index, "País de venta"] != "ES"
        ):
            ws.set_row(i, 18, format_cell_no_data)
        # Verde: país diferente de ES
        elif df.loc[index, "País de venta"] != "ES":
            ws.set_row(i, 18, format_cell_no_spain)

        i += 1

    # Anchos de columna: A=Nombre Cliente, B=Factura, C=NIF, D=Fecha, E-L=resto
    ws.set_default_row(18)
    ws.set_column(0, 0, 30)  # Nombre Cliente
    ws.set_column(1, 1, 15)  # Factura
    ws.set_column(2, 2, 15)  # NIF SOCIEDAD
    ws.set_column(3, 3, 12)  # Fecha
    ws.set_column(4, 9, 15)  # IVA(%) a CUENTA INGRESO
    ws.set_column(10, 11, 12)  # País de venta, Moneda
    writer.close()
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
        if number is None:
            number = 1

        spectra_df = pd.read_csv(spectra)
        final_data = transform_data(spectra_df, last_order=int(number), nif_sociedad=st.secrets["NIF_SOCIEDAD"])

        st.dataframe(final_data)

        doc = convert_df(final_data)

        st.download_button(
            label="Download as Excel",
            data=doc,
            file_name="Listado Facturas.xlsx",
            mime="application/vnd.ms-excel",
        )
elif password:
    st.error("Contraseña incorrecta")
