# Development Log

## Prelude (October 10-12, 2025)
Summary of what happened so far:
- On Oct. 10th, I discussed with **ChatGPT5.0** about the features and structure of the project.
  - We've decided it would be best to build the compiler in `Python` for now (rather
    than with `flex` and `bison`).
  - To allow for running in "debug" mode (Step-by-step runner), we decided to compile into an
    **Intermediate Representation (IR)** on the compiler *frontend*, which will simply be a classic
    turing machine definition, then transform that into a **Bytecode** (in the *backend*) which
    would be **interpreted** by a `C++` runtime module.
  - Later on, we can transform the *backend* into one that emits `C/C++` code instead for
    performance and straight execution, or change the **Bytecode** approach into a
    **Resumable C/C++** approach.
  - There was also some discussion about and *alternative syntax* which defines a turing machine
    by the **classic definition** rather than the modular (Building blocks) approach, and an
    alternative compiler *frontend* for that, as well as an alternative **IR** composed of the
    modular building blocks for efficiency when the machine is not being debugged.


- On october 11th and 12th, I defined the moduler language `TMLang`, had to do a bunch of
  installations and corrections, and learned about `PLY` for my python compiler.


## October 13th, 2025
### General
- Had some fun time with ``gtksourceview`` (Not really it was abysmal - not doing that again for a while).

### Compiler/Lexer
- Implemented the basic token recognition (The tough mechanisms are left for tomorrow).
- Decided to implement *indentation based scoping* (`if/else` statements, instead of pure-assembly style).
- Need to decide on **post-processing** vs. **in-processing** approach for `INDENT`, `DEDENT` generation.
- Also, need to figure out a way to avoid generating `INDENT` and `DEDENT` when near a `label` type token.


## October 14th, 2025
### Compiler/Lexer
- Decided to use **in-processing** for indentation management in the lexer, since `PLY` returns
  a generator instance which is iterated, hence making the process suitable for extension.
- To handle **labels**, the Lexer can utilize a **lookahead** type approach - Before yielding
  the custom `INDENT` or `DEDENT` tokens, they are cached in some **queue** which is dumped
  when the decision is made.

  This approach can also be used for empty lines w/ indentations inside them.
- Implementation of the lexer is yet to be finished - I need to be more decisive in my implementation
  methods, so I can generate more code, rather than constantly worrying about design and what is
  most correct.


## October 15th, 2025
### General
- Learned about Python's **Exception Hierarchy** and custom exception definition (properly).
- Learned about how **MRO** and `super()` are defined in python in cases of multiple inheritance.

### Compiler/Lexer
- Consider **exposing the Lexer's `indent_char` parameter** so it can be set by calling user.
- Realized indentation support is complex - There could also be inconsistencies with indentation
  levels and custom exceptions are needed - Did not finish implementation.
- Added a bunch of TODOs, most of them for things that need to update when I add column tracking
  for tokens.
- I need to eventually refactor the `compiler/lexer.py` file.


## October 16th, 2025
### General
- Read about design patterns for splitting the lexer class into a `PLY` specification and added
  utilities versus a whitespace token manager (the main lexer).

### Compiler/Lexer
- Finished (to some extent) the lexer implementation.
  - Separated the errors into a new file, and the class into two parts: The **PLY integration** in
    `_PLY_Lexer_Facade` and the **indentation/whitespace management** in `TMLexer`. Packaged everything
    into a package called `lexer`.
  - Implemented **column tracking** (Count starts with 1).
- Left to do:
  - Add doc, `t_error`, and whitespace filtering to the main `TMLexer` class.<break>
    Details can be found in a `TODO` on the class doc.
  - Testing for the Lexer.
  - Some added refactory. Mainly need to decide if the Facade should be private or not.


## October 17th, 2025
### Compiler/Lexer
- Finished the lexer implementation.
  - Added documentation on classes / methods.
  - Decided to **ignore all whitespace** that is not relevant to indentation in `_PLYLexerFacade`.
- Left to do:
  - Testing for the Lexer.
  - Maybe some refactoring.


## October 18th, 2025
### Compiler/Lexer
#### Testing
- Started developing tests using ``pytest``. This can be a bit more complicated than expected.
  This is because the inputs are entire program, and the outputs are sequences of tokens, I
  cannot simply define the input and expected output, as the expected outputs can be
  significantly larger than the inputs.


- To combat this, ChatGPT suggested the ***Golden-File*** approach:
  - When encountering a new input, instead of testing the generated output against an existing
    expected output, the test will just generate and save the output into a *"golden-file"* that
    can and will be manually checked.
  - Later on, when retesting, we can compare the result to the previously generated golden file,
    or choose to update it if the Lexer underwent significant changes.


- By choosing this mechanism, the following features are required.
  - Token management (filtering values, dumping lists of tokens into files and reading them).
  - Some file management (Backing up old golden files in case of accidental overwrite).
  - Optionally, some utilities for inspecting differences between outputs.
  - Metadata file processing.

#### Other Notes
- Today I will commit all updated files except for the testing files, as they are in a very
  early stage:
  - Apart from this file, the `PLYLexerFacade` became public (for testing).
    
    I still think some renaming needs to happen.
- Read a bit about `pytest` and installed it.
- I did other stuff (Was here for 8 hrs) but I don't remember :') .


## October 19th, 2025
### General
- Moved the project code (`compiler/`) into a `src/` directory for separation.
- Moved some code that is useful for the compiler implementation *and* for testing into a new
  package `compiler/utils`.
  - These utilities are placed under `src/` because they hold simple code that is used both in
    `src/` and `test/`, and since `test/compiler/` is naturally dependent on `src/compiler/`,
    this placement does not increase cross-package coupling.
  - If I later choose to add **development tools**, those should be placed under a separate
    directory from `src/` and `test/`

