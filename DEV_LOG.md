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



