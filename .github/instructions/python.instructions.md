---
applyTo: 'src/**/*.py,tests/**/*.py,scripts/**/*.py'
---

# Python Style Rules

Apply these conventions for all Python changes.

## Core Directives

- Target **Python 3.12+** with compatibility for modern packaging workflows (uv/Poetry)
- **Standard library first** - only add dependencies when they make code simpler, safer, or faster
- Generate code that is **typed, documented, and testable** by default
- Produce **small, single-responsibility** functions; keep classes lean and focused
- Use **f-strings**, **`pathlib.Path`**, **`logging`** (never `print`), and **context managers** for resources
- Prefer **comprehensions** to `map`/`filter`; never use wildcard imports

## Type safety and signatures

- Add type hints to all new or edited functions.
- In views, use explicit Django request/response types where practical.
- Prefer explicit return types for service and utility functions.

## Code style

- Prefer small, focused functions over large multi-purpose blocks.
- Use guard clauses and early returns for invalid states.
- Keep error handling explicit and actionable.
- Do not leave dead code, unused imports, or placeholder branches.

## Comments and documentation

- Avoid comments that restate obvious code.
- Add short comments only where behavior is non-obvious.
- Keep function/module docs concise and concrete.

### Agent Integration

**Prompt optimization:** "Write a typed, small function that accepts `Path` inputs, uses only the stdlib (unless clearly justified), raises specific exceptions, and includes a short docstring."

## Modern Python Features & Language Mastery

### Python 3.12+ Features

- **Improved error messages** and performance optimizations
- **Enhanced type system** with better inference and error reporting
- **Pattern matching** (structural pattern matching) with match statements
- **Performance improvements** in interpreter and core libraries
- **Better debugging support** with enhanced tracebacks

### Core Language Features

- **Advanced async/await patterns** with asyncio, aiohttp, and trio
- **Context managers** and the `with` statement for resource management
- **Dataclasses, Pydantic models**, and modern data validation
- **Generator expressions, itertools**, and memory-efficient data processing
- **Descriptors, metaclasses**, and advanced object-oriented patterns

## Type System & Interfaces

### Modern Typing Practices

- Add **explicit type hints** for parameters and returns
- Use **built-in generics** (`list[str]`, `dict[str, int]`, `set[Path]`)
- Use the **union operator** (`A | B`, `str | None`) instead of `Union`
- Handle forward references with **`from __future__ import annotations`**
- Use **`Protocol`** for structural typing; prefer **dependency injection** over concrete coupling

### Advanced Type Features

- **`TypeVar`/`ParamSpec/Concatenate`** for complex generics and decorator signatures
- **Avoid `Any`**; if unavoidable, scope narrowly and document rationale
- **`dataclasses`** for data containers; choose immutability (`frozen=True`) when possible
- **Type aliases** with `type ID = int` for clarity
- **`Annotated`** for metadata and validation constraints

## Standard Library First Approach

### Priority Libraries

- **`pathlib`** for all filesystem work; **`shutil`** for safe file operations
- **`contextlib`** for deterministic cleanup (including `AsyncExitStack`)
- **`functools`** for caching and partials; **`itertools`** for iteration tools
- **`collections`** for counters, dequeues, and default dict patterns
- **`argparse`** for CLI; parse paths directly into `Path`
- **`typing`** utilities for clarity; **`dataclasses`** for readable records

### Decision Framework

Only add third-party dependencies when they:

- Significantly simplify complex logic
- Provide essential security features not in stdlib
- Offer substantial performance improvements
- Are industry standards for specific domains (e.g., `requests` for HTTP)

## Code Architecture & Design Patterns

### Structure Guidelines

- **Prefer functions** for stateless operations
- **Use classes** when you need state, invariants, or polymorphism
- **Composition over inheritance**; keep inheritance shallow and purposeful
- Separate **pure computation** from **I/O** for testability
- Keep public APIs small, explicit (`__all__`) and documented

### Decision Guide: Classes vs Functions

**Use a class when:**

- Persistent state required
- Multiple related methods
- Lifecycle/cleanup needed
- Polymorphic behavior

**Use a function when:**

- Single small task
- No stored state
- Simple transformation
- Convenience wrapper

### Advanced Patterns

- **Design patterns** implementation (Singleton, Factory, Observer, etc.)
- **SOLID principles** in Python development
- **Dependency injection** and inversion of control
- **Event-driven architecture** and messaging patterns
- **Functional programming** concepts and tools
- **Plugin architectures** and extensible systems

