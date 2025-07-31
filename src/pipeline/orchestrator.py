"""
Automated ML Training Pipeline Orchestrator
Coordinates data processing, feature engineering, model training, and validation
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import mlflow
import mlflow.sklearn
from datetime import datetime
import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import numpy as np

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class MLPipelineOrchestrator:
    """Orchestrates the complete ML training pipeline"""
    
    def __init__(self, config_path: str, mlflow_uri: str = "databricks"):
        self.config_path = config_path
        self.mlflow_uri = mlflow_uri
        self.config = self._load_config()
        self.setup_logging()
        self.setup_mlflow()
        
        # Pipeline paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_raw = self.project_root / "data" / "raw" / "house_data.csv"
        self.data_cleaned = self.project_root / "data" / "processed" / "cleaned_house_data.csv"
        self.data_featured = self.project_root / "data" / "processed" / "featured_house_data.csv"
        self.models_dir = self.project_root / "models" / "trained"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler('pipeline.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_mlflow(self):
        """Setup MLflow tracking"""
        try:
            self.logger.info(f"Setting up MLflow: {self.mlflow_uri}")
            mlflow.set_tracking_uri(self.mlflow_uri)
            
            # Set or create experiment
            experiment_name = "/Users/michaeloppong731@gmail.com/house_price_pipeline"
            try:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if experiment:
                    mlflow.set_experiment(experiment_name)
                else:
                    mlflow.create_experiment(experiment_name)
                    mlflow.set_experiment(experiment_name)
            except Exception:
                mlflow.set_experiment("Default")
                
        except Exception as e:
            self.logger.error(f"MLflow setup failed: {e}")
            raise
    
    def run_data_processing(self) -> bool:
        """Execute data processing step"""
        self.logger.info("Processing data...")
        
        try:
            cmd = [
                sys.executable, 
                str(self.project_root / "src" / "data" / "run_processing.py"),
                "--input", str(self.data_raw),
                "--output", str(self.data_cleaned)
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("Data processing completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Data processing failed: {e}")
            return False
    
    def run_feature_engineering(self) -> bool:
        """Execute feature engineering step"""
        self.logger.info("Engineering features...")
        
        try:
            cmd = [
                sys.executable,
                str(self.project_root / "src" / "features" / "engineer.py"),
                "--input", str(self.data_cleaned),
                "--output", str(self.data_featured),
                "--preprocessor", str(self.models_dir / "preprocessor.pkl")
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("Feature engineering completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Feature engineering failed: {e}")
            return False
    
    def run_model_training(self) -> bool:
        """Execute model training step"""
        self.logger.info("Training model...")
        
        try:
            cmd = [
                sys.executable,
                str(self.project_root / "src" / "models" / "train_model.py"),
                "--config", str(self.config_path),
                "--data", str(self.data_featured),
                "--models-dir", str(self.models_dir),
                "--mlflow-tracking-uri", self.mlflow_uri
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("Model training completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Model training failed: {e}")
            return False
    
    def validate_model(self) -> Dict[str, Any]:
        """Validate the trained model against quality thresholds"""
        self.logger.info("Validating model...")
        
        try:
            model_path = self.models_dir / "house_price_model.pkl"
            if not model_path.exists():
                raise FileNotFoundError("Model not found")
            
            model = joblib.load(model_path)
            data = pd.read_csv(self.data_featured)
            
            # Use last 20% for validation
            val_size = int(len(data) * 0.2)
            val_data = data.tail(val_size)
            
            target_col = self.config.get('model', {}).get('target_variable', 'price')
            feature_cols = [col for col in val_data.columns if col != target_col]
            
            X_val = val_data[feature_cols]
            y_val = val_data[target_col]
            y_pred = model.predict(X_val)
            
            # Calculate metrics
            mae = mean_absolute_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            
            # Quality thresholds
            validation_passed = r2 >= 0.60 and mae <= 25000 and rmse <= 30000
            
            results = {
                'mae': mae,
                'r2_score': r2,
                'rmse': rmse,
                'validation_samples': len(val_data),
                'validation_passed': validation_passed
            }
            
            self.logger.info(f"Validation: R²={r2:.3f}, MAE={mae:.0f}, RMSE={rmse:.0f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Model validation failed: {e}")
            return {'validation_passed': False, 'error': str(e)}
    
    def register_model_in_mlflow(self, validation_results: Dict[str, Any]) -> Optional[str]:
        """Register the validated model in MLflow Model Registry"""
        if not validation_results.get('validation_passed', False):
            self.logger.warning("Model validation failed, skipping MLflow registration")
            return None
        
        self.logger.info("Registering model in MLflow...")
        
        try:
            model_name = "house_price_predictor"
            model_path = self.models_dir / "house_price_model.pkl"
            
            if not model_path.exists():
                self.logger.error("Model file not found")
                return None
            
            with mlflow.start_run(run_name=f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
                # Log metrics
                metrics = {
                    'validation_mae': validation_results['mae'],
                    'validation_r2': validation_results['r2_score'],
                    'validation_rmse': validation_results['rmse'],
                    'validation_samples': validation_results['validation_samples']
                }
                mlflow.log_metrics(metrics)
                mlflow.log_dict(self.config, "model_config.yaml")
                
                # Log model
                model = joblib.load(model_path)
                try:
                    mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)
                    self.logger.info(f"Model registered as: {model_name}")
                except Exception as registry_error:
                    if "legacy workspace model registry is disabled" in str(registry_error):
                        mlflow.sklearn.log_model(model, "model")
                        self.logger.info("Model logged (registry disabled)")
                    else:
                        raise registry_error
                
                self.logger.info("MLflow registration completed")
                return run.info.run_id
                
        except Exception as e:
            self.logger.error(f"Failed to register model in MLflow: {e}")
            return None
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Execute the complete ML pipeline"""
        self.logger.info("Starting ML pipeline...")
        
        steps = [
            ("Data Processing", self.run_data_processing),
            ("Feature Engineering", self.run_feature_engineering),
            ("Model Training", self.run_model_training),
        ]
        
        # Execute pipeline steps
        for step_name, step_func in steps:
            if not step_func():
                self.logger.error(f"{step_name} failed")
                return {'overall_success': False, 'failed_step': step_name}
        
        # Validate model
        validation_results = self.validate_model()
        if not validation_results.get('validation_passed', False):
            self.logger.error("Model validation failed")
            return {'overall_success': False, 'failed_step': 'validation', 'validation_results': validation_results}
        
        # Register model
        model_version = self.register_model_in_mlflow(validation_results)
        if not model_version:
            self.logger.error("Model registration failed")
            return {'overall_success': False, 'failed_step': 'registration'}
        
        self.logger.info("ML pipeline completed successfully!")
        return {
            'overall_success': True,
            'validation_results': validation_results,
            'model_version': model_version
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run ML Pipeline")
    parser.add_argument("--config", required=True, help="Path to model config YAML")
    parser.add_argument("--mlflow-uri", default="databricks", help="MLflow tracking URI")
    
    args = parser.parse_args()
    
    orchestrator = MLPipelineOrchestrator(args.config, args.mlflow_uri)
    results = orchestrator.run_full_pipeline()
    
    print("\n" + "="*50)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*50)
    print(f"Overall Success: {results['overall_success']}")
    
    if results['overall_success']:
        validation = results.get('validation_results', {})
        print(f"Model R² Score: {validation.get('r2_score', 'N/A'):.3f}")
        print(f"Model Version: {results.get('model_version', 'N/A')}")
    else:
        print(f"Failed Step: {results.get('failed_step', 'Unknown')}")
    
    print("="*50)