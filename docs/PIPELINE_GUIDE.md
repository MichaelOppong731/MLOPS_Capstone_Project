# 🚀 Automated ML Pipeline Guide

This guide covers the automated ML training pipeline implementation for the House Price Predictor project.

## 📋 Overview

The automated pipeline provides:
- **Orchestrated Training**: Automated execution of data processing, feature engineering, and model training
- **Model Validation**: Comprehensive testing with performance, statistical, and robustness checks
- **MLflow Integration**: Enhanced model registry with versioning and lifecycle management
- **CI/CD Automation**: GitHub Actions workflow for continuous integration
- **Quality Gates**: Automated validation thresholds to ensure model quality

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data          │    │   Feature       │    │   Model         │
│   Processing    │───▶│   Engineering   │───▶│   Training      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data          │    │   Feature       │    │   Trained       │
│   Validation    │    │   Validation    │    │   Model         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │   Model         │
                                              │   Validation    │
                                              └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │   MLflow        │
                                              │   Registration  │
                                              └─────────────────┘
```

## 🛠️ Components

### 1. Pipeline Orchestrator (`src/pipeline/orchestrator.py`)

The main orchestrator that coordinates all pipeline steps:

```python
from src.pipeline.orchestrator import MLPipelineOrchestrator

orchestrator = MLPipelineOrchestrator(
    config_path="configs/model_config.yaml",
    mlflow_uri="http://localhost:5555"
)

results = orchestrator.run_full_pipeline()
```

**Features:**
- Sequential execution of all pipeline steps
- Error handling and rollback capabilities
- Comprehensive logging
- MLflow experiment tracking
- Automatic model registration

### 2. Model Validator (`src/pipeline/validator.py`)

Comprehensive model testing framework:

```python
from src.pipeline.validator import ModelValidator

validator = ModelValidator(
    model_path="models/trained/house_price_model.pkl",
    preprocessor_path="models/trained/preprocessor.pkl",
    config=config
)

results = validator.run_all_validations("data/processed/featured_house_data.csv")
```

**Validation Tests:**
- **Performance Tests**: R², MAE, RMSE, MAPE metrics
- **Statistical Tests**: Residual normality, homoscedasticity, autocorrelation
- **Robustness Tests**: Noise tolerance, missing value handling
- **Consistency Tests**: Determinism, monotonicity checks
- **Performance Benchmarks**: Prediction latency and throughput

### 3. Model Registry (`src/pipeline/model_registry.py`)

Enhanced MLflow model registry integration:

```python
from src.pipeline.model_registry import ModelRegistry

registry = ModelRegistry("http://localhost:5555")

# Register new model
version = registry.register_model(
    model_path="models/trained/house_price_model.pkl",
    preprocessor_path="models/trained/preprocessor.pkl",
    model_name="house_price_predictor",
    config=config,
    validation_results=validation_results
)

# Compare models
comparison = registry.compare_models("house_price_predictor", "1", "2")
```

**Features:**
- Automatic model versioning
- Stage-based promotion (None → Staging → Production)
- Model comparison and metrics tracking
- Comprehensive metadata logging
- Automated archiving of old versions

## 🚀 Usage

### Quick Start

1. **Check Setup**:
```bash
python scripts/run_pipeline.py check --check-mlflow
```

2. **Run Complete Pipeline**:
```bash
python scripts/run_pipeline.py run --config configs/model_config.yaml
```

3. **Validate Existing Model**:
```bash
python scripts/run_pipeline.py validate \
  --model models/trained/house_price_model.pkl \
  --preprocessor models/trained/preprocessor.pkl \
  --config configs/model_config.yaml \
  --test-data data/processed/featured_house_data.csv
```

### Advanced Usage

#### Manual Pipeline Steps

```python
from src.pipeline.orchestrator import MLPipelineOrchestrator

orchestrator = MLPipelineOrchestrator("configs/model_config.yaml")

# Run individual steps
orchestrator.run_data_processing()
orchestrator.run_feature_engineering()
orchestrator.run_model_training()

# Validate model
validation_results = orchestrator.validate_model()

# Register in MLflow
if validation_results['validation_passed']:
    orchestrator.register_model_in_mlflow(validation_results)
