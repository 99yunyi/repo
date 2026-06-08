import os
from bpcs_simulation.storage_calc import compute_scheme_storage
from bpcs_simulation.crypto_bench import bench_all
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    os.makedirs('bpcs_simulation/results', exist_ok=True)
    sdf = compute_scheme_storage()
    benches = bench_all()

    order = ['ECDSA (no batch)','ECDSA+Batch','SLH-DSA+Batch','ML-DSA-44+Batch']
    sdf = sdf.set_index('Scheme').loc[order].reset_index()

    # Plot 1
    onchain = sdf['Monthly_Onchain_MB'].astype(float)
    offchain = sdf['Monthly_Offchain_MB'].astype(float)
    x = range(len(sdf))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9,5))
    ax.bar([i-width/2 for i in x], onchain, width, label='Monthly On-chain (100 nodes) (MB)')
    ax.bar([i+width/2 for i in x], offchain, width, label='Monthly Off-chain per Enterprise (MB)')
    ax.set_xticks(x)
    ax.set_xticklabels(sdf['Scheme'], rotation=20, ha='right')
    ax.set_ylabel('MB')
    ax.set_title('100 nodes, 5000 IoC/day — On-chain vs Off-chain Monthly Storage')
    ax.legend()
    plt.tight_layout()
    plt.savefig('bpcs_simulation/results/storage_comparison.png', bbox_inches='tight')
    plt.close(fig)

    # Plot 2: aggregate daily verification
    verify_ms = []
    for _, row in sdf.iterrows():
        alg = row['Algorithm']
        v = benches.get(alg, benches.get('ecdsa', {})).get('verify_ms', 0)
        agg = row['Daily_Uploads'] * v
        verify_ms.append(agg)

    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(x, verify_ms)
    ax.set_xticks(x)
    ax.set_xticklabels(sdf['Scheme'], rotation=20, ha='right')
    ax.set_ylabel('ms')
    ax.set_title('Aggregate Daily Verification Time (ms)')
    plt.tight_layout()
    plt.savefig('bpcs_simulation/results/daily_verify.png', bbox_inches='tight')
    plt.close(fig)

    print('WROTE bpcs_simulation/results/storage_comparison.png and daily_verify.png')

if __name__ == '__main__':
    main()
