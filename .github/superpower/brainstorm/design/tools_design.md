# Async Runtime Update
> **2026-03-10:** Project migrated to Node.js-like asynchronous runtime; synchronous loops are prohibited by automated tests.

# Tools Framework Design

`src/tools` contains utility functions and helper classes used throughout the
project.  The legacy `ToolParserFramework.py` mentioned in the todo list
highlights the need for a structured parser/registry for command‑line tools.

## Goals

- **Central registry** of available tools so agents and CLI scripts can
  discover and invoke them dynamically.
- **Parsing helpers** for standardizing command syntax, argument parsing, and
  configuration loading.
- **Error handling** wrappers to ensure uniform logging and exit codes.
- **Testability** – ability to stub or mock tools during automated testing.

## Legacy Insights

The todo item about splitting `ToolParserFramework.py` suggests the original
module was large and monolithic; refactoring should emphasize separation of
concerns.

## Brainstorm Topics

- Design of a `Tool` base class with metadata (name, description, version).
- Automatic documentation generation from tool definitions.
- Permission model for tools in multi-tenant or fleet environments.
- Integration with `tools.pm` (recently added) to enable Python-based tools as
  first-class citizens.

*Consider reusing any comments from `src-old` modules in the `tools/` folder
if present.*