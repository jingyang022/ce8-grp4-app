## These are the Snyk commands we use in this capstone project

# What can we scan with Snyk
- Code (Javascript, Python etc.)
- Docker images
- Terraform code
- 3rd party libraries used


# Install Snyk
npm install -g snyk
(if doesn’t work) sudo npm install -g snyk

# Check version of snyk
snyk --version

# Run the below command to link CLI/IDE to Snyk Console:
snyk auth

# Test Repo code
Navigate to your github repository and run the command below
snyk code test 
(if doesn’t work) sudo snyk code test

# Test IaC code
Navigate to your github repository and run the command below
snyk iac test 
(if doesn’t work) sudo snyk iac test

# Test Docker images
Navigate to your github repository and build the image:
docker build -t snyk-image .
Run the command below
snyk container test snyk-image
(if doesn’t work) sudo snyk container test snyk-image

# How to Add SNYK_TOKEN to GitHub Secrets:
Go to your repository on GitHub.
Navigate to Settings > Secrets and variables > Actions.
Click New repository secret.
Enter SNYK_TOKEN as the Name and paste your Snyk API token as the Value.
SNYK_TOKEN
17624450-8e7f-4954-89a5-4209a7656435
Click Add secret.


jobs:
  snyk_scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Install Snyk CLI
        run: npm install -g snyk

      - name: Run Snyk test
        run: snyk test
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}


  name: Snyk Security Scan
    on: [push, pull_request]
    jobs:
      security:
        runs-on: ubuntu-latest
        steps:
        - name: Checkout code
        - uses: actions/checkout@v4
        - name: Run Snyk scan
          uses: snyk/actions/node@master
          with:
            token: ${{ secrets.SNYK_TOKEN }}
            project-name: ${{ github.ce8-grp4-capstone }}


name: Workflow for Snyk Infrastructure as Code
on: 
  push:
    branches: [ main ]
  # pull_request:
  #   branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Snyk to check Terraform files for issues
        uses: snyk/actions/iac@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --scan=resource-changes
          args: --severity-threshold=high
          args: --report



The SNYK_TOKEN is accessed securely from the GitHub Secrets store.
The SNYK_TOKEN is set as an environment variable, so Snyk can authenticate and perform the scan without exposing the token in the workflow file.

# Summary:
Security: Keeps sensitive tokens safe and encrypted.
Automation: Easily integrate Snyk into your CI/CD pipeline with secure access to the token.
Access Control: Ensures only authorized workflows or users can access the token.
Using GitHub Secrets is the best practice for securely managing sensitive information like API tokens in GitHub workflows.