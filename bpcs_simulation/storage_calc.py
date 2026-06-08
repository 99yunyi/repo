"""Utilities for storage calculation and human-readable formatting.

This module now includes `compute_scheme_storage` which computes per-upload,
daily and monthly storage metrics for four schemes and returns a pandas
DataFrame with columns:
  [Scheme, PK_Size, SK_Size, Sig_Size, Daily_Uploads, Daily_Volume_KB, Monthly_Storage_MB]

Defaults are conservative estimates; sizes can be adjusted if accurate
key/signature sizes are available.
"""

from typing import Dict, List
import pandas as pd

from bpcs_simulation import config


def _bytes_to_kb(b: float) -> float:
    return b / 1024.0


def _bytes_to_mb(b: float) -> float:
    return b / (1024.0 * 1024.0)


def compute_scheme_storage() -> pd.DataFrame:
    """Compute on-chain and off-chain storage metrics for configured BPCS schemes.

    On-chain:
      - Batches: fixed ONCHAIN_PAYLOAD per upload
      - No-batch ECDSA: signature + report digest (32 bytes) per upload

    Off-chain:
      - Batches: per batch = BATCH_SIZE × (sig_size + AVG_REPORT_SIZE),
        daily per E = daily_uploads × per_batch, monthly per E = daily × DAYS_PER_MONTH
      - No-batch: per report = AVG_REPORT_SIZE, daily per E = DAILY_IOC × AVG_REPORT_SIZE
    """

    rows = []
    for scheme_name, scheme_cfg in config.SCHEMES.items():
        algorithm = scheme_cfg["algorithm"]
        daily_uploads = scheme_cfg["daily_uploads"]
        key_sizes = config.KEY_SIZES.get(algorithm, {})
        sig_size = key_sizes.get("sig", 0)
        pk_size = key_sizes.get("pk", 0)
        sk_size = key_sizes.get("sk", 0)

        if scheme_cfg.get("batch", False):
            onchain_per_upload = config.ONCHAIN_PAYLOAD
            onchain_daily = onchain_per_upload * daily_uploads
            onchain_monthly = onchain_daily * config.DAYS_PER_MONTH * config.NUM_NODES

            batch_payload = config.BATCH_SIZE * (sig_size + config.AVG_REPORT_SIZE)
            offchain_daily = daily_uploads * batch_payload
            offchain_monthly = offchain_daily * config.DAYS_PER_MONTH
        else:
            onchain_per_upload = sig_size + 32
            onchain_daily = onchain_per_upload * daily_uploads
            onchain_monthly = onchain_daily * config.DAYS_PER_MONTH * config.NUM_NODES

            offchain_daily = config.DAILY_IOC * config.AVG_REPORT_SIZE
            offchain_monthly = offchain_daily * config.DAYS_PER_MONTH

        rows.append({
            "Scheme": scheme_name,            "Algorithm": algorithm,            "Public_Key_Size": pk_size,
            "Private_Key_Size": sk_size,
            "Signature_Size": sig_size,
            "Daily_Uploads": daily_uploads,
            "Onchain_Per_Upload": onchain_per_upload,
            "Daily_Onchain_KB": round(_bytes_to_kb(onchain_daily), 3),
            "Monthly_Onchain_MB": round(_bytes_to_mb(onchain_monthly), 3),
            "Daily_Offchain_KB": round(_bytes_to_kb(offchain_daily), 3),
            "Monthly_Offchain_MB": round(_bytes_to_mb(offchain_monthly), 3),
        })

    df = pd.DataFrame(rows, columns=[
        "Scheme",
        "Algorithm",
        "Public_Key_Size",
        "Private_Key_Size",
        "Signature_Size",
        "Daily_Uploads",
        "Onchain_Per_Upload",
        "Daily_Onchain_KB",
        "Monthly_Onchain_MB",
        "Daily_Offchain_KB",
        "Monthly_Offchain_MB",
    ])
    return df


if __name__ == "__main__":
    print(compute_scheme_storage().to_string(index=False))