### Compiler/Lexer Testing
- Started developing a token-wrapper class which is created from original `PLY` tokens and
  adds on top of them some capabilities (like natural member access, but also comparisons 
  and ignored values management).
  - Initially, I had high capabilities for this class, such as managing its own dumping
    and loading process, but it turns out this was a bad idea, because the method of dumping
    or loading can change over time, and it is mostly dependent on what the code that writes
    to or reads from file wants to do.
    
    In other words, **It is not the wrappers responsibility!** Therefore, I backed away from
    this approach and implemented bare-bones utilities.
    

## October 20th, 2025
### Compiler/Lexer Testing
Super tired today, so I did not implement anything, however I thought of a couple of problems
related to the design of the testing utilities components:<br>

- There is an issue of determining the *type* of the value of a token when it is loaded from
  a dump-file, as the value is always loaded as a string.<br><br>
  
  - One non-clean way to do this is to determine the value-type using the token's type attribute
    in some separate method. This is not clean in my opinion as this forces the determining method
    to be changed when the lexer changes (High coupling).<br><br>

  - Another slightly cleaner way of solving this is using a **Class Hierarchy** of tokens where
    each node in the hierarchy supports a specific method of determining the token's value.<br><br>
    
    This approach allows distribution of value type logic across a class hierarchy, but requires
    us to maintain the hierarchy which could be cumbersome.<br><br>

  - The cleanest approach I found was to **write the value-type to the file**, as it is known
    on write, and this information can be used on subsequent reads.<br><br>
  
    The only downside of such an approach is that it makes the files themselves less readable
    on manual reviews. One way of tackling this is to separate the written information into
    multiple files, but this requires added development of manual review tools.<br><br>

- Another issue has to do with file manager implementation - We know that later in the project
  we would like to generate files containing the AST, IR and Bytecode for both testing and
  executing a program on the runtime. Therefore, in order to avoid code duplication, we need
  to think how this logic can fit into those types of writes as well.<br><br>
  
  The file management logic can differ by the type of object being dumped and loaded, but also
  potentially by the type and format of the file.<br><br>

  - To allow for different object to be processed by the same file management logic, a **Mixin**
    (or a **Protocol**) interface can be implemented, enforcing any dumpable object to implement
    read/write methods, and the file management logic can invoke these methods.<br><br>
  
    While this approach seems perfectly valid, the issue of **object referencing** should still
    be tackled - If we wish to write an AST or an IR into a file, each element being written can
    have *references* to other elements being written, and so the file management logic has to
    handle reading and writing references like this.<br><br>
    
    A simple approach to do this involves transforming each reference into a **line number**,
    but this concept should still be developed.<br><br>
    
    A more pressing issue is that some objects **do not require this logic to be written**.
    The **Interface Segregation Principle** requires that objects do not rely on interfaces
    they do not use, hence careful design of the interface (Mixin) above should be taken.
    

## October 22nd, 2025
### Compiler/Lexer Testing
Did not implement a lot, but thought about the file-management utility at a larget scope; I want
this utility to be useful down the road as well, allowing to easily read and write other types
of data into files, and also allowing a friendly user view for manual reviews.

The thing is - While `tabulate` seems like a fine solution for now, it has a lot of issues making
it much less robust. One issue it has is lacking an ability to deal with delimiter characters in
fields (Whitespace or '|') while keeping the view simple for manual review. Another problem has to
do with referencing - Tables are known to be not ideal for such data.

To allow for a much more robust storage method, I am considering using the JSON file format, with
some specification as to how to determine what kind of data are we looking at. This approach fits
the read/write requirements much better, but has the glaring downside of no support for manual
review.

So, after discussing this with ChatGPT, we've come to the conclusion that JSON storage is ideal,
but for manual reviews an external tool should be implemented for each case.

So, the to-do list for this:
- Making JSON storage module:
  - Need to decide on a schema that fits my file types.
  - Need to decide on an architecture to fit this schema - How to cleanly generate it from raw
    output, and load into it from a file.
- External tooling for manual review:
  - Keep this ***very simple***.
  - Implement just for tokens with `tabulate`, `tempfile` and opening a subprocess.
    - Potentially, you may add cleanup and modification abilities to this tool.
    

## November 5th, 2025
### Compiler/Lexer Testing
Finished implementing and refactoring (multiple times) the testing file with fixtures,
parametrization, and some utilities:
- Defined a `Schema` class hierarchy which uses `dataclass` and a mixin I defined to define
  a structure for any JSON file. Currently, this is mostly used for golden files generated by
  the testing infrastructure.
  <br><br>
  - This caused me to define a `pyproject.toml` file which defines dependencies and project
    attributes, which is managed by `Poetry`, and a special file `src/bootstrap.py` which reads
    these attributes into environment variables for the sake of automatically initializing
    contents of these schema (for example, the project's version is automatically read from
    the project definition into any schema).
  <br><br>
- Defined a `FileManager` hierarchy - Each subclass defines mechanisms to read/write **different
  kinds** of files, and the base class and some of its children vary by a **generic type** defining
  the input/output object for read/write operations.
  <br><br>
  - The `GoldenFileManager` class is currently the only one that interacts with `schemas`, and is
    implemented using `jsonpickle`.
  <br><br>
- There is another utility class called `LazyMetadata` which uses caching to lazily-load and
  compute values from the testing metadata file. This was implemented because of how `pytest`
  works - mainly that it **collects tests first, and evaluates fixtures only when they're 
  needed**, hence there cannot be a fixture that reads the file and leads to parametrization.
  



