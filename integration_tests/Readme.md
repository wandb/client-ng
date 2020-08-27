# Description

This directory contains integration tests for testing the client libraries various integrated systems.

The tests in this repository are also useful for logging. 

# Standalone tests

The tests files in the `test_scripts` directory are meant to be run as part of the automated test system as well as ad-hoc standalone tests for reproducing bugs, generating examples, etc.. 

For example
```
python3 integration_tests/test_scripts/media/image.py
```

# Development 

## Requirements

Python 3.7
Docker

There are two ways to run theses tests locally when testing

1.  Serve local yourself and run the python files against it for development. 


```bash
# Launch local
scripts/serve-local.sh

## Test setup

# Set environment variables
# This will set the WANDB_* environment varaiables for testing
eval $(python3 integration_tests/setup.py)

## Install deps
pip3 install -r requirements_dev.txt
pip3 install -r integration_tests/requirements.txt

### Proceed with your preffered methods of development

# REPL driven development
(cd integration-tests; python3)

# Run all tests
python3 -m pytest integration_tests


```

2. Run the full test suite using. This requires install CircleCI's local test runner.

NOTE: The circeci tests checkout the github. So you will not get updates unless you commit. This is a little frustrating as you get a long tail of commit messages, but is faster than waiting on CI.

```bash

### You must add to git for the local circle runner to pick up changes
git add -p; git commit -m "BUMP"; sh integration_tests/scripts/test-integration-local.sh

# Base command
sh integration_tests/scripts/test-integration-local.sh

```
