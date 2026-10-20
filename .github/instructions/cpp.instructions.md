---
applyTo: "src/**/*.{cc,h}"
---

# Core module review rules

- Module API calls (`ValkeyModule_*`) have strict thread and context rules.
  Flag any call made without the required context or lock held, and any
  context opened but not freed on every path.
- Keyspace notification handlers and background index threads run concurrently
  with command execution. Flag shared state touched from both without
  synchronisation.
- RDB serialisation must round-trip: flag any field written but not read, or
  read at a different width or endianness than it was written.
- `absl::Status` must be checked and propagated, never discarded.
