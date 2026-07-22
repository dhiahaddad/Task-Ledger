# Architecture

## Dependency rule

Task Ledger uses a lightweight ports-and-adapters structure:

1. `domain` owns task state and invariants and imports no project layer.
2. `application` coordinates use cases and defines ports needed from the outside world.
3. `infrastructure` implements those ports using files and operating-system services.
4. `interfaces` compose the application and translate framework-specific input/output.

An inner layer never imports an outer layer. `TaskService` accepts a `TaskRepository`
protocol rather than constructing JSON persistence itself. Tests can therefore use an
in-memory implementation, and a future SQLite implementation can be added without
changing any use case.

## One use case, three adapters

Creating a task follows the same path everywhere:

```text
user gesture or command
    -> interface parses title, priority, and tags
    -> TaskService.create_task(...)
    -> Task validates its invariants
    -> TaskRepository.save(task)
    -> interface renders the result
```

Typer, PySide6, and Textual types stop at the interface boundary. Domain errors cross
that boundary and each adapter renders them appropriately.

## Composition

`interfaces.common.create_service` is the local composition root. It connects
`TaskService` to `JsonTaskRepository`. A larger application may create a dedicated
composition package, load configuration there, and inject logging, telemetry, or
database implementations.

## Persistence

The JSON repository stores a versioned document and writes through a temporary file
followed by `os.replace`. This prevents an interrupted write from leaving a partially
written database. Its in-process lock protects multiple threads; it is not intended to
coordinate concurrent writes from multiple processes. Replace it with a transactional
database when that becomes a requirement.

## Adding a new interface

Create another package below `interfaces`, depend on `TaskService` and domain result
types, and add an optional dependency group and entry point. Do not import existing UI
adapters or duplicate domain validation.

## Adding infrastructure

Define the capability as a protocol in `application.ports`, implement it under
`infrastructure`, and inject it at the composition root. This keeps external SDKs and
I/O concerns out of the use cases.

