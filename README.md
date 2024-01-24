# AIRe AI

This is the repository for AIRe AI module.

It uses LangChain framework to implement the AIRe platform's AI features.

## Getting Started

Run the following command to setup the development environment:

```bash
./setup_env.sh --dev
```

This will create a Python virtual environment and install necessary packages.

Adjust development environment with `development.env` file as needed.

There are launch/debug configurations for VSCode.

Example of `development.env`:

```
OPENAI_API_BASE=<Remove if using OpenAI's API or place URL of OpenAI compatible endpoints here.>
OPENAI_API_KEY=<Your API Key to OpenAI, or any string if using local API>
AIRE_SERVICE_BASE=http://localhost:7071/api
AIRE_SERVICE_KEY=<any string>
PGVECTOR_CONNECTION_STRING=<connection string here>
ALLOW_ANONYMOUS_USERS=1
```

`ALLOW_ANONYMOUS_USERS=1` is required for testing without signing in. Otherwise, you have to register and log in to your account.

## Local Inference

You can test the features with a local language model. Options for running local "OpenAI-compatible" servers:

- [LM Studio](https://lmstudio.ai/) is a fast and easy way to get up and running. Although, some features may not work correctly as the OpenAI-compatibility is not perfect.
- [text-generation-webui](https://github.com/oobabooga/text-generation-webui) is another option with more complete OpenAI-compatibility. The setup may be more involved.

Recent Mistral-based models have relatively low hardware requirements and perform well for their size.

## LangChain

Tips for using LangChain.

### Adding packages

```bash
# adding packages from 
# https://github.com/langchain-ai/langchain/tree/master/templates
langchain app add $PROJECT_NAME

# adding custom GitHub repo packages
langchain app add --repo $OWNER/$REPO
# or with whole git string (supports other git providers):
# langchain app add git+https://github.com/hwchase17/chain-of-verification

# with a custom api mount point (defaults to `/{package_name}`)
langchain app add $PROJECT_NAME --api_path=/my/custom/path/rag
```

Note: you remove packages by their api path

```bash
langchain app remove my/custom/path/rag
```

### Setup LangSmith (Optional)

LangSmith will help us trace, monitor and debug LangChain applications. 
LangSmith is currently in private beta, you can sign up [here](https://smith.langchain.com/). 
If you don't have access, you can skip this section


```shell
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your-api-key>
export LANGCHAIN_PROJECT=<your-project>  # if not specified, defaults to "default"
```

### Launch LangServe

```bash
langchain serve
```

### Running in Docker

This project folder includes a Dockerfile that allows you to easily build and host your LangServe app.

#### Building the Image

To build the image, you simply:

```shell
docker build . -t my-langserve-app
```

If you tag your image with something other than `my-langserve-app`,
note it for use in the next step.

#### Running the Image Locally

To run the image, you'll need to include any environment variables
necessary for your application.

In the below example, we inject the `OPENAI_API_KEY` environment
variable with the value set in my local environment
(`$OPENAI_API_KEY`)

We also expose port 8080 with the `-p 8080:8080` option.

```shell
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8080:8080 my-langserve-app
```
