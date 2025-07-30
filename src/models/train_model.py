import argparse
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import yaml
import logging
from mlflow.tracking import MlflowClient
import platform
import sklearn

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------
# Argument parser
# -----------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Train and register final model from config.")
    parser.add_argument("--config", type=str, required=True, help="Path to model_config.yaml")
    parser.add_argument("--data", type=str, required=True, help="Path to processed CSV dataset")
    parser.add_argument("--models-dir", type=str, required=True, help="Directory to save trained model")
    parser.add_argument("--mlflow-tracking-uri", type=str, default=None, help="MLflow tracking URI")
    return parser.parse_args()

# -----------------------------
# Load model from config
# -----------------------------
def get_model_instance(name, params):
    model_map = {
        'LinearRegression': LinearRegression,
        'RandomForest': RandomForestRegressor,
        'GradientBoosting': GradientBoostingRegressor,
        'XGBoost': xgb.XGBRegressor
    }
    if name not in model_map:
        raise ValueError(f"Unsupported model: {name}")
    return model_map[name](**params)

# -----------------------------
# Main logic
# -----------------------------
def main(args):
    try:
        logger.info("🚀 Starting model training...")
        
        # Load config
        logger.info(f"📋 Loading config from: {args.config}")
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        model_cfg = config['model']
        logger.info(f"📋 Model config loaded: {model_cfg['best_model']}")

        if args.mlflow_tracking_uri:
            logger.info(f"🔧 Setting up MLflow with URI: {args.mlflow_tracking_uri}")
            mlflow.set_tracking_uri(args.mlflow_tracking_uri)
            
            # Use proper Databricks experiment path
            if args.mlflow_tracking_uri == "databricks":
                experiment_name = "/Users/michaeloppong731@gmail.com/house_price_pipeline"
            else:
                experiment_name = model_cfg['name']
            
            try:
                mlflow.set_experiment(experiment_name)
                logger.info(f"✅ Using MLflow experiment: {experiment_name}")
            except Exception as e:
                logger.warning(f"⚠️ MLflow experiment setup failed: {e}")
                # Continue without MLflow if it fails
                pass

        # Load data
        logger.info(f"📊 Loading data from: {args.data}")
        data = pd.read_csv(args.data)
        logger.info(f"📊 Data loaded: {len(data)} rows, {len(data.columns)} columns")
        
        target = model_cfg['target_variable']
        logger.info(f"🎯 Target variable: {target}")

        # Use all features except the target variable
        X = data.drop(columns=[target])
        y = data[target]
        logger.info(f"📊 Features: {len(X.columns)} columns")
        logger.info(f"📊 Target range: {y.min():.2f} to {y.max():.2f}")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        logger.info(f"📊 Train/test split: {len(X_train)} train, {len(X_test)} test samples")
        
        # Get model
        logger.info(f"🤖 Creating model instance: {model_cfg['best_model']}")
        model = get_model_instance(model_cfg['best_model'], model_cfg['parameters'])
        logger.info(f"✅ Model instance created successfully")

        # Start MLflow run
        logger.info("🏃 Starting MLflow run...")
        with mlflow.start_run(run_name="final_training"):
            logger.info(f"🎯 Training model: {model_cfg['best_model']}")
            model.fit(X_train, y_train)
            logger.info("✅ Model training completed")
            
            y_pred = model.predict(X_test)
            logger.info("✅ Model predictions generated")

            mae = float(mean_absolute_error(y_test, y_pred))
            r2 = float(r2_score(y_test, y_pred))
            logger.info(f"📊 Model performance - MAE: {mae:.2f}, R²: {r2:.4f}")

            # Log params and metrics
            logger.info("📈 Logging parameters and metrics to MLflow...")
            mlflow.log_params(model_cfg['parameters'])
            mlflow.log_metrics({'mae': mae, 'r2': r2})
            logger.info("✅ Parameters and metrics logged")

            # Log and register model
            logger.info("🤖 Logging model to MLflow...")
            mlflow.sklearn.log_model(model, "tuned_model")
            logger.info("✅ Model logged to MLflow")
            
            model_name = model_cfg['name']
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/tuned_model"
            logger.info(f"📦 Model URI: {model_uri}")

            logger.info("📋 Registering model to MLflow Model Registry...")
            client = MlflowClient()
            try:
                client.create_registered_model(model_name)
                logger.info(f"✅ Created registered model: {model_name}")
            except mlflow.exceptions.RestException as e:
                logger.info(f"📋 Registered model already exists: {model_name}")

            try:
                model_version = client.create_model_version(
                    name=model_name,
                    source=model_uri,
                    run_id=mlflow.active_run().info.run_id
                )
                logger.info(f"✅ Created model version: {model_version.version}")

                # Transition model to "Staging"
                client.transition_model_version_stage(
                    name=model_name,
                    version=model_version.version,
                    stage="Staging"
                )
                logger.info(f"✅ Transitioned model to Staging")

                # Add a human-readable description
                description = (
                    f"Model for predicting house prices.\n"
                    f"Algorithm: {model_cfg['best_model']}\n"
                    f"Hyperparameters: {model_cfg['parameters']}\n"
                    f"Features used: All features in the dataset except the target variable\n"
                    f"Target variable: {target}\n"
                    f"Trained on dataset: {args.data}\n"
                    f"Model saved at: {args.models_dir}/{model_name}.pkl\n"
                    f"Performance metrics:\n"
                    f"  - MAE: {mae:.2f}\n"
                    f"  - R²: {r2:.4f}"
                )
                client.update_registered_model(name=model_name, description=description)
                logger.info("✅ Updated model description")

                # Add tags for better organization
                client.set_registered_model_tag(model_name, "algorithm", model_cfg['best_model'])
                client.set_registered_model_tag(model_name, "hyperparameters", str(model_cfg['parameters']))
                client.set_registered_model_tag(model_name, "features", "All features except target variable")
                client.set_registered_model_tag(model_name, "target_variable", target)
                client.set_registered_model_tag(model_name, "training_dataset", args.data)
                client.set_registered_model_tag(model_name, "model_path", f"{args.models_dir}/{model_name}.pkl")
                logger.info("✅ Added model tags")

                # Add dependency tags
                deps = {
                    "python_version": platform.python_version(),
                    "scikit_learn_version": sklearn.__version__,
                    "xgboost_version": xgb.__version__,
                    "pandas_version": pd.__version__,
                    "numpy_version": np.__version__,
                }
                for k, v in deps.items():
                    client.set_registered_model_tag(model_name, k, v)
                logger.info("✅ Added dependency tags")
                
            except Exception as e:
                logger.error(f"❌ Error in model registry operations: {e}")
                # Continue with local model saving even if registry fails
                pass

            # Save model locally
            logger.info("💾 Saving model locally...")
            import os
            os.makedirs(args.models_dir, exist_ok=True)
            save_path = f"{args.models_dir}/{model_name}.pkl"
            joblib.dump(model, save_path)
            logger.info(f"✅ Saved trained model to: {save_path}")
            logger.info(f"🎉 Training completed! Final MAE: {mae:.2f}, R²: {r2:.4f}")
            
    except Exception as e:
        logger.error(f"❌ Error in model training: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    args = parse_args()
    main(args)
