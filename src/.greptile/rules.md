# Review rules — `src/` (core module)

Inherits the repository-root rules. Additional rules for the core module:

- This code runs inside the Valkey server process. A crash here takes down the
  whole server, so memory and lifetime defects outrank everything else.
- Module API calls (`RedisModule_*` / `ValkeyModule_*`) have strict rules about
  which thread may call them and when a context must be locked or freed. Flag
  any call made without the required context or lock held, and any context that
  is opened and not freed on every path.
- Keyspace notification and background-index paths run concurrently with
  command execution. Flag shared state touched from both without
  synchronisation.
- RDB serialisation must round-trip. Flag any field written but not read, or
  read with a different width or endianness than it was written with.
