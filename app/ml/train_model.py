"""
Model Training - Train Random Forest Classifier.

Usage:
    from app.ml.train_model import ModelTrainer
    trainer = ModelTrainer()
    trainer.load_data("data/raw/training_data.csv")
    trainer.train()
    trainer.evaluate()
    trainer.save_model("models/rf_network_selector.pkl")
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
from .feature_engineering import FeatureEngineer
from app.core.constants import MLConfig


class ModelTrainer:
    """
    Train và evaluate Random Forest model.
    """
    
    def __init__(self, n_estimators=None, max_depth=None, random_state=None):
        """
        Initialize model với hyperparameters từ MLConfig.
        
        Args:
            n_estimators: Số lượng trees (default từ MLConfig)
            max_depth: Độ sâu tối đa của tree (default từ MLConfig)
            random_state: Random seed (default từ MLConfig)
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators or MLConfig.N_ESTIMATORS,
            max_depth=max_depth or MLConfig.MAX_DEPTH,
            random_state=random_state or MLConfig.RANDOM_STATE,
            n_jobs=-1  # Use all CPU cores
        )
        self.feature_engineer = FeatureEngineer()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_pred = None
        self.network_labels = {0: 'Wi-Fi', 1: '5G', 2: 'BLE'}
    
    def load_data(self, filepath: str, test_size=0.2):
        """
        Load data từ CSV và split train/test.
        
        Args:
            filepath: Path to CSV file
            test_size: Tỷ lệ test set
        """
        # Kiểm tra file tồn tại
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"\n❌ File không tồn tại: {filepath}\n"
                f"\n💡 Hướng dẫn:\n"
                f"   1. Chạy script thu thập dữ liệu:\n"
                f"      python scripts/collect_training_data.py --samples 1000\n"
                f"   2. Hoặc copy file training_data.csv vào thư mục data/raw/\n"
            )
        
        print(f"📂 Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        
        # Kiểm tra missing values
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            print(f"⚠️  Warning: Found {missing_count} missing values. Dropping rows...")
            df = df.dropna()
            print(f"✅ After cleanup: {df.shape}")
        
        print(f"📊 Dataset shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Feature engineering
        X, y = self.feature_engineer.fit_transform(df)
        
        # Train/test split sử dụng MLConfig
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size or MLConfig.TEST_SIZE, random_state=MLConfig.RANDOM_STATE, stratify=y
        )
        
        print(f"✅ Train set: {self.X_train.shape}")
        print(f"✅ Test set: {self.X_test.shape}")
        
        # In distribution của labels với percentage
        print(f"\n📊 Label distribution (Training set):")
        unique, counts = np.unique(self.y_train, return_counts=True)
        for label, count in zip(unique, counts):
            percentage = (count / len(self.y_train)) * 100
            print(f"   {self.network_labels[label]}: {count} samples ({percentage:.1f}%)")
    
    def train(self):
        """Train model trên training data."""
        print(f"\n🚀 Training Random Forest model...")
        print(f"   n_estimators: {self.model.n_estimators}")
        print(f"   max_depth: {self.model.max_depth}")
        
        self.model.fit(self.X_train, self.y_train)
        
        # Training accuracy
        train_acc = self.model.score(self.X_train, self.y_train)
        print(f"✅ Training accuracy: {train_acc:.4f}")
        
        # Cross-validation
        print(f"\n🔄 Running 5-fold cross-validation...")
        cv_scores = cross_val_score(self.model, self.X_train, self.y_train, cv=5, n_jobs=-1)
        print(f"   CV scores: {[f'{s:.4f}' for s in cv_scores]}")
        print(f"✅ CV mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    def evaluate(self, save_plots=False, output_dir="models"):
        """
        Evaluate model performance trên test set.
        
        Args:
            save_plots: Có lưu plots không (cho báo cáo)
            output_dir: Thư mục lưu plots
        
        Returns:
            Dict chứa metrics
        """
        print(f"\n📊 Evaluating on test set...")
        
        self.y_pred = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, self.y_pred)
        
        print(f"✅ Test accuracy: {accuracy:.4f}")
        
        # Classification Report
        print(f"\n📋 Classification Report:")
        report = classification_report(
            self.y_test, 
            self.y_pred,
            target_names=list(self.network_labels.values()),
            digits=4
        )
        print(report)
        
        # Confusion Matrix
        print(f"\n🔢 Confusion Matrix:")
        cm = confusion_matrix(self.y_test, self.y_pred)
        
        # In confusion matrix với format đẹp
        cm_df = pd.DataFrame(
            cm,
            index=list(self.network_labels.values()),
            columns=list(self.network_labels.values())
        )
        print(cm_df)
        
        # Feature Importance
        print(f"\n🎯 Top 10 Feature Importances:")
        feature_importance = pd.DataFrame({
            'feature': self.feature_engineer.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(feature_importance.head(10).to_string(index=False))
        
        # Save plots nếu cần (cho báo cáo đồ án)
        if save_plots:
            self._save_evaluation_plots(cm, feature_importance, output_dir)
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': cm,
            'classification_report': report,
            'feature_importance': feature_importance
        }
    
    def _save_evaluation_plots(self, cm, feature_importance, output_dir):
        """
        Lưu các plots cho báo cáo đồ án.
        
        Args:
            cm: Confusion matrix
            feature_importance: DataFrame feature importance
            output_dir: Thư mục output
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Feature Importance Bar Chart (Top 10)
        plt.figure(figsize=(10, 6))
        top_features = feature_importance.head(10)
        
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))
        bars = plt.barh(range(len(top_features)), top_features['importance'], color=colors)
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Importance Score', fontsize=12, fontweight='bold')
        plt.ylabel('Features', fontsize=12, fontweight='bold')
        plt.title('Top 10 Feature Importances - Random Forest Model', 
                 fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Thêm giá trị vào bars
        for i, (idx, row) in enumerate(top_features.iterrows()):
            plt.text(row['importance'] + 0.003, i, f"{row['importance']:.4f}", 
                    va='center', fontsize=9, fontweight='bold')
        
        plt.grid(axis='x', alpha=0.3, linestyle='--')
        plt.tight_layout()
        fi_path = os.path.join(output_dir, 'feature_importance.png')
        plt.savefig(fi_path, dpi=300, bbox_inches='tight')
        print(f"\n📊 Feature importance chart saved to: {fi_path}")
        plt.close()
        
        # 2. Confusion Matrix Heatmap
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Vẽ heatmap
        im = ax.imshow(cm, cmap='Blues')
        
        # Thêm colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Count', rotation=-90, va="bottom", fontweight='bold')
        
        # Thiết lập ticks
        ax.set_xticks(np.arange(len(self.network_labels)))
        ax.set_yticks(np.arange(len(self.network_labels)))
        ax.set_xticklabels(list(self.network_labels.values()))
        ax.set_yticklabels(list(self.network_labels.values()))
        
        # Xoay labels
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
        
        # Thêm giá trị vào cells
        for i in range(len(self.network_labels)):
            for j in range(len(self.network_labels)):
                text = ax.text(j, i, cm[i, j],
                             ha="center", va="center", 
                             color="white" if cm[i, j] > cm.max() / 2 else "black",
                             fontsize=14, fontweight='bold')
        
        ax.set_title('Confusion Matrix - Random Forest Model', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        
        fig.tight_layout()
        cm_path = os.path.join(output_dir, 'confusion_matrix.png')
        plt.savefig(cm_path, dpi=300, bbox_inches='tight')
        print(f"📊 Confusion matrix saved to: {cm_path}")
        plt.close()
    
    def save_model(self, filepath: str):
        """
        Lưu trained model và feature engineer.
        
        Args:
            filepath: Path to save model (.pkl)
        """
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        joblib.dump(self.model, filepath)
        print(f"💾 Model saved to {filepath}")
        
        # Save feature engineer
        fe_path = filepath.replace('.pkl', '_feature_engineer.pkl')
        self.feature_engineer.save(fe_path)
    
    @staticmethod
    def load_model(filepath: str):
        """
        Load trained model.
        
        Args:
            filepath: Path to model file
            
        Returns:
            Loaded RandomForestClassifier
        """
        return joblib.load(filepath)


def _parse_args():
    parser = argparse.ArgumentParser(description="Train Random Forest for network selection")
    parser.add_argument("--data", default=MLConfig.TRAINING_DATA_PATH, help="Path to training CSV")
    parser.add_argument("--model", default=MLConfig.MODEL_PATH, help="Output model path (.pkl)")
    parser.add_argument("--test-size", type=float, default=MLConfig.TEST_SIZE, help="Test split ratio")
    parser.add_argument("--no-save-plots", action="store_true", help="Disable saving evaluation plots")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    trainer = ModelTrainer()
    trainer.load_data(args.data, test_size=args.test_size)
    trainer.train()
    trainer.evaluate(save_plots=not args.no_save_plots, output_dir=os.path.dirname(args.model) or "models")
    trainer.save_model(args.model)
