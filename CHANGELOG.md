# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- 
    The following heading should be used
        - Added
        - Changed
        - Deprecated
        - Removed
        - Fixed
        - Security
 -->

## [Unreleased]

### Changed
- The min, max and sum functions are changed to accomodate single argument.

### Fixed
- Fixed unary - operator.
- Minor bug-fixes.

### Removed
- The test cases that were failing were either edited, or removed completely.



## [0.0.3]

### Added

- Ported tests from [fish-shell](https://github.com/fish-shell/fish-shell/blob/master/tests/checks/math.fish) to pytest.
- Ported examples from [math - perform mathematics calculations](https://fishshell.com/docs/current/cmds/math.html#examples) to check50 and pytest.
- Added a simple lexical analyzer (without Error handling).
- Added GitHub workflow for automated testing using pytest
- Added GitHub workflow for deploymeny to PyPI and TestPyPI
- Added Shunting yard algorithm to solve Operator precedence.
- Linked all math.* function in `known_lexemes` by default.
- Added reverse polish notation converter & solver
- Added support for base 2, 8, and 16 using `--base` flag


### Changed
- The format of `token_stream` returned by `analyzer.lexical_analyzer` is changed.
- Some tests are changed to simplify logic.

## [0.0.1]
- Setup the skeleton of MicroProjects in an extensible manner.
- Added Calculator module


<!-- Here comes the `git diff` of each version. -->
[unreleased]: https://github.com/nyx-4/MicroProjects/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/nyx-4/MicroProjects/compare/v0.0.1...v0.0.3
[0.0.1]: https://github.com/nyx-4/MicroProjects/releases/tag/v0.0.1