```

#### Model Registry Operations

```bash
# List all model versions
python src/pipeline/model_registry.py --action list --model-name house_price_predictor

# Compare two versions
python src/pipeline/model_registry.py --action compare --version1 1 --version2 2

# Promote model to production
python src/pipeline/model_registry.py --action promote --version1 2 --target-stage Production

# Get production model info
python src/pipeline/model_registry.py --action info --stage Production
```

## 🔧 Configuration

### Quality Thresholds

The pipeline uses configurable quality thresholds in `src/pipeline/validator.py`:

```python
thresholds = {
    'min_r2_score': 0.85,      # Minimum R² score
    'max_mae': 15000,          # Maximum Mean Absolute Error
    'max_rmse': 20000,         # Maximum Root Mean Square Error
    'max_mape': 0.15,          # Maximum Mean Absolute Percentage Error (15%)
    'min_samples': 100,        # Minimum test samples
    'max_prediction_time_ms': 100  # Maximum prediction time in milliseconds
}
```

### MLflow Configuration

Set up MLflow tracking in your environment:

```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5555 --default-artifact-root ./mlruns

# Or use Docker
cd deployment/mlflow
docker-compose up -d
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

The pipeline includes a comprehensive GitHub Actions workflow (`.github/workflows/ml-pipeline.yml`) that:

1. **Triggers on**:
   - Push to main/develop branches
   - Changes to src/, configs/, or data/ directories
   - Daily schedule (2 AM UTC)
   - Manual workflow dispatch

2. **Pipeline Steps**:
   - Data validation
   - Automated training
   - Model validation
   - API integration testing
   - Docker image building
   - Staging deployment

3. **Quality Gates**:
   - All validation tests must pass
   - Performance benchmarks must meet thresholds
   - API health checks must succeed

### Local Development

For local development and testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Start MLflow
mlflow server --host 0.0.0.0 --port 5555 &

# Run pipeline
python scripts/run_pipeline.py run --config configs/model_config.yaml

# Check results
python scripts/run_pipeline.py validate \
  --model models/trained/house_price_model.pkl \
  --preprocessor models/trained/preprocessor.pkl \
  --config configs/model_config.yaml \
  --test-data data/processed/featured_house_data.csv
```

## 📊 Monitoring and Logging

### Pipeline Logs

All pipeline execution is logged to:
- Console output (INFO level)
- `pipeline.log` file (DEBUG level)
- MLflow experiment runs

### Model Metrics

Key metrics tracked in MLflow:
- **Training Metrics**: Model performance on training data
- **Validation Metrics**: Performance on held-out validation set
- **Statistical Tests**: P-values for normality, homoscedasticity tests
- **Performance Benchmarks**: Prediction latency, throughput
- **Robustness Scores**: Noise tolerance, missing value handling

### Alerts and Notifications

The GitHub Actions workflow provides:
- ✅ Success notifications with model metrics
- ❌ Failure alerts with error details
- 📊 Performance comparison with previous versions

## 🔍 Troubleshooting

### Common Issues

1. **MLflow Connection Error**:
```bash
# Check if MLflow server is running
curl -f http://localhost:5555/health

# Restart MLflow server
mlflow server --host 0.0.0.0 --port 5555 --default-artifact-root ./mlruns
```

2. **Model Validation Failures**:
```bash
# Check validation thresholds in validator.py
# Review model performance metrics
# Ensure sufficient training data quality
```

3. **Pipeline Step Failures**:
```bash
# Check individual step logs
# Verify data file paths and permissions
# Ensure all dependencies are installed
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run pipeline with detailed logs
orchestrator = MLPipelineOrchestrator(config_path, mlflow_uri)
results = orchestrator.run_full_pipeline()
```

## 🎯 Best Practices

1. **Data Quality**: Always validate input data before training
2. **Version Control**: Track all model versions and configurations
3. **Testing**: Run comprehensive validation before deployment
4. **Monitoring**: Set up alerts for model performance degradation
5. **Documentation**: Keep model cards and experiment notes updated
6. **Rollback**: Maintain ability to quickly rollback to previous versions


## 🤝 Contributing

To contribute to the pipeline:
1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation
4. Ensure all quality gates pass
5. Submit pull requests with detailed descriptions

---

For more information, see the main [README.md](../README.md) or contact the development team.