# Release Integrity Model

A release is a bounded statement about a specific repository state. It must identify the commit, included record families, conformance artifacts, known unresolved items, source-hydration status, and release decision. A release may describe foundation completeness without representing that public records have been populated or that any institution has adopted the model.

## Freeze conditions

- The worktree must be clean.
- Every release artifact is enumerated and digest-addressed.
- Conformance vectors and their recorded outcomes are included.
- Outstanding source, interpretation, implementation, or legal-validation work remains explicitly marked unresolved.
- A later release does not silently rewrite the earlier manifest.