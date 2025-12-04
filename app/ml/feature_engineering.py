"""
Feature Engineering - Xử lý và chuẩn bị features cho ML model.

Bao gồm:
- Feature extraction từ DeviceState
- Encoding categorical variables (task, network)
- Scaling numerical features (optional)
- Feature selection
"""

from typing import Dict, List
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib


class FeatureEngineer:
    """
    Xử lý features cho ML model.
    """
    
    def __init__(self):
        """Initialize encoders và scalers"""
        self.task_encoder = LabelEncoder()
        self.network_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_columns = []
    
    def fit_transform(self, df: pd.DataFrame) -> tuple:
        """
        Fit encoders/scalers và transform features.
        
        Args:
            df: DataFrame với raw features
            
        Returns:
            Tuple (X, y) - feature matrix và labels
        """
        # Separate features and labels
        y = df['optimal_network'].values
        X_df = df.drop('optimal_network', axis=1)
        
        # Store feature columns
        self.feature_columns = list(X_df.columns)
        
        # Convert to numpy array
        X = X_df.values
        
        # Optional: Fit và transform với StandardScaler
        # X = self.scaler.fit_transform(X)
        
        return X, y
    
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform features sử dụng fitted encoders/scalers.
        
        Args:
            df: DataFrame với raw features
            
        Returns:
            Transformed feature matrix
        """
        # Ensure same column order
        X_df = df[self.feature_columns]
        X = X_df.values
        
        # Optional: Transform với fitted scaler
        # X = self.scaler.transform(X)
        
        return X
    
    def save(self, filepath: str):
        """
        Lưu feature engineer (scaler, encoders).
        
        Args:
            filepath: Path to save (.pkl)
        """
        joblib.dump({
            'scaler': self.scaler,
            'task_encoder': self.task_encoder,
            'network_encoder': self.network_encoder,
            'feature_columns': self.feature_columns
        }, filepath)
        print(f"💾 FeatureEngineer saved to {filepath}")
    
    @staticmethod
    def load(filepath: str):
        """
        Load feature engineer từ file.
        
        Args:
            filepath: Path to .pkl file
            
        Returns:
            FeatureEngineer instance
        """
        data = joblib.load(filepath)
        fe = FeatureEngineer()
        fe.scaler = data['scaler']
        fe.task_encoder = data['task_encoder']
        fe.network_encoder = data['network_encoder']
        fe.feature_columns = data['feature_columns']
        return fe
