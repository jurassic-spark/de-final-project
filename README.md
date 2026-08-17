# de-final-project
The intention is to create a data platform that extracts data from an operational database (and potentially other sources), archives it in a data lake, and makes it available in a remodelled OLAP data warehouse.

---

## Project structure

```text
.
├── data/
├── sql/
├── src/
├── terraform/
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/jurassic-spark/de-final-project.git
cd de-final-project
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install project dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Install development dependencies

```bash
python -m pip install -r requirements_dev.txt
```

### 5. Build the Lambda layer

Lambda layer dependencies are defined in:

```text
lambda_layer/requirements.txt
```

Build the layer with:

```bash
bash lambda_layer/build.sh
```

This creates:

```text
lambda_layer/build/python/
```

using Python 3.13 in a Linux `x86_64` Docker environment.

### 6. Initialise Terraform

```bash
cd terraform
terraform init
terraform validate
terraform plan
```

The Lambda layer must be built before running `terraform plan`.

### 7. CI/CD

GitHub Actions reproduces the same setup automatically.

The test workflow installs:

```text
requirements.txt
requirements_dev.txt
```

The deployment workflow:

```text
Checkout repository
- Set up Python 3.13
- Build Lambda layer
- Terraform
```