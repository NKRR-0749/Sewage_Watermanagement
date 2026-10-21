import pandas as pd
import matplotlib.pyplot as plt
import os

def run_visualizations():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 12 -- Visualization")
    print("=" * 80)

    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'processed', 'simulation_results.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Please ensure Phase 11 has run successfully.")
        return

    # Read the data
    df = pd.read_csv(csv_path)

    # We will create a figure with multiple subplots
    fig, axes = plt.subplots(3, 1, figsize=(10, 15))
    fig.suptitle('Sewage Network Simulation Results', fontsize=16)

    # 1. Water Quality: Turbidity over time for each station
    ax1 = axes[0]
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        ax1.plot(station_data['step'], station_data['turbidity'], label=station, marker='o', markersize=4)
    ax1.set_title('Turbidity vs Simulation Step')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Turbidity (NTU)')
    ax1.legend()
    ax1.grid(True)

    # 2. Pollution: Anomaly Score over time
    ax2 = axes[1]
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        ax2.plot(station_data['step'], station_data['anomaly_score'], label=station, marker='x', markersize=4)
    ax2.set_title('Anomaly Score vs Simulation Step')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Anomaly Score')
    ax2.legend()
    ax2.grid(True)

    # 3. Treatment: Treatment Cycles per Station
    ax3 = axes[2]
    # Bar chart of total treatment cycles per station
    treatment_totals = df.groupby('station')['treatment_cycles'].sum()
    stations = treatment_totals.index
    cycles = treatment_totals.values
    
    ax3.bar(stations, cycles, color='skyblue')
    ax3.set_title('Total Treatment Cycles per Station')
    ax3.set_xlabel('Station')
    ax3.set_ylabel('Total Cycles')
    ax3.grid(axis='y')

    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    # Save the plot
    output_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, 'dashboard.png')
    plt.savefig(plot_path)
    
    print(f"Visualizations generated and saved to: {plot_path}")
    print("Opening the dashboard...")
    plt.show()

if __name__ == '__main__':
    run_visualizations()
