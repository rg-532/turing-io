# Notes

## Future Ideas
### Migration of Output Files
Schemas which define output files may change overtime, which incurs version increments. There is 
enough information within the project configuration to detect outdated files (Given that they
actually have defined formats), but there is no mechanism in place to migrate them, so such a
mechanism may be desired.

Because many internal files (including outputted **Bytecode** and **C/C++ code**) can differ while
project versioning semantics hold (Meaning that minor feature additions do not break the program,
but do break testing), some mechanism to ensure that previously generated expected output files are
still relevant may be required.


### File Traceability
A suggestion I have received was to include the input files which caused generation of output files
as metadata, so source files could be traced. The issue here is that some output files may be tied
to multiple inputs and in different ways, so more thought is needed regarding how to properly track
this in a flexible way.

Since this is a future idea, it will incur **version updates** of involved schemas (and potentially
migrations).


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
checked out


### Composite File Manager
There is already an implementation of File manager which are specific to loading techniques and
generic by the data type to be read/written and bound to a specific directory. However, given that
tests may require loading input/output from multiple directories, and may vary in input/output type,
any directory+type combination mandates an appropriate, separate fixture.

Assuming we proceed with a more sophisticated metadata loading capability, which is able to specify
multiple source directory for inputs (and potential outputs), and define the type of data being loaded,
a more complex mechanism, using composition, is required.

It should be noted that such a mechanism was created and dumped due to incompatibility with generics
w.r.t. the read/write data type, so a more sophisticated approach to this is required.

Additionally, although it provides flexibility (and its cool), this idea is beyond the scope of the
necessities of this project.


