# CLO835 Final Project — Kubernetes Application Deployment on AWS

## 📌 Overview

This project demonstrates the deployment of a containerized Flask web application on **Amazon EKS (Elastic Kubernetes Service)** with integration to multiple AWS services including:

* **Amazon ECR** for container image storage
* **Amazon S3 (private bucket)** for dynamic background image loading
* **Kubernetes ConfigMaps and Secrets** for configuration management
* **Kubernetes Services and Deployments** for application orchestration

The project follows a cloud-native architecture and showcases DevOps practices such as containerization, infrastructure-as-code, and CI/CD integration.

---

## 🏗️ Architecture

The application consists of two main components:

### 1. Flask Web Application

* Displays employee information form
* Loads background image dynamically from S3
* Reads configuration from Kubernetes ConfigMap
* Uses environment variables and secrets for configuration

### 2. MySQL Database

* Intended to store employee records
* Designed to use Kubernetes PersistentVolumeClaim (PVC)
* Backed by Amazon EBS for persistence (see limitations below)

---

## ⚙️ Features Implemented

### ✅ Application Enhancements

* Background image loaded from **private S3 bucket**
* Image path controlled via **ConfigMap**
* Application logs print S3 image path
* Application runs on **port 81**
* Author name injected via ConfigMap and displayed in UI
* Database credentials passed via **Kubernetes Secrets**

---

### ✅ Containerization

* Dockerfile created for Flask application
* Application tested locally using Docker

---

### ✅ GitHub & CI/CD

* Application source code stored in GitHub
* Incremental commits maintained
* GitHub Actions workflow configured for automation (build & push to ECR)

---

### ✅ Amazon ECR

* Docker image stored in Amazon ECR
* Kubernetes deployment pulls image from ECR

---

### ✅ Amazon EKS Deployment

* EKS cluster created with worker nodes
* Kubernetes manifests created and applied:

  * Deployment (Flask app)
  * Service (LoadBalancer)
  * ConfigMap
  * Secret
  * ServiceAccount
  * RBAC

---

### ✅ Public Access

* Application exposed via Kubernetes **LoadBalancer Service**
* Accessible through browser using AWS ELB endpoint

---

### ✅ Private S3 Integration

* Background image stored in private S3 bucket
* Application downloads image dynamically using AWS credentials
* Verified through application logs

---

### ✅ Dynamic Configuration (Image Change)

* New image uploaded to S3
* ConfigMap updated with new image key
* Deployment restarted
* Application reflects updated image in browser

---

## 📂 Kubernetes Manifests

The following Kubernetes manifests are included:

* `configmap.yaml` — Application configuration
* `serviceaccount.yaml` — Service account for app
* `rbac.yaml` — Role and role binding
* `clo835-app-deployment.yaml` — Flask deployment
* `clo835-service.yaml` — Public LoadBalancer service
* `mysql-deployment.yaml` — MySQL deployment
* `mysql-service.yaml` — MySQL internal service
* `mysql-pvc.yaml` — Persistent volume claim

---

## ⚠️ Limitations / Known Issues

### MySQL Persistence (Blocked)

The project includes full implementation for:

* PersistentVolumeClaim (PVC)
* MySQL Deployment
* MySQL Service
* Database initialization script

However, **dynamic volume provisioning using Amazon EBS is blocked** due to IAM restrictions in the lab environment.

#### Issue Details:

* EBS CSI driver cannot obtain AWS credentials
* PVC remains in `Pending` state
* Persistent Volume (PV) is not created
* MySQL pod cannot fully initialize
* Persistence validation cannot be demonstrated

#### Root Cause:

* Missing IAM permissions / IRSA configuration for EBS CSI driver
* Not a Kubernetes configuration issue

---

## 🧪 How to Run / Verify

### 1. Check Kubernetes Resources

```bash
kubectl get pods -n default
kubectl get svc -n default
kubectl get deployments -n default
```

### 2. Access Application

Open the LoadBalancer URL from:

```bash
kubectl get svc clo835-service -n default
```

### 3. Verify Logs

```bash
kubectl logs -l app=clo835-app -n default
```

Look for:

* S3 image path
* AWS credentials detection

---

### 4. Update Background Image

```bash
kubectl patch configmap clo835-app-config -n default --type merge -p '{"data":{"BG_IMAGE_KEY":"new_image.png"}}'
kubectl rollout restart deployment clo835-app -n default
```

Refresh browser to see updated image.

---

## 📸 Demonstration Highlights

* Application runs locally via Docker
* Image built and stored in ECR
* App deployed to EKS
* Accessible publicly via LoadBalancer
* Background image loaded from private S3
* Image updated dynamically using ConfigMap
* Kubernetes manifests organized and version-controlled

---

## 🎯 Conclusion

This project successfully demonstrates:

* Cloud-native application deployment on Kubernetes
* Integration with AWS services (ECR, S3, EKS)
* Configuration management using ConfigMaps and Secrets
* Public service exposure using LoadBalancer
* Dynamic application behavior without code changes

The only incomplete portion is persistent storage using EBS, which is blocked due to external IAM restrictions in the lab environment.

---

## 👤 Author

**Clyde Dsouza**
**Tien Dat Pham**

---

## 📎 Notes

* All required manifests are included in this repository
* All non-blocked requirements are fully implemented and verified
* Persistence limitation is documented and explained

---
