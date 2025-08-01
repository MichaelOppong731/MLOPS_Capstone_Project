# House Price Predictor - MLOps Architecture Diagram

## 🏗️ **Complete MLOps Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          🌐 INTERNET                                                               │
└─────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                  │
┌─────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┐
│                                    👨‍💻 DEVELOPER WORKFLOW                                                          │
│                                                 │                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    │    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   📝 Code       │    │  🔄 GitHub      │    │    │  🤖 GitHub      │    │  📊 Databricks  │                  │
│  │   Changes       │───▶│  Repository     │────┼───▶│  Actions        │───▶│  MLflow         │                  │
│  │                 │    │                 │    │    │  (CI/CD)        │    │  (Tracking)     │                  │
│  └─────────────────┘    └─────────────────┘    │    └─────────────────┘    └─────────────────┘                  │
│                                                 │             │                        │                         │
│                                                 │             ▼                        ▼                         │
│                                                 │    ┌─────────────────┐    ┌─────────────────┐                  │
│                                                 │    │  🐳 Docker      │    │  📈 Model       │                  │
│                                                 │    │  Build & Push   │    │  Training &     │                  │
│                                                 │    │  to ECR         │    │  Validation     │                  │
│                                                 │    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┘
                                                  │
┌─────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┐
│                                      ☁️ AWS CLOUD INFRASTRUCTURE                                                  │
│                                                 │                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                    🏢 VPC (10.0.0.0/16)                                                  │   │
│  │                                                                                                           │   │
│  │  ┌─────────────────────────────────────────┐    ┌─────────────────────────────────────────┐             │   │
│  │  │           📡 PUBLIC SUBNETS              │    │           📡 PUBLIC SUBNETS              │             │   │
│  │  │           (10.0.1.0/24)                 │    │           (10.0.2.0/24)                 │             │   │
│  │  │           eu-west-1a                    │    │           eu-west-1b                    │             │   │
│  │  │                                         │    │                                         │             │   │
│  │  │  ┌─────────────────────────────────┐    │    │  ┌─────────────────────────────────┐    │             │   │
│  │  │  │        🌐 NAT Gateway           │    │    │  │        🌐 NAT Gateway           │    │             │   │
│  │  │  │        (High Availability)      │    │    │  │        (High Availability)      │    │             │   │
│  │  │  └─────────────────────────────────┘    │    │  └─────────────────────────────────┘    │             │   │
│  │  └─────────────────────────────────────────┘    └─────────────────────────────────────────┘             │   │
│  │                           │                                           │                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────────────┐             │   │
│  │  │                            ⚖️ APPLICATION LOAD BALANCER                                   │             │   │
│  │  │                                  (Port 80/443)                                          │             │   │
│  │  │                              🔒 SSL Termination                                          │             │   │
│  │  └─────────────────────────────────────────────────────────────────────────────────────────┘             │   │
│  │                           │                                           │                                   │   │
│  │  ┌─────────────────────────────────────────┐    ┌─────────────────────────────────────────┐             │   │
│  │  │          🔒 PRIVATE SUBNETS              │    │          🔒 PRIVATE SUBNETS              │             │   │
│  │  │          (10.0.3.0/24)                  │    │          (10.0.4.0/24)                  │             │   │
│  │  │          eu-west-1a                     │    │          eu-west-1b                     │             │   │
│  │  │                                         │    │                                         │             │   │
│  │  │  ┌─────────────────────────────────┐    │    │  ┌─────────────────────────────────┐    │             │   │
│  │  │  │     🐳 ECS FARGATE              │    │    │  │     🐳 ECS FARGATE              │    │             │   │
│  │  │  │     🤖 Inference API            │    │    │  │     🎨 Streamlit UI             │    │             │   │
│  │  │  │     Port: 8000                  │    │    │  │     Port: 8501                  │    │             │   │
│  │  │  │     CPU: 512, Memory: 1024      │    │    │  │     CPU: 256, Memory: 512       │    │             │   │
│  │  │  └─────────────────────────────────┘    │    │  └─────────────────────────────────┘    │             │   │
│  │  └─────────────────────────────────────────┘    └─────────────────────────────────────────┘             │   │
│  │                           │                                           │                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────────────────────┐             │   │
│  │  │                          🔍 SERVICE DISCOVERY                                             │             │   │
│  │  │                    house-price-predictor-services                                        │             │   │
│  │  │                                                                                           │             │   │
│  │  │    inference-api.house-price-predictor-services:8000                                     │             │   │
│  │  │    ui.house-price-predictor-services:8501                                                │             │   │
│  │  └─────────────────────────────────────────────────────────────────────────────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                 │                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                  📦 SUPPORTING SERVICES                                                   │   │
│  │                                                                                                           │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐               │   │
│  │  │  🐳 Amazon      │    │  📊 CloudWatch  │    │  🔐 IAM Roles   │    │  🛡️ Security    │               │   │
│  │  │  ECR             │    │  Logs           │    │  & Policies     │    │  Groups         │               │   │
│  │  │                 │    │                 │    │                 │    │                 │               │   │
│  │  │  house-price-   │    │  /ecs/          │    │  ECS Task       │    │  ALB-SG         │               │   │
│  │  │  api:latest     │    │  inference-api  │    │  Execution      │    │  ECS-Tasks-SG   │               │   │
│  │  │                 │    │                 │    │  Role           │    │                 │               │   │
│  │  │  house-price-   │    │  /ecs/ui        │    │                 │    │                 │               │   │
│  │  │  ui:latest      │    │                 │    │                 │    │                 │               │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘               │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┘
                                                  │
