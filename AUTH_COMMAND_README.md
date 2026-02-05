# Git Auth Command Implementation

## Overview

This implementation adds a new `auth` command to Git that supports token-based authentication.

## Usage

```bash
gt auth --token <token>
```

or

```bash
git auth --token <token>
```

## Example

```bash
gt auth --token JBuZpxBYcdhjnwISGO5cDk3yJG1rKfTzS2E3vzqVsMPlwLb1wh2ZtlyHk1o1
```

Output:
```
Authentication successful with token: JBuZpxBYcdhjnwISGO5cDk3yJG1rKfTzS2E3vzqVsMPlwLb1wh2ZtlyHk1o1
```

## Implementation Details

### Files Modified

1. **auth.c** (New file)
   - Implements the `cmd_auth` function
   - Handles the `--token` option using Git's parse-options API
   - Validates that a token is provided

2. **integrations/builtin.h**
   - Added declaration: `int cmd_auth(int argc, const char **argv, const char *prefix, struct repository *repo);`

3. **git.c**
   - Added command entry: `{ "auth", cmd_auth, RUN_SETUP_GENTLY }`
   - Enables the `auth` subcommand in Git

### Command Options

- `--token <token>`: Required. Specifies the authentication token to use.

### Build Instructions

To build Git with the new `auth` command:

1. Ensure you have the Git build dependencies installed
2. Run `make` in the repository root
3. The resulting `git` binary will include the new `auth` command

### Testing

A test script `test-auth-command.sh` is provided to simulate the command behavior:

```bash
./test-auth-command.sh --token <your-token>
```

The `gt` wrapper script allows you to use `gt` instead of `git`:

```bash
./gt auth --token <your-token>
```

## Notes

- The command uses `RUN_SETUP_GENTLY` which means it will work both inside and outside of a Git repository
- The token is printed to stdout for demonstration purposes
- In a production implementation, the token should be stored securely (e.g., in Git's credential system)
