"""Run all benchmarks and simulations, output results to CSV and PNG."""
import os

import pandas as pd
import matplotlib.pyplot as plt

from bpcs_simulation import config
from bpcs_simulation.crypto_bench import bench_all
from bpcs_simulation.storage_calc import compute_scheme_storage


def _format_bytes(value: float, unit: str) -> str:
    if unit == "KB":
        return f"{value:.2f} KB"
    if unit == "MB":
        return f"{value:.1f} MB" if value >= 1 else f"{value:.2f} MB"
    return str(value)


def run_all():
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    print("Running crypto benchmarks...")
    bench_results = bench_all()
    print("Benchmarks:")
    for name, result in bench_results.items():
        print(f"  {name}: {result}")

    storage_df = compute_scheme_storage()

    security_info = {
        "ECDSA (no batch)": {"pq": "✗", "assumption": "ECDLP"},
        "ECDSA+Batch": {"pq": "✗", "assumption": "ECDLP"},
        "SLH-DSA+Batch": {"pq": "✓ (FIPS 205)", "assumption": "Hash col.res."},
        "ML-DSA-44+Batch": {"pq": "✓ (FIPS 204)", "assumption": "MLWE (lattice)"},
    }

    table_rows = []
    for metric in [
        "Public Key Size",
        "Private Key Size",
        "Signature Size",
        "Daily Uploads (per node)",
        "On-chain Per Upload",
        "Daily On-chain (per node)",
        "Monthly On-chain (100 nodes)",
        "Daily Off-chain (per Enterprise)",
        "Monthly Off-chain (per Enterprise)",
        "KeyGen Time",
        "Signing Time (per operation)",
        "Verification Time (per signature)",
        "Aggregate Daily Verification Time",
        "Post-Quantum Security",
        "Security Assumption",
    ]:
        row = {"Metric": metric}
        for _, scheme in storage_df.iterrows():
            name = scheme["Scheme"]
            if metric == "Public Key Size":
                row[name] = f"{scheme['Public_Key_Size']} bytes"
            elif metric == "Private Key Size":
                row[name] = f"{scheme['Private_Key_Size']} bytes"
            elif metric == "Signature Size":
                row[name] = f"{scheme['Signature_Size']} bytes"
            elif metric == "Daily Uploads (per node)":
                row[name] = f"{int(scheme['Daily_Uploads'])}"
            elif metric == "On-chain Per Upload":
                row[name] = f"{int(scheme['Onchain_Per_Upload'])} bytes"
            elif metric == "Daily On-chain (per node)":
                row[name] = _format_bytes(scheme["Daily_Onchain_KB"], "KB")
            elif metric == "Monthly On-chain (100 nodes)":
                row[name] = _format_bytes(scheme["Monthly_Onchain_MB"], "MB")
            elif metric == "Daily Off-chain (per Enterprise)":
                row[name] = _format_bytes(scheme["Daily_Offchain_KB"], "KB")
            elif metric == "Monthly Off-chain (per Enterprise)":
                row[name] = _format_bytes(scheme["Monthly_Offchain_MB"], "MB")
            elif metric == "KeyGen Time":
                alg = scheme["Algorithm"]
                bench = bench_results.get(alg, bench_results.get("ecdsa", {}))
                row[name] = f"{bench.get('keygen_ms', 0):.3f} ms"
            elif metric == "Signing Time (per operation)":
                alg = scheme["Algorithm"]
                bench = bench_results.get(alg, bench_results.get("ecdsa", {}))
                row[name] = f"{bench.get('sign_ms', 0):.3f} ms"
            elif metric == "Verification Time (per signature)":
                alg = scheme["Algorithm"]
                bench = bench_results.get(alg, bench_results.get("ecdsa", {}))
                row[name] = f"{bench.get('verify_ms', 0):.3f} ms"
            elif metric == "Aggregate Daily Verification Time":
                alg = scheme["Algorithm"]
                bench = bench_results.get(alg, bench_results.get("ecdsa", {}))
                row[name] = f"{scheme['Daily_Uploads'] * bench.get('verify_ms', 0):.3f} ms"
            elif metric == "Post-Quantum Security":
                row[name] = security_info[name]["pq"]
            elif metric == "Security Assumption":
                row[name] = security_info[name]["assumption"]
        table_rows.append(row)

    table_df = pd.DataFrame(table_rows).set_index("Metric")
    csv_path = os.path.join(config.RESULTS_DIR, "table_5_3.csv")
    table_df.to_csv(csv_path)
    print(f"Wrote Table 5.3 CSV to {csv_path}")

    txt_path = os.path.join(config.RESULTS_DIR, "table_5_3.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        try:
            f.write(table_df.to_markdown())
            print(f"Wrote Table 5.3 Markdown to {txt_path}")
        except Exception:
            f.write(table_df.to_string())
            print(f"Wrote Table 5.3 text to {txt_path} (markdown unavailable)")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    table = ax.table(cellText=table_df.reset_index().values,
                     colLabels=table_df.reset_index().columns,
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    png_path = os.path.join(config.RESULTS_DIR, "table_5_3.png")
    fig.savefig(png_path, bbox_inches='tight')
    plt.close(fig)
    print(f"Wrote Table 5.3 image to {png_path}")


if __name__ == "__main__":
    run_all()
