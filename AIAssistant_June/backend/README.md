# AIWordingAssist

AIWordingAssist is an advanced application designed for document ingestion, retrieval, and interaction with language models. This project leverages state-of-the-art techniques in natural language processing and machine learning to provide efficient and effective solutions for various text-based tasks.

## Project Structure

The project is organized into several key components:

- **src/app**: Contains the core application logic, including API routes, services, retrieval logic, chunking strategies, embeddings, and LLM abstraction.
- **data**: Stores raw and processed data, including documents and embeddings.
- **cli**: Command-line interface scripts for document ingestion, querying, and other functionalities.
- **tests**: Unit tests for various components of the application to ensure reliability and correctness.
- **deployment**: Configuration files and scripts for deploying the application in different environments.
- **notebooks**: Jupyter notebooks for exploration and evaluation of the application.

## Features

- **Document Ingestion**: Supports various document formats (PDF, DOCX, JSON) for seamless ingestion and processing.
- **Retrieval Mechanisms**: Implements multiple retrieval strategies, including BM25 and vector-based methods, for efficient information retrieval.
- **Embedding Generation**: Utilizes advanced embedding techniques to enhance the understanding of text data.
- **Evaluation Framework**: Provides tools for evaluating the performance of retrieval and generation processes.
- **Customizable**: Easily extendable architecture to accommodate new features and improvements.

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd AIWordingAssist
pip install -r deployment/requirements.txt
```

## Usage

To run the application, use the following command:

```bash
uvicorn src.app.main:app --reload
```

For command-line operations, you can use the scripts located in the `cli` directory.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.