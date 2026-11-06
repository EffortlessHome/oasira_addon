# Project Coding Instructions

## Mission

Write correct, maintainable code that fits the existing architecture.

Correctness is more important than speed.

Do not assume an API, library behavior, file path, function name, configuration option, or framework convention. Verify it from the existing code, installed dependencies, project documentation, or available tooling.

---

# 1. Before Making Changes

Before editing anything:

1. Understand the user's requested outcome.
2. Inspect the existing implementation.
3. Find related code and existing patterns.
4. Identify the smallest set of files that need to change.
5. Check how the project is built, tested, linted, and type-checked.
6. Identify compatibility requirements.

Do not start writing code immediately when the task involves an unfamiliar area of the project.

For non-trivial tasks, first explain the implementation approach briefly.

---

# 2. Follow Existing Architecture

Prefer existing project patterns over introducing new ones.

Before creating:

- a new service
- utility
- abstraction
- state-management pattern
- API client
- database access pattern
- component pattern
- dependency

search the repository for an existing implementation that can be reused.

Do not introduce a new library when the repository already has equivalent functionality.

Do not refactor unrelated code.

Do not rename, move, or rewrite unrelated files.

---

# 3. Make Small Changes

Implement complex tasks incrementally.

Do not attempt a large feature as one enormous edit.

Preferred workflow:

1. Inspect
2. Implement one logical change
3. Verify
4. Fix problems
5. Implement the next logical change
6. Verify again

Keep each change as small as reasonably possible.

---

# 4. Verification Is Mandatory

Never consider a coding task complete immediately after writing code.

After making changes:

1. Format the modified files.
2. Run the project's type checker/compiler.
3. Run relevant tests.
4. Run lint/static analysis when available.
5. Inspect the resulting errors and warnings.
6. Fix errors caused by the changes.
7. Run verification again.

Continue until the relevant checks pass.

If the project has no automated tests for the changed functionality, perform the strongest available verification instead.

Never claim that code works if you have not verified it.

---

# 5. When a Command Fails

Do not make random changes after an error.

Instead:

1. Read the complete error.
2. Identify the exact failing file, symbol, command, or dependency.
3. Inspect the relevant source.
4. Determine the root cause.
5. Make the smallest correction.
6. Run the failed command again.

Do not repeatedly try unrelated fixes.

---

# 6. Do Not Guess

If something is uncertain:

- search the repository
- inspect package/dependency definitions
- inspect existing usages
- inspect type definitions
- inspect framework documentation available to the project
- use compiler/type-checker feedback

Do not invent APIs.

Do not invent configuration properties.

Do not invent function parameters.

Do not invent database fields.

Do not invent entity IDs.

Do not invent file paths.

If the required information cannot be determined, state what is missing rather than fabricating an answer.

---

# 7. Preserve Existing Behavior

Unless explicitly requested:

- Do not change public APIs.
- Do not change existing behavior.
- Do not change database schemas.
- Do not change authentication behavior.
- Do not change configuration.
- Do not change dependencies.
- Do not change deployment behavior.

If a requested feature requires one of these changes, identify it before making the change.

---

# 8. Error Handling

Handle errors consistently with the existing project.

Do not hide errors with:

- empty catch blocks
- ignored promises
- unnecessary optional chaining
- arbitrary fallback values
- silent failures
- disabled compiler checks
- disabled lint rules

Do not suppress an error unless there is a documented reason.

---

# 9. Types

Prefer strong typing.

Do not use `any`, unsafe casts, or equivalent escape hatches merely to make an error disappear.

When a type error occurs, determine why the types are incompatible and fix the underlying problem.

---

# 10. Dependencies

Do not add dependencies unless necessary.

Before adding one:

1. Search the existing dependencies.
2. Check whether the project already provides equivalent functionality.
3. Verify that the dependency is compatible with the project's platform and runtime.
4. Explain why it is necessary.

Do not update unrelated dependencies as part of a feature.

---

# 11. Generated Files

Do not manually edit generated files unless the project explicitly requires it.

Find the source that generates them and modify that instead.

---

# 12. Tests

When adding functionality, add or update tests when the project has a testing framework.

Tests should verify behavior, not merely implementation details.

For bug fixes, whenever practical, add a regression test that would have failed before the fix.

---

# 13. Final Response

Before saying the task is complete, verify:

- [ ] Requested functionality implemented
- [ ] Existing behavior preserved
- [ ] No obvious errors
- [ ] Compiler/type checker passes
- [ ] Relevant tests pass
- [ ] Linter/static analysis passes when available
- [ ] No unnecessary files changed
- [ ] No unnecessary dependencies added

In the final response, briefly state:

1. What changed
2. What was verified
3. Any remaining limitations or warnings

Do not claim successful verification if it was not performed.