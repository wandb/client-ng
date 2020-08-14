# Description

This directory contains integration tests for testing the client libraries various integrated systems.

## Requirements

Python 3.7
Docker

# Development 

There are two ways to run theses tests locally:

1.  Serve local yourself and run the python files against it for development

```bash
scripts/serve-local.sh

# Run file
(cd integration-tests; python setup.py)

# REPL driven development
(cd integration-tests; python3)
```

2. Run the full test suite using. This requires install CircleCI's local test runner.

```bash
scripts/test-integration-local.sh
```