┌─────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┐
│                                      👥 END USERS                                                                  │
│                                                 │                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    │    ┌─────────────────┐    ┌─────────────────┐                  │
│  │  🌐 Web Browser │    │  📱 Mobile App  │    │    │  🔗 API Client  │    │  📊 Analytics   │                  │
│  │                 │───▶│                 │────┼───▶│                 │───▶│  Dashboard      │                  │
│  │  Streamlit UI   │    │  (Future)       │    │    │  Direct API     │    │  (Future)       │                  │
│  └─────────────────┘    └─────────────────┘    │    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────┘
                                                  │
                                          🏠 House Price Predictions
```

## 🔄 **Data Flow Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        📊 ML PIPELINE DATA FLOW                                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

1️⃣ DATA INGESTION & PROCESSING
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  📄 Raw Data    │───▶│  🧹 Data        │───▶│  🔧 Feature     │───▶│  📊 Processed   │
│  house_data.csv │    │  Cleaning       │    │  Engineering    │    │  Features       │
│                 │    │                 │    │                 │    │                 │
│  • sqft         │    │  • Handle nulls │    │  • house_age    │    │  • 7 features   │
│  • bedrooms     │    │  • Data types   │    │  • bed_bath_    │    │  • Scaled data  │
│  • bathrooms    │    │  • Validation   │    │    ratio        │    │  • One-hot enc  │
│  • location     │    │                 │    │  • Remove       │    │                 │
│  • condition    │    │                 │    │    leakage      │    │                 │
│  • year_built   │    │                 │    │                 │    │                 │
│  • price        │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘

2️⃣ MODEL TRAINING & VALIDATION
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  🤖 Model       │───▶│  📈 Training    │───▶│  ✅ Validation  │───▶│  📦 Model       │
│  Selection      │    │  Process        │    │  & Testing      │    │  Artifacts      │
│                 │    │                 │    │                 │    │                 │
│  • Linear       │    │  • Train/Test   │    │  • R² ≥ 0.60    │    │  • model.pkl    │
│    Regression   │    │    Split (80/20)│    │  • MAE ≤ 25K    │    │  • preprocessor │
│  • Random       │    │  • Cross        │    │  • RMSE ≤ 30K   │    │    .pkl         │
│    Forest       │    │    Validation   │    │  • Quality      │    │  • config.yaml  │
│  • XGBoost      │    │  • Hyperparams  │    │    Gates        │    │                 │
│  • Gradient     │    │                 │    │                 │    │                 │
│    Boosting     │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘

3️⃣ MODEL DEPLOYMENT & SERVING
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  🐳 Docker      │───▶│  📦 ECR         │───▶│  🚀 ECS         │───▶│  🌐 Live        │
│  Containerization│    │  Registry       │    │  Deployment     │    │  Predictions    │
│                 │    │                 │    │                 │    │                 │
│  • API Image    │    │  • house-price- │    │  • Auto-scaling │    │  • REST API     │
│  • UI Image     │    │    api:latest   │    │  • Health       │    │  • Web UI       │
│  • Model        │    │  • house-price- │    │    Checks       │    │  • Real-time    │
│    Artifacts    │    │    ui:latest    │    │  • Rolling      │    │    Inference    │
│  • Dependencies │    │                 │    │    Updates      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘

4️⃣ MONITORING & FEEDBACK
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  📊 MLflow      │───▶│  📈 CloudWatch  │───▶│  🔔 Alerts      │───▶│  🔄 Continuous  │
│  Tracking       │    │  Monitoring     │    │  & Notifications│    │  Improvement    │
│                 │    │                 │    │                 │    │                 │
│  • Experiments  │    │  • API Metrics  │    │  • Performance  │    │  • Model        │
│  • Model        │    │  • Error Rates  │    │    Degradation  │    │    Retraining   │
│    Versions     │    │  • Latency      │    │  • System       │    │  • Feature      │
│  • Parameters   │    │  • Throughput   │    │    Health       │    │    Updates      │
│  • Metrics      │    │                 │    │                 │    │  • A/B Testing  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 **Security Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        🛡️ SECURITY LAYERS                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🌐 NETWORK SECURITY
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  Internet ──▶ ALB (Public) ──▶ Private Subnets ──▶ NAT Gateway ──▶ Internet                                      │
│                │                        │                                                                          │
│                ▼                        ▼                                                                          │
│         🔒 SSL/TLS              🔒 No Direct Access                                                                │
│         Certificate             to Private Resources                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🛡️ SECURITY GROUPS (Firewall Rules)
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ALB Security Group:                    │  ECS Tasks Security Group:                                              │
│  ├─ Inbound: HTTP (80) from 0.0.0.0/0  │  ├─ Inbound: 8501 from ALB-SG only                                     │
│  ├─ Inbound: HTTPS (443) from 0.0.0.0/0│  ├─ Inbound: 8000 from ECS-Tasks-SG (service discovery)               │
│  └─ Outbound: All traffic              │  ├─ Inbound: All from VPC CIDR (internal communication)                │
│                                         │  └─ Outbound: All traffic (for ECR pulls, updates)                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🔐 IAM SECURITY (Identity & Access Management)
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ECS Task Execution Role:               │  GitHub Actions Role:                                                   │
│  ├─ ECR: Pull images                    │  ├─ ECR: Push/pull images                                               │
│  ├─ CloudWatch: Create logs             │  ├─ ECS: Update services                                                │
│  ├─ Secrets Manager: Access secrets     │  └─ CloudWatch: Read metrics                                            │
│  └─ Principle of Least Privilege        │                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 📈 **Scalability & Performance Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ⚡ PERFORMANCE & SCALING                                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🔄 AUTO-SCALING STRATEGY
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                     │
│  Load Increase ──▶ CloudWatch Metrics ──▶ ECS Auto Scaling ──▶ New Tasks Launched                                │
│                                    │                                    │                                          │
│                                    ▼                                    ▼                                          │
│                            • CPU > 70%                          • FARGATE_SPOT                                     │
│                            • Memory > 80%                       • Multi-AZ Distribution                            │
│                            • Request Count                      • Health Checks                                    │
│                                                                                                                     │
│  Load Decrease ──▶ Scale Down ──▶ Cost Optimization ──▶ Maintain Min Capacity                                     │
│                                                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

📊 PERFORMANCE METRICS
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  API Performance:                       │  Infrastructure Performance:                                            │
│  ├─ Response Time: < 200ms              │  ├─ CPU Utilization: < 70%                                              │
│  ├─ Throughput: 1000+ req/min           │  ├─ Memory Usage: < 80%                                                 │
│  ├─ Error Rate: < 1%                    │  ├─ Network Latency: < 50ms                                             │
│  └─ Model Inference: < 100ms            │  └─ Availability: 99.9%                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 **CI/CD Pipeline Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      🚀 DEPLOYMENT PIPELINE                                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

📝 CODE COMMIT
    │
    ▼
🔍 DATA VALIDATION ──▶ ❌ FAIL ──▶ 🛑 STOP PIPELINE
    │
    ✅ PASS
    │
    ▼
🤖 ML PIPELINE
    ├─ Data Processing
    ├─ Feature Engineering  
    ├─ Model Training
    ├─ Model Validation ──▶ ❌ FAIL ──▶ 🛑 STOP PIPELINE
    └─ MLflow Registration
    │
    ✅ PASS
    │
    ▼
🐳 BUILD & PUSH
    ├─ Build API Docker Image
    ├─ Build UI Docker Image
    ├─ Push to ECR
    └─ Tag with Git SHA
    │
    ✅ SUCCESS
    │
    ▼
🚀 DEPLOY TO ECS
    ├─ Update API Service
    ├─ Update UI Service
    ├─ Wait for Stability
    └─ Health Checks
    │
    ✅ SUCCESS
    │
    ▼
📊 MONITORING & ALERTS
    ├─ CloudWatch Metrics
    ├─ Application Logs
    └─ Performance Monitoring
```

