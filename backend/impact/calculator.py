def calculate_impact(
    total_reused_litres: float,
    freshwater_cost_per_1000_litres: float
) -> dict:

    if total_reused_litres < 0:
        raise ValueError("Reused water cannot be negative.")

    if freshwater_cost_per_1000_litres < 0:
        raise ValueError("Water cost cannot be negative.")

    freshwater_displaced_litres = total_reused_litres

    estimated_savings = (
        freshwater_displaced_litres / 1000
    ) * freshwater_cost_per_1000_litres

    return {
        "reused_litres_per_day": total_reused_litres,
        "estimated_freshwater_displaced_litres_per_day":
            freshwater_displaced_litres,
        "estimated_gross_savings_per_day": round(
            estimated_savings, 2
        )
    }