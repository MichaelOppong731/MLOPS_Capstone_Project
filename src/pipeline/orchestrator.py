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
    
    def __init__(self, config_path: str, mlflow_uri: str = "http://localhost:5555"):
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
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pipeline.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_mlflow(self):
        """Setup MLflow tracking"""
        mlflow.set_tracking_uri(self.mlflow_uri)
        mlflow.set_experiment("house_price_pipeline")
        self.logger.info(f"MLflow tracking URI set to: {self.mlflow_uri}")
    
    def run_data_processing(self) -> bool:
        """Execute data processing step"""
        self.logger.info("Starting data processing...")
        
        try:
            cmd = [
                sys.executable, 
                str(self.project_root / "src" / "data" / "run_processing.py"),
                "--input", str(self.data_raw),
                "--output", str(self.data_cleaned)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("Data processing completed successfully")
            self.logger.debug(f"Output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Data processing failed: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return False
    
    def run_feature_engineering(self) -> bool:
        """Execute feature engineering step"""
        self.logger.info("Starting feature engineering...")
        
        try:
            cmd = [
                sys.executable,
                str(self.project_root / "src" / "features" / "engineer.py"),
                "--input", str(self.data_cleaned),
                "--output", str(self.data_featured),
                "--preprocessor", str(self.models_dir / "preprocessor.pkl")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("Feature engineering completed successfully")
            self.logger.debug(f"Output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Feature engineering failed: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return False
    
    def run_model_training(self) -> bool:
        """Execute model training step"""
        self.logger.info("Starting model training...")
        
        try:
            cmd = [
                sys.executable,
                str(self.project_root / "src" / "models" / "train_model.py"),
                "--config", str(self.config_path),
                "--data", str(self.data_featured),
                "--models-dir", str(self.models_dir),
                "--mlflow-tracking-uri", self.mlflow_uri
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info("Model training completed successfully")
            self.logger.debug(f"Output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Model training failed: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return False
    
    def validate_model(self) -> Dict[str, Any]:
        """Validate the trained model against quality thresholds"""
        self.logger.info("Starting model validation...")
        
        try:
            # Load the trained model and preprocessor
            model_path = self.models_dir / "house_price_model.pkl"
            preprocessor_path = self.models_dir / "preprocessor.pkl"
            
            if not model_path.exists() or not preprocessor_path.exists():
                raise FileNotFoundError("Model or preprocessor not found")
            
            model = joblib.load(model_path)
            preprocessor = joblib.load(preprocessor_path)
            
            # Load test data (using a portion of featured data for validation)
            data = pd.read_csv(self.data_featured)
            
            # Split for validation (last 20% as validation set)
            val_size = int(len(data) * 0.2)
            val_data = data.tail(val_size)
            
            # Prepare features and target
            target_col = self.config.get('model', {}).get('target_variable', 'price')
            feature_cols = [col for col in val_data.columns if col != target_col]
            
            X_val = val_data[feature_cols]
            y_val = val_data[target_col]
            
            # Make predictions
            y_pred = model.predict(X_val)
            
            # Calculate metrics
            mae = mean_absolute_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            
            validation_results = {
                'mae': mae,
                'r2_score': r2,
                'rmse': rmse,
                'validation_samples': len(val_data)
            }
            
            # Define quality thresholds
            thresholds = {
                'min_r2_score': 0.85,  # Minimum R² score
                'max_mae': 15000,      # Maximum MAE
                'max_rmse': 20000      # Maximum RMSE
            }
            
            # Check if model meets quality standards
            validation_passed = (
                r2 >= thresholds['min_r2_score'] and
                mae <= thresholds['max_mae'] and
                rmse <= thresholds['max_rmse']
            )
            
            validation_results['validation_passed'] = validation_passed
            validation_results['thresholds'] = thresholds
            
            self.logger.info(f"Model validation results: {validation_results}")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Model validation failed: {e}")
            return {'validation_passed': False, 'error': str(e)}
    
    def register_model_in_mlflow(self, validation_results: Dict[str, Any]) -> Optional[str]:
        """Register the validated model in MLflow Model Registry"""
        if not validation_results.get('validation_passed', False):
            self.logger.warning("Model validation failed, skipping registration")
            return None
        
        try:
            model_name = "house_price_predictor"
            model_path = self.models_dir / "house_price_model.pkl"
            preprocessor_path = self.models_dir / "preprocessor.pkl"
            
            with mlflow.start_run(run_name=f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log model artifacts
                mlflow.sklearn.log_model(
                    joblib.load(model_path),
                    "model",
                    registered_model_name=model_name
                )
                
                # Log preprocessor
                mlflow.log_artifact(str(preprocessor_path), "preprocessor")
                
                # Log validation metrics
                mlflow.log_metrics({
                    'validation_mae': validation_results['mae'],
                    'validation_r2': validation_results['r2_score'],
                    'validation_rmse': validation_results['rmse']
                })
                
                # Log model config
                mlflow.log_dict(self.config, "model_config.yaml")
                
                # Get the model version
                client = mlflow.tracking.MlflowClient()
                model_version = client.get_latest_versions(model_name, stages=["None"])[0]
                
                # Transition to Staging if validation passed
                client.transition_model_version_stage(
                    name=model_name,
                    version=model_version.version,
                    stage="Staging"
                )
                
                self.logger.info(f"Model registered in MLflow as version {model_version.version}")
                return model_version.version
                
        except Exception as e:
            self.logger.error(f"Failed to register model in MLflow: {e}")
            return None
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Execute the complete ML pipeline"""
        self.logger.info("Starting full ML pipeline execution...")
        
        pipeline_results = {
            'start_time': datetime.now().isoformat(),
            'steps_completed': [],
            'steps_failed': [],
            'overall_success': False
        }
        
        # Step 1: Data Processing
        if self.run_data_processing():
            pipeline_results['steps_completed'].append('data_processing')
        else:
            pipeline_results['steps_failed'].append('data_processing')
            return pipeline_results
        
        # Step 2: Feature Engineering
        if self.run_feature_engineering():
            pipeline_results['steps_completed'].append('feature_engineering')
        else:
            pipeline_results['steps_failed'].append('feature_engineering')
            return pipeline_results
        
        # Step 3: Model Training
        if self.run_model_training():
            pipeline_results['steps_completed'].append('model_training')
        else:
            pipeline_results['steps_failed'].append('model_training')
            return pipeline_results
        
        # Step 4: Model Validation
        validation_results = self.validate_model()
        if validation_results.get('validation_passed', False):
            pipeline_results['steps_completed'].append('model_validation')
            pipeline_results['validation_results'] = validation_results
        else:
            pipeline_results['steps_failed'].append('model_validation')
            pipeline_results['validation_results'] = validation_results
            return pipeline_results
        
        # Step 5: Model Registration
        model_version = self.register_model_in_mlflow(validation_results)
        if model_version:
            pipeline_results['steps_completed'].append('model_registration')
            pipeline_results['model_version'] = model_version
        else:
            pipeline_results['steps_failed'].append('model_registration')
            return pipeline_results
        
        pipeline_results['overall_success'] = True
        pipeline_results['end_time'] = datetime.now().isoformat()
        
        self.logger.info("Full ML pipeline completed successfully!")
        return pipeline_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run ML Pipeline")
    parser.add_argument("--config", required=True, help="Path to model config YAML")
    parser.add_argument("--mlflow-uri", default="http://localhost:5555", help="MLflow tracking URI")
    
    args = parser.parse_args()
    
    orchestrator = MLPipelineOrchestrator(args.config, args.mlflow_uri)
    results = orchestrator.run_full_pipeline()
    
    print("\n" + "="*50)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*50)
    print(f"Overall Success: {results['overall_success']}")
    print(f"Steps Completed: {', '.join(results['steps_completed'])}")
    if results['steps_failed']:
        print(f"Steps Failed: {', '.join(results['steps_failed'])}")
    print("="*50)