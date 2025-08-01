# House Price Predictor Infrastructure Architecture

## 🏗️ **Enterprise Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            AWS VPC (10.0.0.0/16)                               │
│                                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐                            │
│  │   Public Subnet     │    │   Public Subnet     │                            │
│  │   10.0.1.0/24       │    │   10.0.2.0/24       │                            │
│  │   (eu-west-1a)      │    │   (eu-west-1b)      │                            │
│  │                     │    │                     │                            │
│  │  ┌───────────────┐  │    │  ┌───────────────┐  │                            │
│  │  │ NAT Gateway   │  │    │  │ NAT Gateway   │  │                            │
│  │  │ (Redundant)   │  │    │  │ (Redundant)   │  │                            │
│  │  └───────────────┘  │    │  └───────────────┘  │                            │
│  └─────────────────────┘    └─────────────────────┘                            │
│           │                           │                                        │
│  ┌─────────────────────────────────────────────────────────┐                   │
│  │              Application Load Balancer                  │                   │
│  │                    (Port 80)                           │                   │
│  └─────────────────────────────────────────────────────────┘                   │
│           │                           │                                        │
│  ┌─────────────────────┐    ┌─────────────────────┐                            │
│  │  Private Subnet     │    │  Private Subnet     │                            │
│  │  10.0.3.0/24        │    │  10.0.4.0/24        │                            │
│  │  (eu-west-1a)       │    │  (eu-west-1b)       │                            │
│  │                     │    │                     │                            │
│  │  ┌───────────────┐  │    │  ┌───────────────┐  │                            │
│  │  │ ECS Fargate   │  │    │  │ ECS Fargate   │  │                            │
│  │  │ Inference API │  │    │  │ Streamlit UI  │  │                            │
│  │  │ Port: 8000    │  │    │  │ Port: 8501    │  │                            │
│  │  └───────────────┘  │    │  └───────────────┘  │                            │
│  └─────────────────────┘    └─────────────────────┘                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
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

### **🔒 Enterprise Security Model**

- **Private subnets** for all application workloads (enhanced security)
- **NAT Gateways** in public subnets for secure outbound internet access
- **Multi-AZ redundancy** with NAT Gateways in each availability zone
- **Application Load Balancer** in public subnets for controlled ingress
- **Service Discovery** for secure internal communication between services

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
- **Public Subnets**: 2 subnets across 2 AZs (512 IPs each) - Host NAT Gateways and ALB
- **Private Subnets**: 2 subnets across 2 AZs (512 IPs each) - Host ECS services
- **Internet Gateway**: Public internet access for ALB and NAT Gateways
- **NAT Gateways**: Multi-AZ redundant NAT Gateways for secure outbound access

### **Load Balancing**

- **Application Load Balancer**: Layer 7 HTTP load balancer
- **Target Group**: Health checks on Streamlit UI
- **Listener**: HTTP port 80 (can add HTTPS later)

### **Security**

- **IAM Roles**: ECS task execution with minimal permissions
- **Security Groups**: Network-level access control
- **CloudWatch Logs**: Centralized logging for debugging

## 💰 **Cost Analysis**

### **Monthly Cost Estimate (eu-west-1)**

- **ECS Fargate**: ~$35-45/month (SPOT pricing)
- **Application Load Balancer**: ~$16/month
- **NAT Gateways**: ~$90/month (2 AZs × $45/month each)
- **Data Transfer**: ~$10-15/month
- **CloudWatch Logs**: ~$5-10/month
- **Total**: ~$156-186/month

### **Enterprise Architecture Benefits**

- **Enhanced Security**: Private subnets isolate workloads from direct internet access
- **High Availability**: Multi-AZ NAT Gateway redundancy prevents single points of failure
- **Compliance Ready**: Meets enterprise security standards and audit requirements
- **Scalable Design**: Can easily add more services without architectural changes

## 🔄 **Deployment Flow**

1. **GitHub Actions** builds and pushes Docker images to ECR
2. **ECS Services** automatically pull latest images
3. **Service Discovery** enables API ↔ UI communication
4. **ALB** routes public traffic to UI
5. **Auto-scaling** based on CPU/memory utilization

## 🛡️ **Security Considerations**

### **Network Security**

- Services isolated in private subnets with no direct internet access
- NAT Gateways provide secure outbound connectivity for updates and ECR pulls
- ALB in public subnets provides controlled ingress to UI service
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
