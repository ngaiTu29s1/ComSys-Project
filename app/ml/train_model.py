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
from .feature_engineering import FeatureEngineer


class ModelTrainer:
    """
    Train và evaluate Random Forest model.
    """
    
    def __init__(self, n_estimators=100, max_depth=15, random_state=42):
        """
        Initialize model với hyperparameters.
        
        Args:
            n_estimators: Số lượng trees
            max_depth: Độ sâu tối đa của tree
            random_state: Random seed
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1  # Use all CPU cores
        )
        self.feature_engineer = FeatureEngineer()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.network_labels = {0: 'Wi-Fi', 1: '5G', 2: 'BLE'}
    
    def load_data(self, filepath: str, test_size=0.2):
        """
        Load data từ CSV và split train/test.
        
        Args:
            filepath: Path to CSV file
            test_size: Tỷ lệ test set
        """
        print(f"📂 Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        
        print(f"📊 Dataset shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Feature engineering
        X, y = self.feature_engineer.fit_transform(df)
        
        # Train/test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"✅ Train set: {self.X_train.shape}")
        print(f"✅ Test set: {self.X_test.shape}")
        print(f"📊 Label distribution:")
        unique, counts = np.unique(self.y_train, return_counts=True)
        for label, count in zip(unique, counts):
            print(f"   {self.network_labels[label]}: {count} samples")
    
    def train(self):
        """Train model trên training data."""
        print(f"\n🚀 Training Random Forest model...")
        self.model.fit(self.X_train, self.y_train)
        
        # Training accuracy
        train_acc = self.model.score(self.X_train, self.y_train)
        print(f"✅ Training accuracy: {train_acc:.4f}")
        
        # Cross-validation
        print(f"🔄 Running 5-fold cross-validation...")
        cv_scores = cross_val_score(self.model, self.X_train, self.y_train, cv=5)
        print(f"✅ CV scores: {cv_scores}")
        print(f"✅ CV mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    def evaluate(self):
        """
        Evaluate model performance trên test set.
        
        Returns:
            Dict chứa metrics
        """
        print(f"\n📊 Evaluating on test set...")
        
        y_pred = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        
        print(f"✅ Test accuracy: {accuracy:.4f}")
        print(f"\n📋 Classification Report:")
        print(classification_report(
            self.y_test, 
            y_pred,
            target_names=list(self.network_labels.values())
        ))
        
        print(f"\n🔢 Confusion Matrix:")
        cm = confusion_matrix(self.y_test, y_pred)
        print(cm)
        
        # Feature importance
        print(f"\n🎯 Top 10 Feature Importances:")
        feature_importance = pd.DataFrame({
            'feature': self.feature_engineer.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(feature_importance.head(10).to_string(index=False))
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': cm,
            'feature_importance': feature_importance
        }
    
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