## Resource Management & Asynchronous Programming

### Resource Management

- Always use `with` (or async `with`) for files, sockets, locks, and sessions
- **`contextlib.suppress`** only for specific, explained exceptions
- Proper cleanup patterns with `try`/`finally` when context managers aren't available

### Async Programming

- Prefer **`asyncio`** with `async`/`await` for I/O-bound concurrency
- **Do not** add async if it doesn't simplify or speed up I/O paths
- For task sets: gather as a group, propagate exceptions, apply explicit timeouts
- For HTTP client code, prefer **`httpx`** (sync or async) when stdlib insufficient
- **Advanced async patterns** with trio for structured concurrency

## Error Handling & Logging

### Exception Handling

- Raise **specific exceptions**; never use bare `except`
- Preserve tracebacks with **exception chaining**
- Add context to error messages
- Use **custom exceptions** for domain-specific errors

### Logging Best Practices

- Configure logging **once at app entry**; use module-level loggers elsewhere
- **Structured logging** with JSON for production systems
- Include **request/correlation IDs** for traceability
- **No secrets in logs** - sanitize sensitive data
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Performance Optimization & Profiling

### Performance Guidelines

- Pick the right **data structure** (list/set/dict/deque/tuple)
- Use **`functools.lru_cache`** for deterministic, expensive computations
- Document **invalidation policy** for cached functions
- Favor clear loops unless vectorization demonstrably improves clarity and speed
- **Measure first** (profilers, high-res timers) before optimizing

### Profiling & Optimization Tools

- **Profiling** with cProfile, py-spy, and memory_profiler
- **Performance optimization** techniques and bottleneck identification
- **Memory optimization** and garbage collection understanding
- **Caching strategies** with functools.lru_cache and external caches
- **Database optimization** with SQLAlchemy and async ORMs
- **NumPy, Pandas optimization** for data processing

### Concurrency Patterns

- **Async programming** for I/O-bound operations
- **Multiprocessing** and concurrent.futures for CPU-bound tasks
- **Threading** for I/O-bound work when async isn't suitable

## Security & Configuration Management

### Security Essentials

- **Never** commit secrets; read via env vars or secret manager
- Use **`secrets`** for tokens/secure randomness (not `random`)
- **Validate and sanitize** all external inputs
- Build file paths with `Path` joins, not string concatenation
- **Secure headers** (HSTS), secure/HTTPOnly cookies, CSP where feasible

### Subprocess Security

- **Default to `shell=False`** and pass **argument lists**
- Avoid `shell=True`; if forced, strictly validate/allowlist inputs
- Quote defensively and use proper escaping

### Configuration Management

- **12-factor app** principles with environment variables
- **Configuration validation** with Pydantic or similar
- **Secrets management** with proper rotation and access controls
- **Environment-specific settings** with clear inheritance

## Modern Tooling & Development Environment

### Primary Tools (2024/2025 ecosystem)

- **Package management** with **uv** (fastest Python package manager)
- **Code formatting and linting** with **ruff** (replacing black, isort, flake8)
- **Static type checking** with **ty** and **pyright**
- **Project configuration** with **pyproject.toml** (modern standard)
- **Pre-commit hooks** for code quality automation

### Tool Configuration

- **Ruff** = primary linter & formatter (target Py 3.12, 100-char lines)
- Enable comprehensive rule sets: errors, formatting, imports, modernization, best practices
- **Virtual environment** management with venv, pipenv, or uv
- **Dependency management** and lock files

### Development Workflow

- Project uses **`pyproject.toml`** with **uv** (primary) or **Poetry** (alternative)
- Prefer `uv run`/`poetry run` for tool execution
- **Modern Python packaging** and distribution practices
- **CI/CD integration** with quality gates

## Testing & Quality Assurance

### Testing Framework

- **Comprehensive testing** with **pytest** and pytest plugins
- **Property-based testing** with **Hypothesis**
- **Test fixtures, factories**, and mock objects
- **Coverage analysis** with pytest-cov and coverage.py
- **Performance testing** with pytest-benchmark

### Test Types & Strategies

- **Unit tests** for business logic
- **Integration tests** for external dependencies
- **End-to-end tests** for critical user flows
- **Performance tests** and benchmarking
- **Security testing** and vulnerability scanning

### Quality Metrics

- **Code coverage** >90% for critical components
- **Static analysis** with multiple tools
- **Dependency scanning** for vulnerabilities
- **Code quality metrics** and technical debt tracking

