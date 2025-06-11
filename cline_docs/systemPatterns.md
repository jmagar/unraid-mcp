# System Patterns

## How the system is built

- The core application is a Python script: `unraid-mcp-server.py`.
- Python dependencies are managed via `requirements.txt`.
- The application will be containerized using Docker.

## Key technical decisions

- Utilize an official Python base image for the Docker container to ensure a stable and secure foundation.
- Python dependencies will be installed within the Docker image using `pip` and the `requirements.txt` file.
- Environment variables will be the primary method for configuring the application within the Docker container. The `.env.example` and `.env.local` files provide templates for these variables, but will not be copied directly into the image for security and flexibility.

## Architecture patterns

- Standard Docker containerization pattern for a Python application.
- The application is expected to be a network service, exposing one or more ports.
