# Notes

## Future Ideas
### `Typing` Migration
Simply remove most deprecated `typing` imports (List, Dict etc.) and replace them with modern 
counterparts.


### `Pydantic` Migration
This idea is two-fold:
1. Replace usage of `EmptySchema` with Pydantic implementations.
   Note that this means no more extra attributes (But I don't care too much anyway).
2. Use `Pydantic` to verify content of read JSON (non-golden) files.
   This is opposed to validating with my own function `_validate_metadata` which is ugly.

Of course, it is important to verify that Pydantic fits well to my needs and check how to repair
the current golden files to work with the new classes.


### File Traceability
A suggestion I have received was to include the input files which caused generation of output files
as metadata, so source files could be traced. The issue here is that some output files may be tied
to multiple inputs and in different ways, so more thought is needed regarding how to properly track
this in a flexible way.

Since this is a future idea, it will incur **version updates** of involved schemas (and potentially
migrations).


### Golden File Management w/ Pytest Flags
It is possible to add flags to `pytest` invocation through a terminal. An old suggestion I received
was to add a flag to remake golden files, which makes sense in a scenario where the golden file
metadata is outdated.

This, however, is not super necessary yet.


### JSON Files as Schema
Due to how flexible the schema structure is, any structured JSON(-like) file can utilize them by
having a schema defining its structure, and this can be especially useful for repeating structures.

The upsides:
- This provides access to read JSON files by member as opposed to by key.
- This provides a common interface between user-defined metadata and the code that reads it.

The downsides:
- This requires added implementation, which mandates careful thought about what structured JSON
  files there may be, for the organization of the implemented class hierarchy.

A potential structure for **test metadata files**:
- Input/Expected keys, each leading to object.
  - Keys hold a representation to a path to some test.
  - Values that hold a set of path (or globbing patterns) which lead to testing data for the tests.
- This structure can be reversed or implicit in some ways.

**Note:** Before anything, there's a plugin for data-driven testing for pytest which should be
checked out.


### Data Migrator Refactory
A tool for data migration of golden files has been implemented, but the implementation is frail
(doesn't feel very maintainable) and may need refactory.

The tool currently supplies two base commands: `scan` and `migrate`, and the CLI itself allows
for command chaining (you may invoke `data-mig scan migrate`, for example), but chaining may not
fit the implementation:
- It allows for multiple scan invocations, which seems unnecessary.
- Invoking `migrate` with `--show-only` allows to show the migration paths without executing any
  migrations, but if preceded with `scan`, it shows info about files twice, and the first set of
  files shown does not include files which are added after `migrate`.

Conversely, not utilizing chaining would mean that migration of entire directory will rely on
default suffixes supported by the underlying `scan` implementation, unless suffixes are allowed
for `migrate`, but this option is only applicable to one specific scenario.

Files to be considered for refactory:
- `data_migrator/logic/ops.py` (Provides API for the CLI commands)
- `data_migrator/cli.py` (Provides the CLI commands themselves)

Suggestion - Change the current scheme in the following way:
- Remove chaining from the base group.
- Implement the following command hierarchy:
  - `scan [-s suffix]` (multiple suffixes allowed).
  - `migrate [--show-only] [--backup/--no-backup] COMMAND`
    Command `migrate` becomes a subgroup of `data-mig`, allowing:
    - `files <file_path> [additional_file_paths]` (at least one file).
    - `dir [-s suffix]` (multiple suffixes allowed).
- Break up the `ops` layer so that it is more fine-grained and allows for modular implementation:
  - `collect_files` will use `globbing` to find all kinds of files.
  - `filter_files` will filter for files needing migration only (or other options).
  - `get/execute_file_migration` will operate similarly to before.

This approach removes confusion occurring when both `files` are specified and `scan` appears
before `migrate`, while exposing all desired APIs. Duplication will be handled through the refactory
of `ops`.


### Composite File Manager
There is already an implementation of File manager which are specific to loading techniques and
generic by the data type to be read/written and bound to a specific directory. However, given that
tests may require loading input/output from multiple directories, and may vary in input/output type,
any directory+type combination mandates an appropriate, separate fixture.

Assuming we proceed with a more sophisticated metadata loading capability, which is able to specify
multiple source directory for inputs (and potential outputs), and define the type of data being loaded,
a more complex mechanism, using composition, may be required.

It should be noted that such a mechanism was created and dumped due to incompatibility with generics
w.r.t. the read/write data type, so a more sophisticated approach to this is required.

Additionally, although it provides flexibility (and its cool), this idea is beyond the scope of the
necessities of this project.


