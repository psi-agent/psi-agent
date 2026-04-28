## ADDED Requirements

### Requirement: Channel CLI imports follow Python module structure

The `psi_agent.channel.__init__.py` file SHALL import CLI classes in a way that avoids E402 lint violations.

#### Scenario: No E402 violations in channel __init__.py
- **WHEN** running `ruff check src/psi_agent/channel/__init__.py`
- **THEN** no E402 errors are reported

#### Scenario: Channel CLI commands still work
- **WHEN** running `psi-agent channel cli --help`
- **THEN** the help text is displayed correctly

#### Scenario: Channel REPL command works
- **WHEN** running `psi-agent channel repl --help`
- **THEN** the help text is displayed correctly

#### Scenario: Channel Telegram command works
- **WHEN** running `psi-agent channel telegram --help`
- **THEN** the help text is displayed correctly

### Requirement: Workspace CLI imports follow Python module structure

The `psi_agent.workspace.__init__.py` file SHALL import CLI classes in a way that avoids E402 lint violations.

#### Scenario: No E402 violations in workspace __init__.py
- **WHEN** running `ruff check src/psi_agent/workspace/__init__.py`
- **THEN** no E402 errors are reported

#### Scenario: Workspace pack command works
- **WHEN** running `psi-agent workspace pack --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace unpack command works
- **WHEN** running `psi-agent workspace unpack --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace mount command works
- **WHEN** running `psi-agent workspace mount --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace umount command works
- **WHEN** running `psi-agent workspace umount --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace snapshot command works
- **WHEN** running `psi-agent workspace snapshot --help`
- **THEN** the help text is displayed correctly
