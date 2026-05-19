# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-05-19

### Added

- Preflight check (if directories are writable)
- Endpoint for Docker container health check

### Fixed


### Changed

- `settings.toml` is now only "build related". Configurable variables are envvars (changeble in compose file).
- Images are not served from `static/` anymore; they are served from `data/` instead.
- Random image endpoint now always invalidates cache.

### Removed


## [1.0.3] - 2026-05-14

### Added


### Fixed


### Changed

- SELinux related changes to compose file 
- `./config.toml` is now located at `./config/config.toml`

### Removed

## [1.0.2] - 2026-05-14

### Added


### Fixed

- Fixed bind mounts in compose files

### Changed


### Removed

## [1.0.1] - 2026-05-14

### Added


### Fixed

- Added `metadata.py` to repository (was accidently ignored)

### Changed


### Removed

## [1.0.0] - 2026-05-14

### Added

- Initial release

### Fixed


### Changed


### Removed


