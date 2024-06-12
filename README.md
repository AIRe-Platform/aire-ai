## TODO: Refactor this document to have an structure like this:
## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Configuration](#configuration)
5. [Contributing](#contributing)
6. [API Reference](#api-reference)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Roadmap](#roadmap)
10. [FAQ](#faq)
11. [Troubleshooting](#troubleshooting)
12. [License](#license)
13. [Acknowledgments](#acknowledgments)
14. [Contact](#contact)

# AIRe AI

This is the repository for the AIRe AI module.

It uses LangChain framework to implement the AIRe platform's AI features.

## Getting Started

Run the following command to setup the development environment:

```bash
./setup_env.sh --dev
```

This will create a Python virtual environment and install necessary packages.

There are launch/debug configurations for VSCode.

Add these to your `development.env` to configure the module:

```env
AIRE_SERVICE_BASE=http://localhost:7071/api
AIRE_SERVICE_KEY=<use the same key as with other platform modules>
TOKEN_SIGNING_KEY=<use the same key as with other platform modules>
TOKEN_ENCRYPTION_KEY=<use the same key as with other platform modules>
PGVECTOR_CONNECTION_STRING=postgresql+psycopg2://<connection string here>
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

If you are using OpenAI's service, or if you have an inference server that has OpenAI-compatible endpoints, set the base address:

```env
OPENAI_API_BASE=http://<link-to-openai-compatible-api-endpoints>/v1
```

## Anonymous Usage

You may use `ALLOW_ANONYMOUS_USERS=1` to skip authentication for testing purposes.

## Local Inference

You can test the features with a local language model. Although, some features may not work correctly as the OpenAI-compatibility is not always perfect. 

Here are various options for running local "OpenAI-compatible" inference servers:

- [LM Studio](https://lmstudio.ai/) is an application with a GUI for running models locally.
- [Ollama](https://ollama.ai) is a commandline application for running models locally. In addition to its own API, it also has OpenAI-compatible endpoints.
- [KoboldCpp](https://github.com/LostRuins/koboldcpp) is another option for running local models.
- [text-generation-webui](https://github.com/oobabooga/text-generation-webui) is another option and has a web interface for a GUI.
