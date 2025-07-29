"""
Model Validation Module
Comprehensive model testing and quality assurance
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
from sklearn.metrics import (
    mean_absolute_error, 
    mean_squared_error, 
    r2_score,
    mean_absolute_percentage_error
)
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class ModelValidator:
    """Comprehensive model validation and testing"""
    
    def __init__(self, model_path: str, preprocessor_path: str, config: Dict[str, Any]):
        self.model_path = Path(model_path)
        self.preprocessor_path = Path(preprocessor_path)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load model and preprocessor
        self.model = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)
        
        # Quality thresholds
        self.thresholds = {
            'min_r2_score': 0.85,
            'max_mae': 15000,
            'max_rmse': 20000,
            'max_mape': 0.15,  # 15% MAPE
            'min_samples': 100,
            'max_prediction_time_ms': 100
        }
    
    def performance_tests(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        self.logger.info("Running performance tests...")
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        
        # Additional metrics
        residuals = y_test - y_pred
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        
        results = {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2_score': r2,
            'mape': mape,
            'mean_residual': mean_residual,
            'std_residual': std_residual,
            'n_samples': len(y_test)
        }
        
        # Performance checks
        performance_checks = {
            'r2_check': r2 >= self.thresholds['min_r2_score'],
            'mae_check': mae <= self.thresholds['max_mae'],
            'rmse_check': rmse <= self.thresholds['max_rmse'],
            'mape_check': mape <= self.thresholds['max_mape'],
            'sample_size_check': len(y_test) >= self.thresholds['min_samples']
        }
        
        results['performance_checks'] = performance_checks
        results['all_performance_checks_passed'] = all(performance_checks.values())
        
        return results
    
    def statistical_tests(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Run statistical validation tests"""
        self.logger.info("Running statistical tests...")
        
        y_pred = self.model.predict(X_test)
        residuals = y_test - y_pred
        
        results = {}
        
        # Normality test for residuals (Shapiro-Wilk)
        if len(residuals) <= 5000:  # Shapiro-Wilk works best for smaller samples
            shapiro_stat, shapiro_p = stats.shapiro(residuals)
            results['residuals_normality'] = {
                'test': 'shapiro_wilk',
                'statistic': shapiro_stat,
                'p_value': shapiro_p,
                'is_normal': shapiro_p > 0.05
            }
        
        # Homoscedasticity test (Breusch-Pagan approximation)
        # Check if variance of residuals is constant across prediction range
        pred_sorted_idx = np.argsort(y_pred)
        n_groups = 3
        group_size = len(pred_sorted_idx) // n_groups
        
        group_variances = []
        for i in range(n_groups):
            start_idx = i * group_size
            end_idx = (i + 1) * group_size if i < n_groups - 1 else len(pred_sorted_idx)
            group_residuals = residuals.iloc[pred_sorted_idx[start_idx:end_idx]]
            group_variances.append(np.var(group_residuals))
        
        # Levene's test for equal variances
        levene_stat, levene_p = stats.levene(*[
            residuals.iloc[pred_sorted_idx[i*group_size:(i+1)*group_size if i < n_groups-1 else len(pred_sorted_idx)]]
            for i in range(n_groups)
        ])
        
        results['homoscedasticity'] = {
            'test': 'levene',
            'statistic': levene_stat,
            'p_value': levene_p,
            'is_homoscedastic': levene_p > 0.05,
            'group_variances': group_variances
        }
        
        # Autocorrelation test (Durbin-Watson)
        dw_stat = self._durbin_watson(residuals)
        results['autocorrelation'] = {
            'durbin_watson_stat': dw_stat,
            'no_autocorrelation': 1.5 < dw_stat < 2.5  # Rule of thumb
        }
        
        return results
    
    def _durbin_watson(self, residuals: pd.Series) -> float:
        """Calculate Durbin-Watson statistic"""
        diff = residuals.diff().dropna()
        return (diff ** 2).sum() / (residuals ** 2).sum()
    
    def robustness_tests(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Test model robustness with various perturbations"""
        self.logger.info("Running robustness tests...")
        
        results = {}
        baseline_pred = self.model.predict(X_test)
        baseline_mae = mean_absolute_error(y_test, baseline_pred)
        
        # Test 1: Small random noise
        noise_levels = [0.01, 0.05, 0.1]  # 1%, 5%, 10% noise
        noise_results = {}
        
        for noise_level in noise_levels:
            X_noisy = X_test.copy()
            # Add Gaussian noise to numerical columns
            numerical_cols = X_test.select_dtypes(include=[np.number]).columns
            for col in numerical_cols:
                noise = np.random.normal(0, X_test[col].std() * noise_level, len(X_test))
                X_noisy[col] = X_test[col] + noise
            
            noisy_pred = self.model.predict(X_noisy)
            noisy_mae = mean_absolute_error(y_test, noisy_pred)
            
            noise_results[f'noise_{int(noise_level*100)}pct'] = {
                'mae': noisy_mae,
                'mae_increase': (noisy_mae - baseline_mae) / baseline_mae,
                'robust': (noisy_mae - baseline_mae) / baseline_mae < 0.1  # Less than 10% increase
            }
        
        results['noise_robustness'] = noise_results
        
        # Test 2: Missing value handling (if applicable)
        missing_results = {}
        for missing_pct in [0.05, 0.1]:  # 5%, 10% missing
            X_missing = X_test.copy()
            n_missing = int(len(X_test) * missing_pct)
            
            # Randomly set some values to NaN in numerical columns
            numerical_cols = X_test.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) > 0:
                for _ in range(n_missing):
                    row_idx = np.random.randint(0, len(X_test))
                    col_idx = np.random.choice(numerical_cols)
                    X_missing.loc[X_missing.index[row_idx], col_idx] = np.nan
                
                # Fill NaN with median (simple strategy)
                X_missing = X_missing.fillna(X_missing.median())
                
                missing_pred = self.model.predict(X_missing)
                missing_mae = mean_absolute_error(y_test, missing_pred)
                
                missing_results[f'missing_{int(missing_pct*100)}pct'] = {
                    'mae': missing_mae,
                    'mae_increase': (missing_mae - baseline_mae) / baseline_mae,
                    'robust': (missing_mae - baseline_mae) / baseline_mae < 0.15
                }
        
        results['missing_value_robustness'] = missing_results
        
        return results
    
    def prediction_consistency_tests(self, X_test: pd.DataFrame) -> Dict[str, Any]:
        """Test prediction consistency and determinism"""
        self.logger.info("Running prediction consistency tests...")
        
        results = {}
        
        # Test 1: Determinism - same input should give same output
        pred1 = self.model.predict(X_test)
        pred2 = self.model.predict(X_test)
        
        results['determinism'] = {
            'identical_predictions': np.array_equal(pred1, pred2),
            'max_difference': np.max(np.abs(pred1 - pred2)) if not np.array_equal(pred1, pred2) else 0.0
        }
        
        # Test 2: Monotonicity tests (for specific features if applicable)
        # This is domain-specific - for house prices, larger houses should generally cost more
        monotonicity_results = {}
        
        # Test if increasing square footage increases price (if sqft feature exists)
        if 'sqft' in X_test.columns:
            test_sample = X_test.iloc[0:1].copy()
            sqft_values = np.linspace(X_test['sqft'].min(), X_test['sqft'].max(), 10)
            predictions = []
            
            for sqft in sqft_values:
                test_sample['sqft'] = sqft
                pred = self.model.predict(test_sample)[0]
                predictions.append(pred)
            
            # Check if predictions generally increase with sqft
            increases = sum(1 for i in range(1, len(predictions)) if predictions[i] > predictions[i-1])
            monotonicity_results['sqft_monotonicity'] = {
                'increases': increases,
                'total_comparisons': len(predictions) - 1,
                'monotonicity_ratio': increases / (len(predictions) - 1),
                'is_monotonic': increases / (len(predictions) - 1) > 0.7  # 70% of increases
            }
        
        results['monotonicity'] = monotonicity_results
        
        return results
    
    def performance_benchmarks(self, X_test: pd.DataFrame) -> Dict[str, Any]:
        """Test model performance benchmarks"""
        self.logger.info("Running performance benchmarks...")
        
        import time
        
        results = {}
        
        # Single prediction time
        single_times = []
        for _ in range(100):
            start_time = time.time()
            _ = self.model.predict(X_test.iloc[0:1])
            end_time = time.time()
            single_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        results['single_prediction'] = {
            'mean_time_ms': np.mean(single_times),
            'median_time_ms': np.median(single_times),
            'p95_time_ms': np.percentile(single_times, 95),
            'meets_threshold': np.mean(single_times) <= self.thresholds['max_prediction_time_ms']
        }
        
        # Batch prediction time
        batch_sizes = [10, 100, 1000]
        batch_results = {}
        
        for batch_size in batch_sizes:
            if len(X_test) >= batch_size:
                batch_data = X_test.iloc[:batch_size]
                
                start_time = time.time()
                _ = self.model.predict(batch_data)
                end_time = time.time()
                
                total_time_ms = (end_time - start_time) * 1000
                per_sample_time_ms = total_time_ms / batch_size
                
                batch_results[f'batch_{batch_size}'] = {
                    'total_time_ms': total_time_ms,
                    'per_sample_time_ms': per_sample_time_ms,
                    'throughput_samples_per_sec': batch_size / (total_time_ms / 1000)
                }
        
        results['batch_prediction'] = batch_results
        
        return results
    
    def run_all_validations(self, test_data_path: str) -> Dict[str, Any]:
        """Run all validation tests"""
        self.logger.info("Starting comprehensive model validation...")
        
        # Load test data
        data = pd.read_csv(test_data_path)
        
        # Prepare test set (last 20% of data)
        test_size = int(len(data) * 0.2)
        test_data = data.tail(test_size)
        
        target_col = self.config.get('model', {}).get('target_variable', 'price')
        feature_cols = [col for col in test_data.columns if col != target_col]
        
        X_test = test_data[feature_cols]
        y_test = test_data[target_col]
        
        # Run all validation tests
        validation_results = {
            'test_data_info': {
                'n_samples': len(test_data),
                'n_features': len(feature_cols),
                'target_variable': target_col
            },
            'performance': self.performance_tests(X_test, y_test),
            'statistical': self.statistical_tests(X_test, y_test),
            'robustness': self.robustness_tests(X_test, y_test),
            'consistency': self.prediction_consistency_tests(X_test),
            'benchmarks': self.performance_benchmarks(X_test)
        }
        
        # Overall validation status
        performance_passed = validation_results['performance']['all_performance_checks_passed']
        determinism_passed = validation_results['consistency']['determinism']['identical_predictions']
        speed_passed = validation_results['benchmarks']['single_prediction']['meets_threshold']
        
        validation_results['overall_validation'] = {
            'passed': performance_passed and determinism_passed and speed_passed,
            'performance_passed': performance_passed,
            'determinism_passed': determinism_passed,
            'speed_passed': speed_passed
        }
        
        self.logger.info(f"Validation completed. Overall passed: {validation_results['overall_validation']['passed']}")
        
        return validation_results


if __name__ == "__main__":
    import argparse
    import yaml
    
    parser = argparse.ArgumentParser(description="Validate trained model")
    parser.add_argument("--model", required=True, help="Path to trained model")
    parser.add_argument("--preprocessor", required=True, help="Path to preprocessor")
    parser.add_argument("--config", required=True, help="Path to model config")
    parser.add_argument("--test-data", required=True, help="Path to test data")
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Run validation
    validator = ModelValidator(args.model, args.preprocessor, config)
    results = validator.run_all_validations(args.test_data)
    
    print("\n" + "="*60)
    print("MODEL VALIDATION RESULTS")
    print("="*60)
    print(f"Overall Validation: {'PASSED' if results['overall_validation']['passed'] else 'FAILED'}")
    print(f"Performance Tests: {'PASSED' if results['overall_validation']['performance_passed'] else 'FAILED'}")
    print(f"Determinism Tests: {'PASSED' if results['overall_validation']['determinism_passed'] else 'FAILED'}")
    print(f"Speed Tests: {'PASSED' if results['overall_validation']['speed_passed'] else 'FAILED'}")
    print("="*60)