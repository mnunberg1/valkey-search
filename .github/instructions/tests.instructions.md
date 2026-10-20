---
applyTo: "testing/**"
---

# Test review rules

Report only:

- Tests that cannot fail (no assertion, or an assertion on a constant).
- Assertions on the wrong value or the wrong side of a comparison.
- Dependence on timing, ordering, or an external service.

Do not ask for additional test cases and do not comment on test naming.
