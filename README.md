# nemori_mcp
> A Simple **M**odel **C**ontext **P**rotocol (MCP) Implementation for the Nemori Memory Service.

`nemori_mcp` is a dedicated tool server that utilizes **FastMCP** to expose the powerful long-term memory capabilities of the **Nemori** library as easily consumable tools for Large Language Models (LLMs).

You can find openapi demo video from [this](./docs/demo_openapi.mp4).

> [Nemori](https://github.com/nemori-ai/nemori) Repository: [https://github.com/nemori-ai/nemori](https://github.com/nemori-ai/nemori)

>Thanks to the [nemori-ai](https://github.com/nemori-ai) team for their work!

## ✨ Features

*   **Persistent Memory:** Utilizes Nemori's memory system, supporting both short-term (episodic) and long-term (semantic) memory.
*   **MCP Integration:** Easily integrates into LLM ecosystems via the **Model Context Protocol (MCP)**.
*   **Memory Retrieval:** Offers flexible memory searching, supporting various methods (e.g., `hybrid`, `vector`, `bm25`).

## 🛠️ Prerequisites

*   Python 3.9+
*   make

## 🚀 Quick Start

This repository includes a `Makefile` to simplify setup, dependency installation, and server management.

### 1. Installation

This step creates a Python virtual environment (`.__env`), installs the necessary dependencies (`requirements.txt`), and downloads the required spaCy language models (`en_core_web_sm` and `zh_core_web_sm`).

```bash
make install_deps
```

### 2. Running the Service

(1). Copy `.env.example` to `.env`.

(2). Set OPENAI_BASE_URL, OPENAI_API_KEY, etc.

#### Run MCP server

```bash
bash ./scripts/start_mcp.bash
```

#### Run [OpenApi server](https://docs.openwebui.com/openapi-servers) (For Open WebUI Integration)

If you need to connect via Open WebUI.

```bash
make start_openapi
```
> Set tool server url as `http://<ip>:8877`.

If you need to listen on a different port (e.g., 8878):

```bash
make start_openapi PORT=8878
```

## ⚙️ Exposed Tools

The memory service provides two core functionalities to the agent:

### `add_user_messages`

Adds new conversational messages to the persistent memory. This is crucial for **recording** context.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `messages` | `List[Message]` | A list of conversation turns, where `Message` is `{"role": str, "content": str}`. |
| **Returns** | `Dict` | Status of the operation. |
| **Note** | This tool is asynchronous and automatically waits for Nemori's semantic processing to ensure the newly added context is immediately searchable. |

### `search_user_memory`

Retrieves relevant historical or semantic context from the dedicated user's memory based on a query.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `query` | `str` | The query string or question to search for. |
| `search_method` | `str` | The method used for retrieval. Defaults to `vector`. |
| **Returns** | `List[Dict[str, Any]]` | A flattened list combining results from episodic and semantic memory searches, ordered by relevance. |

#### Available Search Methods

The `search_method` parameter accepts the following values (case-insensitive):

*   `vector` (Default)
*   `hybrid` (Recommended for general-purpose search)
*   `bm25`
*   `vector_norlift`

## 🧹 Cleanup Operations

To clear all persistent data (memory files and the underlying Chroma database), use the `clean_memory` command:

```bash
make clean_memory
```
This will delete the `./memories` and `./chroma_db` directories.