---

## 📋 **Architecture Summary**

### **🎯 Key Components:**
- **VPC**: Isolated network environment with public/private subnets
- **ECS Fargate**: Serverless container platform for ML services
- **ALB**: Load balancer for high availability and SSL termination
- **ECR**: Private Docker registry for container images
- **Service Discovery**: Internal DNS for service communication
- **NAT Gateways**: Secure outbound internet access for private subnets

### **🔄 MLOps Pipeline:**
- **Automated Training**: Triggered by code changes
- **Model Validation**: Quality gates before deployment
- **Containerization**: Docker images with trained models
- **Zero-Downtime Deployment**: Rolling updates via ECS
- **Monitoring**: CloudWatch + MLflow tracking

### **🛡️ Security Features:**
- **Private Subnets**: Application isolation
- **Security Groups**: Network-level firewall
- **IAM Roles**: Least privilege access
- **SSL/TLS**: Encrypted communication

### **💰 Cost Optimization:**
- **FARGATE_SPOT**: 30% cost savings on compute
- **Multi-AZ NAT**: High availability with redundancy
- **Auto-scaling**: Pay only for what you use
- **Efficient Resource Allocation**: Right-sized containers

This architecture provides enterprise-grade security, scalability, and reliability for your House Price Predictor MLOps system! 🏗️✨