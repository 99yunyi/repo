"""BPCS batch aggregation simulator."""

from typing import Dict
from bpcs_simulation import config
import importlib
import pandas as pd



def simulate_batches(num_batches: int = None, batch_size: int = None, payload_size: int = None,
                     signature_info: Dict = None) -> Dict:
    num_batches = num_batches or config.NUM_BATCHES
    batch_size = batch_size or config.BATCH_SIZE
    payload_size = payload_size or config.PAYLOAD_SIZE_BYTES

    total_items = num_batches * batch_size
    raw_data_bytes = total_items * payload_size

    metadata_bytes = num_batches * config.DEFAULT_METADATA_PER_BATCH

    sig_size = None
    per_sig_time = None
    if signature_info:
        sig_size = signature_info.get("signature_size")
        per_sig_time = signature_info.get("avg_sig_time")

    if not sig_size:
        sig_size = config.ESTIMATED_PQC_SIG_SIZE if config.USE_PQC else config.ESTIMATED_ECDSA_SIG_SIZE

    total_sig_bytes = total_items * sig_size
    total_storage = raw_data_bytes + metadata_bytes + total_sig_bytes

    est_signing_time = (per_sig_time * total_items) if per_sig_time else None

    return {
        "num_batches": num_batches,
        "batch_size": batch_size,
        "total_items": total_items,
        "raw_data_bytes": raw_data_bytes,
        "metadata_bytes": metadata_bytes,
        "signature_size_bytes": sig_size,
        "total_sig_bytes": total_sig_bytes,
        "total_storage_bytes": total_storage,
        "estimated_signing_time_s": est_signing_time,
    }


def simulate_daily_aggregation(total_ioc: int = 5000, batch_size: int = 100, timings: Dict = None, daily_uploads: int = 10) -> pd.DataFrame:
    """Simulate daily signing/verification workload for various schemes.

    Returns a DataFrame with columns:
    [Scheme, Daily_Sign_Count, Daily_Sign_Time_ms, Daily_Verify_Time_ms,
     Aggregate_Daily_Verify_ms, Batch_Reduction_Pct]

    timings: expected dict with keys matching 'ecdsa', 'slh-dsa-sha2-128s', 'ml-dsa-44'
             each mapping to dict with 'sign_ms' and 'verify_ms'. If not provided,
             try to import and call `bpcs_simulation.crypto_bench.bench_all()`.
    """
    # obtain timings if not given
    if timings is None:
        try:
            bench = importlib.import_module("bpcs_simulation.crypto_bench")
            timings = bench.bench_all()
        except Exception:
            # fallback estimates
            timings = {
                "ecdsa": {"sign_ms": 0.7, "verify_ms": 0.6},
                "slh-dsa-sha2-128s": {"sign_ms": 5.0, "verify_ms": 2.0},
                "ml-dsa-44": {"sign_ms": 1.0, "verify_ms": 0.5},
            }

    # map names
    ecdsa = timings.get("ecdsa") or timings.get("ECDSA")
    slh = timings.get("slh-dsa-sha2-128s") or timings.get("SLH-DSA-SHA2-128S")
    ml = timings.get("ml-dsa-44") or timings.get("ML-DSA-44")

    results = []

    # No-batch ECDSA
    sign_count_nobatch = total_ioc
    sign_time_nobatch = sign_count_nobatch * (ecdsa.get("sign_ms") if ecdsa else 0)
    verify_time_nobatch = sign_count_nobatch * (ecdsa.get("verify_ms") if ecdsa else 0)
    aggregate_verify_nobatch = daily_uploads * (ecdsa.get("verify_ms") if ecdsa else 0)
    reduction_pct = (total_ioc - (total_ioc // batch_size)) / total_ioc * 100.0
    results.append({
        "Scheme": "NoBatch-ECDSA",
        "Daily_Sign_Count": sign_count_nobatch,
        "Daily_Sign_Time_ms": round(sign_time_nobatch, 3),
        "Daily_Verify_Time_ms": round(verify_time_nobatch, 3),
        "Aggregate_Daily_Verify_ms": round(aggregate_verify_nobatch, 3),
        "Batch_Reduction_Pct": round(reduction_pct, 3),
    })

    # Batched schemes (one signature per batch)
    batches_per_day = total_ioc // batch_size

    def add_batched(name, timing):
        sign_count = batches_per_day
        sign_time = sign_count * timing.get("sign_ms", 0)
        verify_time = sign_count * timing.get("verify_ms", 0)
        aggregate_verify = daily_uploads * timing.get("verify_ms", 0)
        reduction = (total_ioc - sign_count) / total_ioc * 100.0
        results.append({
            "Scheme": name,
            "Daily_Sign_Count": sign_count,
            "Daily_Sign_Time_ms": round(sign_time, 3),
            "Daily_Verify_Time_ms": round(verify_time, 3),
            "Aggregate_Daily_Verify_ms": round(aggregate_verify, 3),
            "Batch_Reduction_Pct": round(reduction, 3),
        })

    add_batched("Batch-ECDSA", ecdsa if ecdsa else {"sign_ms": 0, "verify_ms": 0})
    add_batched("Batch-SLH-DSA", slh if slh else {"sign_ms": 0, "verify_ms": 0})
    add_batched("Batch-ML-DSA", ml if ml else {"sign_ms": 0, "verify_ms": 0})

    df = pd.DataFrame(results, columns=["Scheme", "Daily_Sign_Count", "Daily_Sign_Time_ms", "Daily_Verify_Time_ms", "Aggregate_Daily_Verify_ms", "Batch_Reduction_Pct"])
    return df


if __name__ == "__main__":
    import pprint
    pprint.pp(simulate_batches())
