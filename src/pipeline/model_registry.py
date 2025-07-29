"""
Enhanced MLflow Model Registry Integration
Handles model versioning, staging, and promotion workflows
"""

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from typing import Dict, Any, List, Optional
import logging
import pandas as pd
import joblib
from pathlib import Path
import json
from datetime import datetime

class ModelRegistry:
    """Enhanced MLflow Model Registry for model lifecycle management"""
    
    def __init__(self, tracking_uri: str = "http://localhost:5555"):
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
        self.logger = logging.getLogger(__name__)
        
    def register_model(self, 
                      model_path: str, 
                      preprocessor_path: str,
                      model_name: str,
                      config: Dict[str, Any],
                      validation_results: Dict[str, Any],
                      experiment_name: str = "house_price_pipeline") -> Optional[str]:
        """Register a new model version with comprehensive metadata"""
        
        try:
            mlflow.set_experiment(experiment_name)
            
            with mlflow.start_run(run_name=f"model_registration_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
                # Load and log the model
                model = joblib.load(model_path)
                mlflow.sklearn.log_model(
                    model,
                    "model",
                    registered_model_name=model_name,
                    metadata={
                        "model_type": config.get('model', {}).get('best_model', 'unknown'),
                        "training_date": datetime.now().isoformat(),
                        "validation_passed": validation_results.get('validation_passed', False)
                    }
                )
                
                # Log preprocessor as artifact
                mlflow.log_artifact(preprocessor_path, "preprocessor")
                
                # Log model configuration
                mlflow.log_dict(config, "model_config.yaml")
                
                # Log validation metrics
                if 'validation_results' in validation_results:
                    val_metrics = validation_results['validation_results']
                    mlflow.log_metrics({
                        'validation_mae': val_metrics.get('mae', 0),
                        'validation_r2': val_metrics.get('r2_score', 0),
                        'validation_rmse': val_metrics.get('rmse', 0),
                        'validation_samples': val_metrics.get('validation_samples', 0)
                    })
                
                # Log comprehensive validation results
                mlflow.log_dict(validation_results, "validation_results.json")
                
                # Get the latest model version
                latest_versions = self.client.get_latest_versions(model_name, stages=["None"])
                if latest_versions:
                    model_version = latest_versions[0].version
                    
                    # Add detailed tags
                    self.client.set_model_version_tag(
                        model_name, 
                        model_version, 
                        "validation_status", 
                        "passed" if validation_results.get('validation_passed', False) else "failed"
                    )
                    
                    self.client.set_model_version_tag(
                        model_name,
                        model_version,
                        "model_type",
                        config.get('model', {}).get('best_model', 'unknown')
                    )
                    
                    self.client.set_model_version_tag(
                        model_name,
                        model_version,
                        "training_timestamp",
                        datetime.now().isoformat()
                    )
                    
                    # Automatically transition to Staging if validation passed
                    if validation_results.get('validation_passed', False):
                        self.promote_model(model_name, model_version, "Staging", 
                                         "Automatic promotion after successful validation")
                    
                    self.logger.info(f"Model registered successfully as version {model_version}")
                    return model_version
                
        except Exception as e:
            self.logger.error(f"Failed to register model: {e}")
            return None
    
    def promote_model(self, model_name: str, version: str, stage: str, description: str = "") -> bool:
        """Promote model to a specific stage"""
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage,
                archive_existing_versions=True
            )
            
            # Add promotion annotation
            self.client.update_model_version(
                name=model_name,
                version=version,
                description=f"{description} (Promoted on {datetime.now().isoformat()})"
            )
            
            self.logger.info(f"Model {model_name} v{version} promoted to {stage}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to promote model: {e}")
            return False
    
    def get_model_info(self, model_name: str, stage: str = "Production") -> Optional[Dict[str, Any]]:
        """Get information about a model in a specific stage"""
        try:
            versions = self.client.get_latest_versions(model_name, stages=[stage])
            if not versions:
                return None
            
            version = versions[0]
            
            # Get run information
            run = self.client.get_run(version.run_id)
            
            return {
                'name': model_name,
                'version': version.version,
                'stage': version.current_stage,
                'run_id': version.run_id,
                'creation_timestamp': version.creation_timestamp,
                'last_updated_timestamp': version.last_updated_timestamp,
                'description': version.description,
                'tags': dict(version.tags),
                'metrics': run.data.metrics,
                'params': run.data.params,
                'artifacts': [f.path for f in self.client.list_artifacts(version.run_id)]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get model info: {e}")
            return None
    
    def compare_models(self, model_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two model versions"""
        try:
            # Get model version details
            v1 = self.client.get_model_version(model_name, version1)
            v2 = self.client.get_model_version(model_name, version2)
            
            # Get run details
            run1 = self.client.get_run(v1.run_id)
            run2 = self.client.get_run(v2.run_id)
            
            comparison = {
                'model_name': model_name,
                'version1': {
                    'version': version1,
                    'stage': v1.current_stage,
                    'creation_date': datetime.fromtimestamp(v1.creation_timestamp / 1000).isoformat(),
                    'metrics': run1.data.metrics,
                    'tags': dict(v1.tags)
                },
                'version2': {
                    'version': version2,
                    'stage': v2.current_stage,
                    'creation_date': datetime.fromtimestamp(v2.creation_timestamp / 1000).isoformat(),
                    'metrics': run2.data.metrics,
                    'tags': dict(v2.tags)
                }
            }
            
            # Calculate metric differences
            metrics_comparison = {}
            common_metrics = set(run1.data.metrics.keys()) & set(run2.data.metrics.keys())
            
            for metric in common_metrics:
                v1_value = run1.data.metrics[metric]
                v2_value = run2.data.metrics[metric]
                
                metrics_comparison[metric] = {
                    'version1_value': v1_value,
                    'version2_value': v2_value,
                    'difference': v2_value - v1_value,
                    'percent_change': ((v2_value - v1_value) / v1_value * 100) if v1_value != 0 else 0,
                    'better_version': version2 if self._is_better_metric(metric, v2_value, v1_value) else version1
                }
            
            comparison['metrics_comparison'] = metrics_comparison
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Failed to compare models: {e}")
            return {}
    
    def _is_better_metric(self, metric_name: str, value1: float, value2: float) -> bool:
        """Determine if value1 is better than value2 for a given metric"""
        # For error metrics (MAE, RMSE), lower is better
        # For score metrics (R2), higher is better
        error_metrics = ['mae', 'rmse', 'mse', 'validation_mae', 'validation_rmse']
        score_metrics = ['r2', 'r2_score', 'validation_r2']
        
        metric_lower = metric_name.lower()
        
        if any(error_metric in metric_lower for error_metric in error_metrics):
            return value1 < value2
        elif any(score_metric in metric_lower for score_metric in score_metrics):
            return value1 > value2
        else:
            # Default: assume higher is better
            return value1 > value2
    
    def list_model_versions(self, model_name: str) -> List[Dict[str, Any]]:
        """List all versions of a model"""
        try:
            versions = self.client.search_model_versions(f"name='{model_name}'")
            
            version_list = []
            for version in versions:
                run = self.client.get_run(version.run_id)
                
                version_info = {
                    'version': version.version,
                    'stage': version.current_stage,
                    'creation_date': datetime.fromtimestamp(version.creation_timestamp / 1000).isoformat(),
                    'last_updated': datetime.fromtimestamp(version.last_updated_timestamp / 1000).isoformat(),
                    'description': version.description,
                    'tags': dict(version.tags),
                    'metrics': run.data.metrics,
                    'run_id': version.run_id
                }
                version_list.append(version_info)
            
            # Sort by version number (descending)
            version_list.sort(key=lambda x: int(x['version']), reverse=True)
            
            return version_list
            
        except Exception as e:
            self.logger.error(f"Failed to list model versions: {e}")
            return []
    
    def archive_old_versions(self, model_name: str, keep_latest: int = 5) -> bool:
        """Archive old model versions, keeping only the latest N versions"""
        try:
            versions = self.list_model_versions(model_name)
            
            # Keep versions in Production and Staging stages
            protected_stages = ['Production', 'Staging']
            versions_to_archive = []
            
            kept_count = 0
            for version in versions:
                if version['stage'] in protected_stages:
                    continue
                
                if kept_count >= keep_latest:
                    versions_to_archive.append(version['version'])
                else:
                    kept_count += 1
            
            # Archive old versions
            for version in versions_to_archive:
                self.client.transition_model_version_stage(
                    name=model_name,
                    version=version,
                    stage="Archived"
                )
                self.logger.info(f"Archived model {model_name} version {version}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to archive old versions: {e}")
            return False
    
    def get_production_model_path(self, model_name: str) -> Optional[str]:
        """Get the MLflow model URI for the production model"""
        try:
            versions = self.client.get_latest_versions(model_name, stages=["Production"])
            if versions:
                return f"models:/{model_name}/Production"
            else:
                # Fallback to Staging if no Production model
                versions = self.client.get_latest_versions(model_name, stages=["Staging"])
                if versions:
                    return f"models:/{model_name}/Staging"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get production model path: {e}")
            return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Model Registry CLI")
    parser.add_argument("--action", choices=["list", "compare", "promote", "info"], required=True)
    parser.add_argument("--model-name", default="house_price_predictor")
    parser.add_argument("--version1", help="First version for comparison")
    parser.add_argument("--version2", help="Second version for comparison")
    parser.add_argument("--stage", default="Production", help="Model stage")
    parser.add_argument("--target-stage", help="Target stage for promotion")
    parser.add_argument("--mlflow-uri", default="http://localhost:5555")
    
    args = parser.parse_args()
    
    registry = ModelRegistry(args.mlflow_uri)
    
    if args.action == "list":
        versions = registry.list_model_versions(args.model_name)
        print(f"\nModel Versions for {args.model_name}:")
        print("-" * 60)
        for version in versions:
            print(f"Version {version['version']} ({version['stage']})")
            print(f"  Created: {version['creation_date']}")
            if 'validation_r2' in version['metrics']:
                print(f"  R² Score: {version['metrics']['validation_r2']:.4f}")
            if 'validation_mae' in version['metrics']:
                print(f"  MAE: {version['metrics']['validation_mae']:.2f}")
            print()
    
    elif args.action == "compare" and args.version1 and args.version2:
        comparison = registry.compare_models(args.model_name, args.version1, args.version2)
        print(f"\nModel Comparison: {args.model_name}")
        print("-" * 60)
        print(f"Version {args.version1} vs Version {args.version2}")
        
        for metric, data in comparison.get('metrics_comparison', {}).items():
            print(f"{metric}:")
            print(f"  v{args.version1}: {data['version1_value']:.4f}")
            print(f"  v{args.version2}: {data['version2_value']:.4f}")
            print(f"  Better: v{data['better_version']}")
            print()
    
    elif args.action == "info":
        info = registry.get_model_info(args.model_name, args.stage)
        if info:
            print(f"\nModel Info: {args.model_name}")
            print("-" * 60)
            print(f"Version: {info['version']}")
            print(f"Stage: {info['stage']}")
            print(f"Created: {datetime.fromtimestamp(info['creation_timestamp']/1000)}")
            print(f"Metrics: {info['metrics']}")
        else:
            print(f"No model found in {args.stage} stage")
    
    elif args.action == "promote" and args.version1 and args.target_stage:
        success = registry.promote_model(args.model_name, args.version1, args.target_stage)
        if success:
            print(f"✅ Model {args.model_name} v{args.version1} promoted to {args.target_stage}")
        else:
            print(f"❌ Failed to promote model")