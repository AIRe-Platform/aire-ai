# AIRe AI

This is the repository for AIRe AI module.

It uses LangChain framework to implement the AIRe platform's AI features.

## Getting Started

Run the following command to setup the development environment:

```bash
./setup_env.sh --dev
```

This will create a Python virtual environment and install necessary packages.

There are launch/debug configurations for VSCode.

Template for `development.env`, adjust as needed:

```
OPENAI_API_VERSION=2023-12-01-preview
OPENAI_API_TYPE=<set to 'azure' if using Azure OpenAI, otherwise omit.>
OPENAI_API_BASE=<set if using local inference server, otherwise omit.>
OPENAI_API_KEY=<either a legit API key if using a service, or any string if running local model>
AZURE_OPENAI_ENDPOINT=<set if using Azure OpenAI, omit otherwise>
AIRE_SERVICE_BASE=http://localhost:7071/api
AIRE_SERVICE_KEY=<use the same key as with other platform modules>
TOKEN_SIGNING_KEY=<use the same key as with other platform modules>
TOKEN_ENCRYPTION_KEY=<use the same key as with other platform modules>
PGVECTOR_CONNECTION_STRING=postgresql+psycopg2://<connection string here>
```

You may use `ALLOW_ANONYMOUS_USERS=1` to skip authentication for testing purposes.

## Local Inference

You can test the features with a local language model. Although, some features may not work correctly as the OpenAI-compatibility is not always perfect. Options for running local "OpenAI-compatible" servers:

- [LM Studio](https://lmstudio.ai/) is an application with a GUI for running models locally.
- [Ollama](https://ollama.ai) is a commandline application for running models locally. In addition to its own API, it also has OpenAI-compatible endpoints.
- [text-generation-webui](https://github.com/oobabooga/text-generation-webui) is another option and has a web interface for a GUI.
