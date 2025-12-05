"""
Script train Random Forest model.

Usage:
    python scripts/train_model.py --data data/raw/training_data.csv --output models/rf_network_selector.pkl
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from app.ml.train_model import ModelTrainer


def main():
    """CLI for model training"""
    parser = argparse.ArgumentParser(description="Train Random Forest model")
    parser.add_argument("--data", type=str, default="data/raw/training_data.csv", help="Path to training data CSV")
    parser.add_argument("--output", type=str, default="models/rf_network_selector.pkl", help="Output model path")
    parser.add_argument("--n-estimators", type=int, default=100, help="Number of trees")
    parser.add_argument("--max-depth", type=int, default=15, help="Max tree depth")
    parser.add_argument("--save-plots", action="store_true", help="Save evaluation plots for report")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 IoT Network Selection - Model Training")
    print("=" * 60)
    print(f"📊 Data: {args.data}")
    print(f"💾 Output: {args.output}")
    print(f"🌲 n_estimators: {args.n_estimators}")
    print(f"📏 max_depth: {args.max_depth}")
    print()
    
    # Initialize trainer
    trainer = ModelTrainer(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    
    # Load data
    trainer.load_data(args.data)
    
    # Train
    trainer.train()
    
    # Evaluate (with optional plot saving)
    output_dir = os.path.dirname(args.output)
    trainer.evaluate(save_plots=args.save_plots, output_dir=output_dir)
    
    # Save model
    trainer.save_model(args.output)
    
    print()
    print("=" * 60)
    print("✅ Model training complete!")
    print("=" * 60)
    print(f"📦 Model saved to: {args.output}")
    print(f"📦 Feature engineer saved to: {args.output.replace('.pkl', '_feature_engineer.pkl')}")


if __name__ == "__main__":
    main()
