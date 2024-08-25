<div align="center">

# Document-Vector-Store

[![python](https://img.shields.io/badge/-Python_3.12-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pytorch](https://img.shields.io/badge/PyTorch_2.0+-ee4c2c?logo=pytorch&logoColor=white)](https://pytorch.org/get-started/locally/)
[![hydra](https://img.shields.io/badge/Config-Hydra_1.3-89b8cd)](https://hydra.cc/)
[![black](https://img.shields.io/badge/Code%20Style-Black-black.svg?labelColor=gray)](https://black.readthedocs.io/en/stable/)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/) <br>
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/ashleve/lightning-hydra-template#license)


A base project for a document vector store which can be built upon.

</div>

<br>

## 📌  Important Tidbits

✅ Modular Design <br>
Easily add new models, text splitters, vector DBs and more as easy as adding a config file.

✅ Containerized <br>
Built on top of Docker and Docker Compose for easy deployment.

**Limitations:**

❌ Built for .txt files (but simple to update to all file formats) <br>
For the purpose of the project limited it to a .txt base loader as I just grabbed some books off Project Gutenberg for testing.

❌ No unit tests / heath-check <br>
I wouldn't deploy this without adding some CI testing and health checks.

❌ Unoptimized <br>
There's a ton of things that could be optimized in this project, load times and vectorization are the main ones. But also the docker image could be made smaller and adding a caching layer to the vector DB would be good. The API isn't async. Also, I think Langchain is bloated, and the abstractions are poorly throughout, which makes modularity difficult. I would probably switch to a more lightweight library or build from scratch many of the components.

> **Note**: Besides Langchain, the limitations are mostly easy to fix but I'm trying to timebox this project to a few hours.

<br>

## Main Technologies

[Hydra](https://github.com/facebookresearch/hydra) - a framework for elegantly configuring complex applications. The key feature is the ability to dynamically create a hierarchical configuration by composition and override it through config files and the command line.

[Langchain](https://www.langchain.com/) - a library for building language models.

[PyTorch](https://pytorch.org/) - an open-source machine learning library based on the Torch library.

<br>

## How to run

### 1. Clone the repository

```bash
git clone https://github.com/natephysics/document-vector-store.git
cd Document-Vector-Store
```

### 2. Create the credentials file

Create a `hf.yaml` file in the `configs/credentials/` path of the project and add the following:

```yaml
api_token: hf_YourTokenGoesHere
```

Before I get any comments about the security of this, I'm aware that this is not secure. I would normally use a secret system on the cloud platform or sops to encrypt this file.

### 3. Build the Docker image

```bash
docker build -t doc-vec-store .
```

### 4. Run the Docker container

```bash
docker run -p 8080:8080 doc-vec-store
```

### Settings
To change the settings of the project, you can modify the `configs/deply.yaml` file. The project is based on the hydra framework, so you can override any setting by adding a new config file or using the command line. For more details on how to use Hydra, check out the [documentation](https://hydra.cc/docs/intro).
