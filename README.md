# AWS Serverless Telemetry & Alerting System with AI Voice (Polly)

This project is a fully automated Serverless Infrastructure-as-Code (IaC) application built on AWS using Terraform. It processes telemetry data, analyzes it against configured thresholds, logs history, sends email alerts for anomalies, and utilizes **Amazon Polly** to dynamically generate English voice alerts accessible via a fully automated static S3 frontend Dashboard.

## 🏗️ Architecture

- **AWS API Gateway (HTTP v2):** Exposes endpoints for telemetry ingestion (`POST`) and history retrieval (`GET`).
- **AWS Lambda (Python 3.12):** Analyzes metrics, compares against DynamoDB thresholds, generates Polly MP3 files, sets S3 bucket URLs. 
- **Amazon DynamoDB:** 
  - `Config Table` (Stores limits/thresholds, e.g., CPU > 80%).
  - `History Table` (Stores continuous log of all parsed telemetry and flags triggered alerts).
- **Amazon SNS:** Fires an email notification to subscribed users when a threshold is breached.
- **Amazon Polly:** AI service text-to-speech engine acting dynamically on the `GET /alerts/{id}/audio` endpoint.
- **Amazon S3:**
  - `Audio Bucket`: Stores the dynamically generated MP3 files.
  - `Frontend Website Bucket`: Fully automated static hosting for `index.html`. 

## ⚙️ Prerequisites
- [Terraform](https://www.terraform.io/downloads) >= 1.10.0
- [Python 3.10+](https://www.python.org/downloads/)
- AWS CLI configured with active credentials (`aws configure`)

## 🚀 Deployment Guide

### 1. Configure Infrastructure Settings
1. Navigate to the `envs/dev` directory:
   ```bash
   cd envs/dev
   ```
2. Rename `terraform.tfvars.example` to `terraform.tfvars` and update your unique prefix and email:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```
   Modify `terraform.tfvars`:
   ```hcl
   prefix      = "your-unique-name-here" # Must be globally unique!
   alert_email = "your_real_email@example.com" # You will get an AWS confirmation here
   ```
3. Open `backend.tf`:
   - Either create your own S3 bucket to store Terraform state and specify its name in `bucket = "..."`.
   - OR, if you are testing locally, simply **delete/comment out** the entire `backend "s3" { ... }` block to use local state.

### 2. Deploy with Terraform
Still inside `envs/dev`, run:
```bash
terraform init
terraform plan
terraform apply --auto-approve
```
*Note: Terraform will output an `api_url`, `dashboard_url`, and table names at the end.*

**⚠️ IMPORTANT:** Check your email inbox. AWS SNS will send a "Subscription Confirmation" email. You **must click the Confirm link** in that email to receive alerts!

### 3. Setup Python Scripts
Return to the project root directory and install dependencies:
```bash
cd ../..
pip install -r requirements.txt
```

Prepare your environment variables by copying the example file:
```bash
cp .env.example .env
```
Open `.env` and fill it with output values from Terraform:
```env
API_URL=https://<your-id>.execute-api.eu-central-1.amazonaws.com
TABLE_NAME=your-unique-table
AWS_REGION=eu-central-1
```

### 4. Seed the Database
Run the seed script to populate DynamoDB with initial metric thresholds:
```bash
python seed.py
```
*(If you skip this, incoming metrics will not have thresholds to compare against).*

## 🧪 Testing the Application

1. **Open the Dashboard:** Open the `dashboard_url` (from terraform output) in your web browser. 
2. **Generate Traffic:** Run the simulation script:
   ```bash
   python generator.py
   ```
   *This script continuously sends simulated telemetry (metrics) to your API.*
3. **Observe the Magic:** 
   - The Dashboard automatically refreshes every 5 seconds.
   - Normal values show as green.
   - When the generator triggers a critical value (e.g., CPU > 80%), it appears as a red **Alert**.
   - Click the **"🔊 Play"** button next to an alert to hear **Amazon Polly** read out exactly what went wrong.
