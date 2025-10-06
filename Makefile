.PHONY: help install install-dev format lint type-check test clean run docker-build docker-run docker-dev docker-stop docker-logs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  format       Format code with black and isort"
	@echo "  lint         Run linting checks"
	@echo "  type-check   Run type checking with mypy"
	@echo "  test         Run tests"
	@echo "  clean        Clean up build artifacts"
	@echo "  run          Run the MCP server"
	@echo ""
	@echo "Docker commands:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with docker-compose"
	@echo "  docker-dev   Run development version with docker-compose"
	@echo "  docker-stop  Stop Docker containers"
	@echo "  docker-logs  Show Docker container logs"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -e ".[dev]"

# Format code
format:
	black mcp_server/
	isort mcp_server/

# Run linting
lint:
	black --check mcp_server/
	isort --check-only mcp_server/

# Type checking
type-check:
	mypy mcp_server/

# Run tests
test:
	pytest tests/ -v

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the server
run:
	python -m mcp_server.main

# Docker commands
docker-build:
	docker build -t mcp-http-template .

docker-run:
	docker-compose up -d

docker-dev:
	docker-compose --profile dev up -d mcp-server-dev

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f
