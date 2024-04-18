# VoicePassport: Your Trusted Voice Authentication Companion 🎙️🔒

🔒🗣️ VoicePassport isa  robust and secure voice authentication system designed to ensure the authenticity of users through their unique voiceprints. Powered by Resemblyzer, VoicePassport leverages advanced voice processing technology to generate voice embeddings, which are compact numerical representations of voice characteristics. These embeddings capture the distinctive features of an individual's voice in a highly accurate and secure manner.

🔍🔐 Using these voice embeddings, VoicePassport employs a similarity search mechanism to authenticate users. By comparing the voice embeddings extracted from an input voice sample with those stored in its database, VoicePassport can determine the likelihood of a match, thereby verifying the identity of the user.

💼💬 VoicePassport offers a reliable and efficient means of authentication, enabling seamless user access to various applications and services while ensuring a high level of security. With its innovative approach to voice-based authentication, VoicePassport provides a convenient and dependable solution for organizations seeking robust identity verification mechanisms.

<p align="center">
  <img src="https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white" />
  <img src="https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white" />
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
  <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" />
</p>

## ✨ Features

* **🔒 Advanced Voice Authentication**: VoicePassport harnesses the cutting-edge Resemblyzer technology to analyze and generate unique voice embeddings from user audio samples. These embeddings serve as the foundation for precise and trustworthy user authentication based on voice similarity.

* **⛓️ Blockchain-Powered Security:** With blockchain integration, VoicePassport ensures unparalleled security and immutability in storing user authentication data. Each user's voice authentication details are securely hashed and recorded on the blockchain, establishing a tamper-proof ledger of user interactions.

* **💾 Efficient Vector Database:** VoicePassport leverages a specialized vector database to effectively store and query voice embeddings derived from user audio samples. By employing advanced vector similarity search algorithms, VoicePassport facilitates rapid and accurate matching of voice patterns for seamless user authentication.

* **🚀 Streamlined Workflow Management**: Empowered by Apache Airflow, VoicePassport streamlines the authentication process with robust workflow management capabilities. Through automated task orchestration, including audio processing, embedding generation, and database integration, VoicePassport ensures smooth and dependable operation.

* **👤 Intuitive User Experience:** Designed for user convenience, VoicePassport offers a hassle-free authentication experience. Users can effortlessly enroll their voice profiles and authenticate themselves with a simple voice command, eliminating the complexity of traditional password-based methods.

## 🛠️ Technologies Used

* **🎤 Resemblyzer**: Advanced voice analysis tool for generating voice embeddings.
* **🔍 QDrant**: Vector database for efficient storage and querying of voice embeddings.
* **🐍 Python**: Programming language used for backend development.
* **🌐 Flask**: Web framework for building the RESTful API.
* **🔗 Web3**: Python library for interacting with Ethereum blockchain.
* **📝 Solidity**: Programming language for writing smart contracts on the Ethereum blockchain.
* **🟣 Polygon PoS**: Scalable Ethereum sidechain for fast and low-cost transactions.
* **📦 MinIO**: Object storage service for storing voice samples and embeddings.
* **🍃 MongoDB**: NoSQL database for storing user metadata and authentication data.
* **🌀 Apache Airflow**: Workflow management tool for automation of audio processing tasks and database integration.
* **🐳 Docker**: Containerization platform for packaging VoicePassport application components.
* **🔀 HAProxy**: Load balancer for distributing incoming traffic across multiple Docker containers.

## How It Works
1. **Enrollment**: Users enroll their voice profiles by providing audio samples, which are processed by Resemblyzer to generate unique voice embeddings.
2. **Authentication**: During authentication, users speak a passphrase, and their voice is compared against the stored voice embeddings using vector similarity search.
3. **Blockchain Verification**: User authentication data is cryptographically hashed and recorded on the blockchain for verification and auditability.
4. **Apache Airflow Integration**: The entire authentication workflow is managed by Apache Airflow, ensuring efficient task execution and workflow orchestration.

## Installation
To install VoicePassport, simply clone the repository and follow the installation instructions in the [documentation](docs/installation.md).

## Usage
For detailed usage instructions, refer to the [user manual](docs/user_manual.md).

## Contributing
Contributions are welcome! Please read the [contribution guidelines](CONTRIBUTING.md) before submitting any pull requests.

## License
VoicePassport is licensed under the [MIT License](LICENSE).



