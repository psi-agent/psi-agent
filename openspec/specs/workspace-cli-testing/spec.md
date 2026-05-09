## ADDED Requirements

### Requirement: Workspace pack CLI entry point
`psi-workspace-pack` CLI SHALL correctly create config and call the pack API.

#### Scenario: Pack CLI creates correct config
- **WHEN** `Pack(input_dir="/tmp/in", output_file="/tmp/out", tag="v1")` is called
- **THEN** the correct `pack()` API SHALL be called with matching arguments

#### Scenario: Pack CLI main calls tyro
- **WHEN** `main()` is called
- **THEN** `tyro.cli(Pack)` SHALL be invoked

### Requirement: Workspace unpack CLI entry point
`psi-workspace-unpack` CLI SHALL correctly create config and call the unpack API.

#### Scenario: Unpack CLI creates correct config
- **WHEN** `Unpack(input_file="/tmp/in", output_dir="/tmp/out")` is called
- **THEN** the correct `unpack()` API SHALL be called with matching arguments

#### Scenario: Unpack CLI main calls tyro
- **WHEN** `main()` is called
- **THEN** `tyro.cli(Unpack)` SHALL be invoked

### Requirement: Workspace mount CLI entry point
`psi-workspace-mount` CLI SHALL correctly create config and call the mount API.

#### Scenario: Mount CLI creates correct config
- **WHEN** `Mount(input_file="/tmp/in", output_dir="/tmp/out", layer="v1")` is called
- **THEN** the correct `mount()` API SHALL be called with matching arguments

#### Scenario: Mount CLI main calls tyro
- **WHEN** `main()` is called
- **THEN** `tyro.cli(Mount)` SHALL be invoked

### Requirement: Workspace umount CLI entry point
`psi-workspace-umount` CLI SHALL correctly create config and call the umount API.

#### Scenario: Umount CLI creates correct config
- **WHEN** `Umount(mount_point="/tmp/mnt")` is called
- **THEN** the correct `umount()` API SHALL be called with matching arguments

#### Scenario: Umount CLI main calls tyro
- **WHEN** `main()` is called
- **THEN** `tyro.cli(Umount)` SHALL be invoked

### Requirement: Workspace snapshot CLI entry point
`psi-workspace-snapshot` CLI SHALL correctly create config and call the snapshot API.

#### Scenario: Snapshot CLI creates correct config
- **WHEN** `Snapshot(input_file="/tmp/in", mount_point="/tmp/mnt", tag="v2")` is called
- **THEN** the correct `snapshot()` API SHALL be called with matching arguments

#### Scenario: Snapshot CLI main calls tyro
- **WHEN** `main()` is called
- **THEN** `tyro.cli(Snapshot)` SHALL be invoked
