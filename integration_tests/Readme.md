# Description

This directory contains integration tests for testing the client libraries various integrated systems.

The tests in this repository are also useful for logging. 

## Run image test separately
python integration_tests/test_scripts/media/image.py

## Requirements

Python 3.7
Docker

# Development 

There are two ways to run theses tests locally:

1.  Serve local yourself and run the python files against it for development. 

```bash
scripts/serve-local.sh

# Run file

## Test setup
cd integration-tests/setup.py

# REPL driven development
(cd integration-tests; python3)
```

2. Run the full test suite using. This requires install CircleCI's local test runner.

NOTE: The circeci tests checkout the github. So you will not get updates unless you commit. This is a little frustrating as you get a long tail of commit messages, but is faster than waiting on CI.

```bash

### Reccomend one liner
git add -p; git commit -m "BUMP"; sh integration_tests/scripts/test-integration-local.sh


# Base command
sh integration_tests/scripts/test-integration-local.sh

```
