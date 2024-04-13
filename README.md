# VoicePassport 🎙️🔒

VoicePassport is a secure voice authentication system that utilizes Resemblyzer to generate voice embeddings and performs similarity search for user authentication.

## Features

### Voice Authentication
VoicePassport employs Resemblyzer, an advanced voice analysis tool, to generate voice embeddings from user audio samples. These embeddings are then used for accurate and reliable user authentication based on voice similarity.

### Blockchain Integration
To enhance security and immutability, VoicePassport integrates blockchain technology to securely store user authentication data. Each user's voice authentication information is cryptographically hashed and recorded on the blockchain, providing a tamper-proof record of user interactions.

### Vector Database
VoicePassport utilizes a vector database to efficiently store and query voice embeddings generated from user audio samples. By leveraging vector similarity search algorithms, VoicePassport enables fast and accurate matching of voice patterns for user authentication.

### Apache Airflow Workflow
VoicePassport streamlines the authentication process using Apache Airflow for workflow management. With Airflow's powerful task orchestration capabilities, VoicePassport automates audio processing tasks, embedding generation, and database integration, ensuring smooth and reliable operation.

## User-Friendly Experience
VoicePassport is designed with user convenience in mind, offering a seamless authentication experience. Users can easily enroll their voice profiles and authenticate themselves with a simple voice command, eliminating the need for complex passwords or authentication methods.

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