## Web Development & APIs

### Modern Web Frameworks

- **FastAPI** for high-performance APIs with automatic documentation
- **Django** for full-featured web applications (5.x+ with async views)
- **Flask** for lightweight web services
- **Pydantic** for data validation and serialization
- **SQLAlchemy 2.0+** with async support

### API Design Patterns

- **RESTful APIs** with proper HTTP methods and status codes
- **GraphQL** with modern Python libraries
- **WebSocket support** with FastAPI and Django Channels
- **Authentication and authorization** patterns (JWT, OAuth2, etc.)
- **API versioning** strategies and backward compatibility

### Background Processing

- **Background task processing** with Celery and Redis
- **Async task queues** with modern alternatives
- **Job scheduling** and cron-like functionality
- **Event-driven architectures** with message queues

## Data Science & Machine Learning

### Data Processing

- **NumPy and Pandas** for data manipulation and analysis
- **Matplotlib, Seaborn, and Plotly** for data visualization
- **Scikit-learn** for machine learning workflows
- **Data pipeline design** and ETL processes

### Development Environment

- **Jupyter notebooks** and IPython for interactive development
- **Data validation** and quality assurance
- **Performance optimization** for large datasets
- **Integration** with modern ML libraries (PyTorch, TensorFlow)

## DevOps & Production Deployment

### Containerization & Deployment

- **Docker containerization** and multi-stage builds
- **Kubernetes deployment** and scaling strategies
- **Cloud deployment** (AWS, GCP, Azure) with Python services
- **Infrastructure as Code** with Terraform or similar

### Monitoring & Operations

- **Monitoring and logging** with structured logging and APM tools
- **Performance monitoring** and alerting
- **Health checks** and service discovery
- **Graceful degradation** and circuit breaker patterns

### Security & Compliance

- **Security best practices** and vulnerability scanning
- **Container security** and image scanning
- **Secrets management** in production
- **Compliance** with industry standards (SOC2, GDPR, etc.)

## Advanced Python Patterns

### Metaprogramming

- **Advanced decorators** and context managers
- **Metaprogramming** and dynamic code generation
- **Descriptors** for advanced attribute access
- **Metaclasses** for framework development

### Functional Programming

- **Functional programming** concepts and tools
- **Immutable data structures** and patterns
- **Pure functions** and side-effect management
- **Monadic patterns** where appropriate

## Behavioral Traits & Best Practices

### Code Quality Standards

- Follows **PEP 8** and modern Python idioms consistently
- Prioritizes **code readability** and maintainability
- Uses **type hints** throughout for better code documentation
- Implements **comprehensive error handling** with custom exceptions
- Writes **extensive tests** with high coverage (>90%)

### Development Philosophy

- **Leverages Python's standard library** before external dependencies
- **Focuses on performance optimization** when needed
- **Documents code thoroughly** with docstrings and examples
- **Stays current** with latest Python releases and ecosystem changes
- **Emphasizes security** and best practices in production code

### Knowledge Areas

- **Python 3.12+** language features and performance improvements
- **Modern Python tooling** ecosystem (uv, ruff, pyright)
- **Current web framework** best practices (FastAPI, Django 5.x)
- **Async programming patterns** and asyncio ecosystem
- **Security considerations** and vulnerability prevention

## Response Approach & Methodology

### Analysis Framework

1. **Analyze requirements** for modern Python best practices
2. **Suggest current tools and patterns** from the 2024/2025 ecosystem
3. **Provide production-ready code** with proper error handling and type hints
4. **Include comprehensive tests** with pytest and appropriate fixtures
5. **Consider performance implications** and suggest optimizations
6. **Document security considerations** and best practices
7. **Recommend modern tooling** for development workflow
8. **Include deployment strategies** when applicable

### Example Focus Areas

- Migrating from legacy tools (pip to uv, black/isort to ruff)
- Optimizing Python code for async performance
- Designing FastAPI applications with proper patterns
- Setting up modern Python projects with full toolchain
- Implementing high-performance data processing pipelines
- Creating production-ready containerized applications
- Designing scalable background task systems
- Implementing modern authentication and security patterns

### Quality Assurance Checklist

- [ ] Code follows PEP 8 and modern Python idioms
- [ ] Comprehensive type hints included
- [ ] Error handling with specific exceptions
- [ ] Tests included with appropriate coverage
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] Documentation and docstrings provided
- [ ] Modern tooling recommendations included
