## 1. Setup

- [x] 1.1 Add `croniter` dependency to pyproject.toml
- [x] 1.2 Create `src/psi_agent/session/schedule.py` module

## 2. Core Implementation

- [x] 2.1 Implement `Schedule` dataclass with cron parsing
- [x] 2.2 Implement `ScheduleLoader` to scan workspace schedules directory
- [x] 2.3 Implement `ScheduleExecutor` to run tasks at scheduled times
- [x] 2.4 Integrate schedule executor with session runner

## 3. Testing

- [x] 3.1 Write unit tests for Schedule dataclass
- [x] 3.2 Write unit tests for ScheduleLoader
- [x] 3.3 Write unit tests for cron expression parsing
- [x] 3.4 Run all quality checks (format, lint, typing, test)
