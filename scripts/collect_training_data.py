"""
Script thu thập training data từ simulation.

Usage:
    python scripts/collect_training_data.py --samples 1000 --output data/raw/training_data.csv
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from app.services.simulation import SimulationEngine
from app.ml.data_collector import DataCollector


def main():
    """CLI for data collection"""
    parser = argparse.ArgumentParser(description="Collect training data from simulation")
    parser.add_argument("--samples", type=int, default=1000, help="Number of samples to collect")
    parser.add_argument("--output", type=str, default="data/raw/training_data.csv", help="Output file path")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 IoT Network Selection - Data Collection")
    print("=" * 60)
    print(f"📊 Target samples: {args.samples}")
    print(f"💾 Output file: {args.output}")
    print()
    
    # Initialize simulation engine
    print("⚙️ Initializing simulation engine...")
    engine = SimulationEngine()
    
    # Initialize data collector
    collector = DataCollector(engine, engine.network_configs)
    
    # Collect data
    collector.collect(num_samples=args.samples)
    
    # Save dataset
    collector.save_dataset(args.output)
    
    print()
    print("=" * 60)
    print("✅ Data collection complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
