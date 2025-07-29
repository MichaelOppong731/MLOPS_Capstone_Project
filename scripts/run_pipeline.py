#!/usr/bin/env python3
"""
ML Pipeline CLI Tool
Simple command-line interface for running the ML pipeline
"""

import sys
import argparse
from pathlib import Path
import yaml
import json
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from pipeline.orchestrator import MLPipelineOrchestrator
from pipeline.validator import ModelValidator

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_pipeline(args):
    """Run the complete ML pipeline"""
    print("🚀 Starting ML Pipeline...")
    print(f"Config: {args.config}")
    print(f"MLflow URI: {args.mlflow_uri}")
    print("-" * 50)
    
    orchestrator = MLPipelineOrchestrator(args.config, args.mlflow_uri)
    results = orchestrator.run_full_pipeline()
    
    # Print results
    print("\n" + "="*60)
    print("🎯 PIPELINE EXECUTION SUMMARY")
    print("="*60)
    print(f"Overall Success: {'✅ YES' if results['overall_success'] else '❌ NO'}")
    print(f"Start Time: {results['start_time']}")
    if 'end_time' in results:
        print(f"End Time: {results['end_time']}")
    
    print(f"\n📋 Steps Completed ({len(results['steps_completed'])}):")
    for step in results['steps_completed']:
        print(f"  ✅ {step}")
    
    if results['steps_failed']:
        print(f"\n❌ Steps Failed ({len(results['steps_failed'])}):")
        for step in results['steps_failed']:
            print(f"  ❌ {step}")
    
    if 'validation_results' in results:
        val_results = results['validation_results']
        print(f"\n🔍 Model Validation:")
        print(f"  R² Score: {val_results.get('r2_score', 'N/A'):.4f}")
        print(f"  MAE: {val_results.get('mae', 'N/A'):.2f}")
        print(f"  RMSE: {val_results.get('rmse', 'N/A'):.2f}")
        print(f"  Validation Passed: {'✅ YES' if val_results.get('validation_passed') else '❌ NO'}")
    
    if 'model_version' in results:
        print(f"\n📦 Model Registration:")
        print(f"  MLflow Version: {results['model_version']}")
        print(f"  Status: Registered in Staging")
    
    print("="*60)
    
    # Save results to file
    results_file = f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"📄 Results saved to: {results_file}")
    
    return 0 if results['overall_success'] else 1

def validate_model(args):
    """Run comprehensive model validation"""
    print("🔍 Starting Model Validation...")
    print(f"Model: {args.model}")
    print(f"Preprocessor: {args.preprocessor}")
    print(f"Config: {args.config}")
    print("-" * 50)
    
    config = load_config(args.config)
    validator = ModelValidator(args.model, args.preprocessor, config)
    results = validator.run_all_validations(args.test_data)
    
    # Print validation summary
    print("\n" + "="*60)
    print("🎯 MODEL VALIDATION SUMMARY")
    print("="*60)
    
    overall = results['overall_validation']
    print(f"Overall Validation: {'✅ PASSED' if overall['passed'] else '❌ FAILED'}")
    print(f"Performance Tests: {'✅ PASSED' if overall['performance_passed'] else '❌ FAILED'}")
    print(f"Determinism Tests: {'✅ PASSED' if overall['determinism_passed'] else '❌ FAILED'}")
    print(f"Speed Tests: {'✅ PASSED' if overall['speed_passed'] else '❌ FAILED'}")
    
    # Performance metrics
    perf = results['performance']
    print(f"\n📊 Performance Metrics:")
    print(f"  R² Score: {perf['r2_score']:.4f}")
    print(f"  MAE: {perf['mae']:.2f}")
    print(f"  RMSE: {perf['rmse']:.2f}")
    print(f"  MAPE: {perf['mape']:.4f}")
    print(f"  Test Samples: {perf['n_samples']}")
    
    # Speed benchmarks
    bench = results['benchmarks']
    print(f"\n⚡ Performance Benchmarks:")
    print(f"  Single Prediction: {bench['single_prediction']['mean_time_ms']:.2f}ms")
    print(f"  P95 Latency: {bench['single_prediction']['p95_time_ms']:.2f}ms")
    
    print("="*60)
    
    # Save validation results
    validation_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(validation_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"📄 Validation results saved to: {validation_file}")
    
    return 0 if overall['passed'] else 1

def check_setup(args):
    """Check if the environment is properly set up"""
    print("🔧 Checking ML Pipeline Setup...")
    print("-" * 50)
    
    issues = []
    
    # Check required directories
    required_dirs = [
        "data/raw",
        "data/processed", 
        "models/trained",
        "configs",
        "src/data",
        "src/features",
        "src/models",
        "src/pipeline"
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            issues.append(f"Missing directory: {dir_path}")
        else:
            print(f"✅ {dir_path}")
    
    # Check required files
    required_files = [
        "data/raw/house_data.csv",
        "configs/model_config.yaml",
        "src/data/run_processing.py",
        "src/features/engineer.py",
        "src/models/train_model.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Missing file: {file_path}")
        else:
            print(f"✅ {file_path}")
    
    # Check Python packages
    try:
        import mlflow
        import sklearn
        import pandas
        import numpy
        print("✅ Required Python packages installed")
    except ImportError as e:
        issues.append(f"Missing Python package: {e}")
    
    # Check MLflow server
    if args.check_mlflow:
        try:
            import requests
            response = requests.get(f"{args.mlflow_uri}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ MLflow server accessible at {args.mlflow_uri}")
            else:
                issues.append(f"MLflow server not responding at {args.mlflow_uri}")
        except Exception as e:
            issues.append(f"Cannot connect to MLflow server: {e}")
    
    print("\n" + "="*50)
    if issues:
        print("❌ Setup Issues Found:")
        for issue in issues:
            print(f"  • {issue}")
        print("\n💡 Fix these issues before running the pipeline")
        return 1
    else:
        print("✅ All checks passed! Ready to run ML pipeline")
        return 0

def main():
    parser = argparse.ArgumentParser(
        description="ML Pipeline CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python scripts/run_pipeline.py run --config configs/model_config.yaml
  
  # Validate existing model
  python scripts/run_pipeline.py validate \\
    --model models/trained/house_price_model.pkl \\
    --preprocessor models/trained/preprocessor.pkl \\
    --config configs/model_config.yaml \\
    --test-data data/processed/featured_house_data.csv
  
  # Check setup
  python scripts/run_pipeline.py check --check-mlflow
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run pipeline command
    run_parser = subparsers.add_parser('run', help='Run the complete ML pipeline')
    run_parser.add_argument('--config', required=True, help='Path to model config YAML')
    run_parser.add_argument('--mlflow-uri', default='http://localhost:5555', help='MLflow tracking URI')
    
    # Validate model command
    validate_parser = subparsers.add_parser('validate', help='Validate trained model')
    validate_parser.add_argument('--model', required=True, help='Path to trained model')
    validate_parser.add_argument('--preprocessor', required=True, help='Path to preprocessor')
    validate_parser.add_argument('--config', required=True, help='Path to model config')
    validate_parser.add_argument('--test-data', required=True, help='Path to test data')
    
    # Check setup command
    check_parser = subparsers.add_parser('check', help='Check pipeline setup')
    check_parser.add_argument('--check-mlflow', action='store_true', help='Check MLflow server connectivity')
    check_parser.add_argument('--mlflow-uri', default='http://localhost:5555', help='MLflow tracking URI')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'run':
        return run_pipeline(args)
    elif args.command == 'validate':
        return validate_model(args)
    elif args.command == 'check':
        return check_setup(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())