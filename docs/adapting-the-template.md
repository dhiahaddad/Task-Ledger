# Adapting the template

1. Choose the distribution name (`task-ledger`) and import name (`task_ledger`).
2. Update project metadata, console scripts, documentation, and application titles.
3. Replace `domain.models.Task` with the project's core concepts and invariants.
4. Replace `TaskService` methods with use cases expressed in domain language.
5. Replace or retain `TaskRepository`; keep concrete storage in `infrastructure`.
6. Adapt each interface independently, calling the same application services.
7. Replace sample tests while preserving unit and integration test boundaries.
8. Update native packaging names, icons, signing, and release settings.
9. Revisit optional dependencies and delete interfaces the project does not ship.
10. Run `uv lock` and all checks before the first commit in the derived project.

Avoid a global search-and-replace without reviewing import paths, workflow artifact
names, environment variable names, and operating-system application identifiers.

