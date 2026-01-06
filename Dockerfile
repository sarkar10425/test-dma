# =============================================================================
# MULTI-STAGE DOCKERFILE FOR GOOGLE CLOUD RUN DEPLOYMENT
# =============================================================================
# This Dockerfile creates a containerized version of the multi-agent system
# optimized for Google Cloud Run deployment with security best practices

# =============================================================================
# BASE IMAGE SELECTION
# =============================================================================
# Use Python 3.13 slim image as the base
# - python:3.13-slim: Lightweight Python runtime with minimal system packages
# - 'slim' variant reduces image size and attack surface compared to full Python image
# - Python 3.13 provides the latest features and performance improvements
# - Compatible with Google ADK requirements
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y git && \
    apt install -y graphviz graphviz-dev && \
    apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/*
# =============================================================================
# WORKING DIRECTORY SETUP
# =============================================================================
# Set the working directory inside the container to /app
# All subsequent commands will be executed relative to this directory
# This is where our application code and dependencies will be installed
WORKDIR /app

# =============================================================================
# DEPENDENCY INSTALLATION (OPTIMIZATION LAYER)
# =============================================================================
# Copy only requirements.txt first to leverage Docker layer caching
# This allows Docker to cache the dependency installation step
# If requirements.txt doesn't change, this layer won't be rebuilt
COPY requirements.txt .

# Install Python dependencies with optimization flags
# --no-cache-dir: Don't store pip cache to reduce image size
# -r requirements.txt: Install from requirements file
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# SECURITY: NON-ROOT USER CREATION
# =============================================================================
# Create a non-root user for security best practices
# Running containers as root is a security risk - if the container is compromised,
# the attacker would have root access to the container
# 
# adduser flags explained:
# --disabled-password: Don't set a password (login via key/token only)
# --gecos "": Skip interactive prompts for user information
# myuser: The username for our application user
RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app
    
# chown command breakdown:
# - chown: Change ownership command
# - -R: Recursive flag - applies ownership change to all files and subdirectories
# - myuser:myuser: Sets both user and group ownership to 'myuser'
#   * First 'myuser' = user owner (who owns the files)
#   * Second 'myuser' = group owner (which group owns the files)
# - /app: Target directory - changes ownership of /app and all its contents
# 
# Why this is needed:
# - Files copied by COPY command are owned by root (since Docker runs as root)
# - When we switch to 'myuser' later, that user needs read/write access
# - Without this, the application would get "permission denied" errors
# - This ensures 'myuser' can read application files and write to any output directories

# =============================================================================
# APPLICATION CODE DEPLOYMENT
# =============================================================================
# Copy all application files to the container
# This includes:
# - main.py (FastAPI application entry point)
# - agents/ directory (all agent definitions and configurations)
# - tools/ directory (custom tools like file_writer_tool.py)
# - utils/ directory (utilities like file_loader.py)
# - Any other project files
# 
# Note: .dockerignore file can be used to exclude unnecessary files
COPY . .

# =============================================================================
# SECURITY: SWITCH TO NON-ROOT USER
# =============================================================================
# Switch to the non-root user for all subsequent operations
# This ensures the application runs with limited privileges
# Even if there's a security vulnerability, the impact is minimized
USER myuser

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
# Add the user's local bin directory to PATH
# This ensures any user-installed packages are accessible
# Some Python packages install executables in ~/.local/bin
ENV PATH="/home/myuser/.local/bin:$PATH"

# =============================================================================
# CONTAINER STARTUP COMMAND
# =============================================================================
# Define the command that runs when the container starts
# This uses the "exec form" of CMD (JSON array format) which is preferred
# 
# Detailed CMD breakdown:
# 
# ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
# 
# 1. "sh": Execute the Bourne shell
#    - Uses the system's default shell interpreter
#    - Lightweight and available in all Linux containers
# 
# 2. "-c": Shell flag meaning "execute the following command string"
#    - Tells sh to run the command that follows as a single string
#    - Allows environment variable expansion (like $PORT)
#    - Without -c, sh would try to read from stdin or a file
# 
# 3. "uvicorn main:app --host 0.0.0.0 --port $PORT": The actual command string
# 
#    uvicorn: 
#    - Lightning-fast ASGI (Asynchronous Server Gateway Interface) server
#    - Designed for Python async frameworks like FastAPI
#    - Handles HTTP requests and WebSocket connections efficiently
#    - Production-ready server with automatic worker management
# 
#    main:app:
#    - Module:object notation for importing the FastAPI application
#    - "main" = the Python file (main.py) containing our FastAPI app
#    - "app" = the variable name of the FastAPI instance in main.py
#    - Equivalent to: from main import app
# 
#    --host 0.0.0.0:
#    - Bind to all available network interfaces
#    - 0.0.0.0 means "listen on all IP addresses"
#    - Required for Cloud Run: containers must accept traffic from any source
#    - Default would be 127.0.0.1 (localhost only), which Cloud Run can't reach
# 
#    --port $PORT:
#    - Use the PORT environment variable for the listening port
#    - Cloud Run automatically sets PORT (usually 8080)
#    - $PORT expands to the actual port number at runtime
#    - The application MUST listen on this specific port to receive traffic
# 
# Why use sh -c instead of direct uvicorn?
# - Allows environment variable expansion ($PORT)
# - Provides shell features if needed (pipes, redirects, etc.)
# - More flexible for complex startup commands
# 
# Alternative approaches:
# - Direct: CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
# - Script: CMD ["./start.sh"] (with startup script)
CMD adk web --port=8080 --host=0.0.0.0 "/app"

# =============================================================================