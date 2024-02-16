# A sandbox project Silly Net (SNet for short)
## Goal
Try different stacks to implement high-performance backends
* Python 3
* C++ userver/boost
* Go

## Structure
* docs
* infra
* services
* tools

## Makefile

### Install Tooling and Dependencies

This project uses Docker and it is expected to be installed. Please provide Docker at least 4 CPUs.

Run these commands to install everything needed.
*	$ `make dev-brew`
*	$ `make dev-docker`
*	$ `make dev-gotooling`

### Running Test

Running the tests is a good way to verify you have installed most of the dependencies properly.

*	$ make test


### Running The Project

*	$ make dev-up
*	$ make dev-update-apply
*   $ make token
*   $ export TOKEN=<token>
*   $ make users

You can use `make dev-status` to look at the status of your KIND cluster.