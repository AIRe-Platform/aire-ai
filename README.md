# AIRe AI

This is the repository for the AIRe AI module.

It uses LangChain framework to implement the AIRe platform's AI features.

## Getting Started

Recommended Python version: 3.12.x

Run the following command to setup the development environment:

### Linux & macOS

```bash
# Optional: You might have to set execute permission for the script
chmod +x ./setup_env.sh

# Creates a virtual environment and install latest versions of the dependencies
./setup_env.sh --dev

# To install 'frozen' versions of the dependencies that are verified to work, call:
./setup_env.sh
```

### Windows

```bat
pip install virtualenv
python -m venv .env
.env\Scripts\activate.bat
pip install -r requirements_dev.txt
```

_TODO: Test the above script on Windows_

This will create a Python virtual environment and install necessary packages.

There are launch/debug configurations for VSCode.

Add these to your `development.env` to configure the module:

```env
AIRE_MODULE_ID=aire.development.ai
AIRE_SERVICE_BASE=http://localhost:7071/api
AIRE_SERVICE_KEY=<use the same key as with other platform modules>
TOKEN_SIGNING_KEY=<use the same key as with other platform modules>
TOKEN_ENCRYPTION_KEY=<use the same key as with other platform modules>
AZURE_COSMOS_DB_CONNECTION_STRING=<your Azure Cosmos DB for NoSQL connection string>
```

## Configuring Inference

Add the following environment variables to your `development.env`:

```env
OPENAI_API_VERSION=2024-02-01
OPENAI_API_KEY=<either a legit API key if using a service, or any string if running local model>
```

### Using Azure OpenAI

If using Azure OpenAI, add these:

```env
OPENAI_API_TYPE=azure
AZURE_OPENAI_ENDPOINT=https://<my-openai-resource>.openai.azure.com
```

### Using OpenAI-compatible API 

If you are using the official OpenAI endpoints, or if you have an inference server that has OpenAI-compatible endpoints, set the base address:

```env
OPENAI_API_BASE=http://<link-to-openai-compatible-api-endpoints>/v1
```

### Third-party APIs or local inference

Note that there may be compatibility issues when using other than OpenAI models, and that you might need to specify which models to use.

You can override default models with environment values:

```env
LLM_DEFAULT_MODEL_NAME=my-model-name-for-general-tasks
LLM_CHAT_MODEL_NAME=my-model-for-chatbot
LLM_EMBEDDINGS_MODEL_NAME=my-model-for-embeddings
```

## Anonymous Usage

You may use `ALLOW_ANONYMOUS_USERS=1` to skip authentication for testing purposes.

## Manual Deployment to Azure Container Registry

```sh
CONTAINER_REG=your_container_registry_name
IMAGE_NAME=aire-ai
IMAGE_TAG=latest

# Login to Azure CLI and Azure Container Registry
az login
az acr login --name $CONTAINER_REG

# Build and tag Docker image
docker build --platform linux/amd64 . -t $IMAGE_NAME
docker tag $IMAGE_NAME $CONTAINER_REG.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Push image to container registry
docker push $CONTAINER_REG.azurecr.io/$IMAGE_NAME:$IMAGE_TAG
```
