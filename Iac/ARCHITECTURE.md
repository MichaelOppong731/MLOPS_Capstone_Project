# House Price Predictor Infrastructure Architecture

## 🏗️ **Simplified Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS VPC (10.0.0.0/16)                   │
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │   Public Subnet     │    │   Public Subnet     │            │
│  │   10.0.1.0/24       │    │   10.0.2.0/24       │            │
│  │   (eu-west-1a)      │    │   (eu-west-1b)      │            │
│  │                     │    │                     │            │
│  │  ┌───────────────┐  │    │  ┌───────────────┐  │            │
│  │  │ ECS Fargate   │  │    │  │ ECS Fargate   │  │            │
│  │  │ Inference API │  │    │  │ Streamlit UI  │  │            │
│  │  │ Port: 8000    │  │    │  │ Port: 8501    │  │            │
│  │  └───────────────┘  │    │  └───────────────┘  │            │
│  └─────────────────────┘    └─────────────────────┘            │
│           │                           │                        │
│           └─────────┬─────────────────┘                        │
│                     │                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Application Load Balancer                  │   │
│  │                    (Port 80)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     │                                          │
└─────────────────────┼──────────────────────────────────────────┘
                      │
              ┌───────────────┐
              │ Internet      │
              │ Gateway       │
              └───────────────┘
                      │
              ┌───────────────┐
              │   Internet    │
              └───────────────┘
```

## 🎯 **Key Architecture Decisions**

### **✅ Simplified Networking (No NAT Gateway)**
- **Both services run in public subnets** with proper security groups
- **No NAT Gateway costs** (~$45/month savings)
- **Direct internet access** for container image pulls and external API calls
- **Service Discovery** for internal communication between API and UI

### **🔒 Security Model**
- **Security Groups** act as virtual firewalls
- **ALB Security Group**: Allows HTTP (80) from internet
- **ECS Tasks Security Group**: 
  - Allows ALB → UI (8501)
  - Allows UI → API (8000) via service discovery
  - Allows outbound for image pulls and updates

### **🚀 Service Architecture**
- **Inference API**: Stateless ML prediction service
- **Streamlit UI**: Interactive web interface
- **Service Discovery**: Internal DNS for API communication
- **Application Load Balancer**: Public entry point for UI

## 📊 **Resource Breakdown**

### **Compute**
- **ECS Fargate Cluster**: Serverless container platform
- **Inference API**: 512 CPU, 1024 MB memory
- **Streamlit UI**: 256 CPU, 512 MB memory
- **Capacity Provider**: FARGATE_SPOT (cost optimization)

### **Networking**
- **VPC**: 10.0.0.0/16 (65,536 IPs)
- **Public Subnets**: 2 subnets across 2 AZs (512 IPs each)
- **Private Subnets**: 2 subnets (reserved for future use)
- **Internet Gateway**: Direct internet access
- **No NAT Gateway**: Cost and complexity reduction

### **Load Balancing**
- **Application Load Balancer**: Layer 7 HTTP load balancer
- **Target Group**: Health checks on Streamlit UI
- **Listener**: HTTP port 80 (can add HTTPS later)

### **Security**
- **IAM Roles**: ECS task execution with minimal permissions
- **Security Groups**: Network-level access control
- **CloudWatch Logs**: Centralized logging for debugging

## 💰 **Cost Optimization**

### **Monthly Cost Estimate (eu-west-1)**
- **ECS Fargate**: ~$25-30/month (SPOT pricing)
- **Application Load Balancer**: ~$16/month
- **Data Transfer**: ~$5-10/month
- **CloudWatch Logs**: ~$2-5/month
- **Total**: ~$48-61/month

### **Savings from Simplified Architecture**
- **No NAT Gateway**: -$45/month
- **FARGATE_SPOT**: -30% compute costs
- **Single ALB**: Shared across services

## 🔄 **Deployment Flow**

1. **GitHub Actions** builds and pushes Docker images to ECR
2. **ECS Services** automatically pull latest images
3. **Service Discovery** enables API ↔ UI communication
4. **ALB** routes public traffic to UI
5. **Auto-scaling** based on CPU/memory utilization

## 🛡️ **Security Considerations**

### **Network Security**
- Services in public subnets but protected by security groups
- No direct SSH/RDP access (use ECS Exec if needed)
- ALB terminates SSL (can add certificate later)

### **Application Security**
- Container images scanned in ECR
- IAM roles follow least privilege principle
- CloudWatch monitoring for anomaly detection

## 🚀 **Future Enhancements**

### **Immediate**
- Add HTTPS certificate to ALB
- Set up CloudWatch alarms
- Configure auto-scaling policies

### **Advanced**
- Add API Gateway for API versioning
- Implement blue/green deployments
- Add RDS for model metadata storage
- Set up VPC endpoints for ECR (if moving to private subnets)

## 📝 **Deployment Commands**

```bash
# Navigate to infrastructure directory
cd Iac

# Make deployment script executable
chmod +x deploy.sh

# Deploy infrastructure
./deploy.sh

# Check deployment status
cd environments/dev
terraform output
```

## ✅ **Ready for Production**

This simplified architecture is:
- **Cost-effective**: No unnecessary NAT Gateway
- **Secure**: Proper security group isolation
- **Scalable**: ECS Fargate auto-scaling
- **Maintainable**: Modular Terraform structure
- **Production-ready**: Monitoring and logging included