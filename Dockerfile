# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY . .

# Make port UNRAID_MCP_PORT available to the world outside this container
# Defaulting to 6970, but can be overridden by environment variable
EXPOSE 6970

# Define environment variables (defaults, can be overridden at runtime)
ENV UNRAID_MCP_PORT=6970
ENV UNRAID_MCP_HOST="0.0.0.0"
ENV UNRAID_MCP_TRANSPORT="streamable-http"
ENV UNRAID_API_URL=""
ENV UNRAID_API_KEY=""
ENV UNRAID_VERIFY_SSL="true"
ENV UNRAID_MCP_LOG_LEVEL="INFO"

# Run unraid-mcp-server.py when the container launches
CMD ["python", "unraid-mcp-server.py"]
