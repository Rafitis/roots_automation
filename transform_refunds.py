import pandas as pd
from pandas import DataFrame


def transform_refunds(data: DataFrame, last_devolucion: int = 1) -> DataFrame:
    # Filtrar solo devoluciones con importe positivo
    data = data[data["amount"] > 0].copy()
    data = data.sort_values("created").reset_index(drop=True)

    # Fecha: solo fecha, sin hora
    data["created"] = pd.to_datetime(data["created"]).dt.strftime("%Y-%m-%d")

    current_year = int(data["created"].iloc[0].split("-")[0])

    num_rows = len(data)
    ids = [
        f"D{current_year}-{i:04d}"
        for i in range(last_devolucion, last_devolucion + num_rows)
    ]

    result = DataFrame(
        {
            "id - Devolucion": ids,
            "order_number": data["order_number"].values,
            "created": data["created"].values,
            "aux": 10000,
            "amount": data["amount"].values,
            "TOTAL": data["amount"].values,
            "BASE IMPONIBLE": (data["amount"] / 1.21).values,
            "IVA": (data["amount"] - data["amount"] / 1.21).values,
            "CUENTA CLIENTE": 70000008,
            "currency": data["currency"].values,
        }
    )

    # Fila de totales
    totals_row = {col: "" for col in result.columns}
    totals_row["created"] = "DEVOLUCIONES"
    totals_row["aux"] = ""
    totals_row["amount"] = ""
    totals_row["TOTAL"] = result["TOTAL"].sum()
    totals_row["BASE IMPONIBLE"] = result["BASE IMPONIBLE"].sum()
    totals_row["IVA"] = result["IVA"].sum()
    totals_row["CUENTA CLIENTE"] = ""
    totals_row["currency"] = result["currency"].iloc[0]

    result = result.astype({"aux": object, "CUENTA CLIENTE": object})
    return pd.concat(
        [result, DataFrame([totals_row])], ignore_index=True
    )
