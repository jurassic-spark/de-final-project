# de-final-project

The intention is to create a data platform that extracts data from an operational database, archives it in a data lake, transforms it, and makes it available in a remodelled OLAP data warehouse.

---

## Project structure

```text
.
├── ingestion/
├── transform/
├── lambda_layers/
│   ├── build.sh
│   ├── ingest/
│   │   └── requirements.txt
│   └── transform/
│       └── requirements.txt
├── sql/
├── terraform/
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── requirements_dev.txt
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

### 5. Build the Lambda layers

Lambda-specific dependencies are separated by function:

```text
lambda_layers/
├── build.sh
├── ingest/
│   └── requirements.txt
└── transform/
    └── requirements.txt
```

The ingest layer contains dependencies required specifically by the ingestion Lambda.

The transform layer contains dependencies required specifically by the transformation Lambda.

Build both layers with:

```bash
bash lambda_layers/build.sh
```

The build script uses a Python 3.14 Docker container so that the generated dependencies are compatible with the Lambda runtime.

This creates:

```text
lambda_layers/
├── ingest/
│   └── build/
│       └── python/
└── transform/
    └── build/
        └── python/
```

The generated `build/` directories are ignored by Git and should not be committed.

The Lambda layers must be built before Terraform attempts to package them.

### 6. Initialise Terraform

This is a shared project and users could be provisioning with terraform regularly.
To avoid conflicts and issues this repository utilises a tf.state shared backend.
To ensure you are provisioning with terraform cleanly esnure you run;

```bash
cd terraform
terraform init
terraform validate
terraform plan
```

before applying anything. If terraform suggests a complete rebuild or throws up an error,
you will need to investigate the shared backend tf.state file and potenitally reconfigure using;

```bash
terraform init --reconfigure
```

If the tf.state has moved, there be need to run;

```bash
terraform init --migrate-state
```

Terraform packages the generated Lambda layer directories into ZIP archives and provisions the corresponding AWS Lambda layers.

The Lambda layers must therefore be built before running Terraform commands that depend on the layer archives.

### 7. CI/CD

GitHub Actions reproduces the project setup automatically.

The test workflow installs:

```text
requirements.txt
requirements_dev.txt
```

The Terraform workflow:

```text
- Checks out the repository
- Sets up Python 3.14
- Builds the ingest and transform Lambda layers
- Sets up Terraform
- Runs terraform init
- Runs terraform validate
```

This ensures the Lambda dependency layers exist before Terraform validates the infrastructure configuration.