# Changelog

All notable changes to tkx-compiler will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete architecture refactoring with separated modules
- Comprehensive validation system (XML, Python, paths)
- Type hints for all functions and classes
- Configuration management with .tkxrc.json support
- Environment variable support for configuration
- Project template generator
- Security improvements (path traversal protection)
- Error handling with detailed error messages
- pyproject.toml for modern Python project management
- Enhanced documentation

### Changed
- Refactored main.py to use builder pattern
- Separated PyParser into specialized modules
- Improved error messages with context
- Updated README with new features

### Removed
- Unused lua.py module
- Old pyparser.py (replaced with refactored version)

### Fixed
- Security vulnerabilities in path handling
- Import rewriting edge cases
- Dependency collection issues

## [1.0.0] - Initial Release

### Added
- XML to Python compilation
- Basic dependency collection
- Support for standard tkinter widgets
- Support for ttk widgets
- CLI interface
- Basic error handling
