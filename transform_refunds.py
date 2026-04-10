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
    totals_row = {
        "id - Devolucion": None,
        "order_number": None,
        "created": "DEVOLUCIONES",
        "aux": None,
        "amount": None,
        "TOTAL": result["TOTAL"].sum(),
        "BASE IMPONIBLE": result["BASE IMPONIBLE"].sum(),
        "IVA": result["IVA"].sum(),
        "CUENTA CLIENTE": None,
        "currency": result["currency"].iloc[0],
    }

    result = pd.concat(
        [result, DataFrame([totals_row])], ignore_index=True
    )
    result["aux"] = pd.to_numeric(result["aux"], errors="coerce")
    result["CUENTA CLIENTE"] = pd.to_numeric(result["CUENTA CLIENTE"], errors="coerce")
    return result
