import pandas as pd
from pandas import DataFrame


def get_data():
    return pd.read_csv("./INPUT/orders_export.csv")


def transform_data(data: DataFrame, last_order: int = 1) -> DataFrame:
    # Elimino duplicados y los totales a cero.
    data = data.drop_duplicates(subset=["Name"])
    data = data.drop(data[data["Total"] == 0].index)

    # Elimniar espacios en blanco
    data["Shipping Name"] = data["Shipping Name"].replace(r"\s+", " ", regex=True)
    data["Shipping Name"] = data["Shipping Name"].str.strip()

    # Si no existe Shipping Name Coger el Billing Name
    data["Shipping Name"] = data["Shipping Name"].fillna(data["Billing Name"])

    # Columnas que me interesan
    new_data = data[
        [
            "Name",
            "Paid at",
            "Currency",
            "Shipping",
            "Taxes",
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
            "Shipping": "Envío",
            "Taxes": "IVA",
            "Total": "Total",
            "Shipping Name": "Nombre Cliente",
            "Billing Country": "País de venta",
        },
        inplace=True,
    )

    # Envio SIN IVA = Envio / 1.21
    new_data.loc[:, "Envío sin IVA"] = round(new_data["Envío"] / 1.21, 2)

    # Envio sin IVA = (Total - (Envio SIN IVA * 0.21) - Envio SIN IVA) / (1 + 0.21)
    new_data.loc[:, "Subtotal sin IVA"] = round(
        (
            new_data["Total"]
            - (new_data["Envío sin IVA"] * 0.21)
            - new_data["Envío sin IVA"]
        )
        / (1 + 0.21),
        2,
    )

    # Reordenar columnas
    new_data = new_data[
        [
            "Factura",
            "Fecha",
            "Moneda",
            "Subtotal sin IVA",
            "Envío",
            "Envío sin IVA",
            "IVA",
            "Total",
            "Nombre Cliente",
            "País de venta",
        ]
    ]

    # Se cambia Facutra por el último pedido
    new_data["Factura"] = range(last_order + len(new_data) - 1, last_order - 1, -1)

    return new_data


if __name__ == "__main__":
    data = get_data()
    new_data = transform_data(data)
    # Elimino duplicados y me quedo con el último

    print(new_data.head())
    print(len(new_data.index))

    gt_data = pd.read_excel("./OUTPUT/Listado Facturas Septiembre 2024.xlsx")
    print(gt_data.head())
    print(len(gt_data.index))

    compare = new_data[
        ~(new_data["Nombre Cliente"].isin(gt_data["Nombre Cliente"]))
    ].reset_index(drop=True)

    print(compare)
    compare.to_csv("./OUTPUT/not_in_gt.csv", index=False)
    gt_data.to_csv("./OUTPUT/gt_data.csv", index=False)
    new_data.to_csv("./OUTPUT/new_data.csv", index=False)
