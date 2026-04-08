import pandas as pd
from pandas import DataFrame


IVA_POR_PAIS = {
    "ES": 21,
    "FR": 20,
    "DE": 19,
    "IT": 22,
    "PT": 23,
    "BE": 21,
    "NL": 21,
    "AT": 20,
    "IE": 23,
    "LU": 17,
}


def get_data():
    return pd.read_csv("./INPUT/orders_export.csv")


def _get_year_from_date(date_str: str) -> int:
    return int(date_str.split("-")[0])


def transform_data(
    data: DataFrame, last_order: int = 1, nif_sociedad: str = ""
) -> DataFrame:
    # Elimino duplicados y los totales a cero.
    data = data.drop_duplicates(subset=["Name"]).copy()
    data = data.drop(data[data["Total"] == 0].index)

    # Elimniar espacios en blanco
    data["Shipping Name"] = data["Shipping Name"].replace(r"\s+", " ", regex=True)
    data["Shipping Name"] = data["Shipping Name"].str.strip()

    # Si no existe Shipping Name Coger el Billing Name
    data["Shipping Name"] = data["Shipping Name"].fillna(data["Billing Name"])

    # Si no existe pais de procedencia poner ES.
    data["Billing Country"] = data["Billing Country"].fillna("ES")

    # Columnas que me interesan
    new_data = data[
        [
            "Name",
            "Paid at",
            "Currency",
            "Total",
            "Shipping Name",
            "Billing Country",
        ]
    ]

    # Cambio de nombres
    new_data.rename(
        columns={
            "Name": "Factura",
            "Paid at": "Fecha",
            "Currency": "Moneda",
            "Total": "Total",
            "Shipping Name": "Nombre Cliente",
            "Billing Country": "País de venta",
        },
        inplace=True,
    )

    # NIF SOCIEDAD
    new_data.loc[:, "NIF SOCIEDAD"] = nif_sociedad

    # Fecha: solo fecha, sin hora ni timezone
    new_data.loc[:, "Fecha"] = pd.to_datetime(new_data["Fecha"]).dt.strftime("%Y-%m-%d")

    # IVA (%) según país de venta. Si no está en la lista → 0% (exportación)
    new_data.loc[:, "IVA (%)"] = new_data["País de venta"].map(IVA_POR_PAIS).fillna(0).astype(int)

    # BASE IMPONIBLE = Total / (1 + IVA/100)
    new_data.loc[:, "BASE IMPONIBLE"] = round(
        new_data["Total"] / (1 + new_data["IVA (%)"] / 100), 2
    )

    # IVA (€) = Total - BASE IMPONIBLE
    new_data.loc[:, "IVA (€)"] = round(new_data["Total"] - new_data["BASE IMPONIBLE"], 2)

    # CUENTA CLIENTE siempre fija
    new_data.loc[:, "CUENTA CLIENTE"] = 43000000

    # CUENTA INGRESO según país e IVA
    new_data.loc[:, "CUENTA INGRESO"] = 70000000  # Por defecto: España
    new_data.loc[
        (new_data["País de venta"] != "ES") & (new_data["IVA (%)"] != 0),
        "CUENTA INGRESO",
    ] = 700000001
    new_data.loc[
        (new_data["País de venta"] != "ES") & (new_data["IVA (%)"] == 0),
        "CUENTA INGRESO",
    ] = 700000002

    # Reordenar columnas
    new_data = new_data[
        [
            "Nombre Cliente",
            "Factura",
            "NIF SOCIEDAD",
            "Fecha",
            "IVA (%)",
            "BASE IMPONIBLE",
            "IVA (€)",
            "Total",
            "CUENTA CLIENTE",
            "CUENTA INGRESO",
            "País de venta",
            "Moneda",
        ]
    ]

    # Se cambia Facutra por el último pedido
    current_year = _get_year_from_date(new_data["Fecha"].iloc[0])
    new_data["Factura"] = [
        f"{current_year}-{i}"
        for i in range(last_order + len(new_data) - 1, last_order - 1, -1)
    ]
    new_data["Nombre Cliente"] = new_data["Nombre Cliente"].fillna("")
    return new_data


if __name__ == "__main__":
    data = get_data()
    new_data = transform_data(data)
    # Elimino duplicados y me quedo con el último

    print(new_data.head())
    print(len(new_data.index))

    gt_data = pd.read_excel("./OUTPUT/Listado de Facturas emitidas Febrero 26.xlsx")
    print(gt_data.head())
    print(len(gt_data.index))

    compare = new_data[
        ~(new_data["Nombre Cliente"].isin(gt_data["Nombre Cliente"]))
    ].reset_index(drop=True)

    print(compare)
    compare.to_csv("./OUTPUT/not_in_gt.csv", index=False)
    gt_data.to_csv("./OUTPUT/gt_data.csv", index=False)
    new_data.to_csv("./OUTPUT/new_data.csv", index=False)
