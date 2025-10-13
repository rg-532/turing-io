# Development Log

## Prelude
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
### Decisions
- Had some fun time with ``gtksourceview`` (Not really it was abysmal - not doing that again for a while).
- Implemented the basic token recognition (The tough mechanisms are left for tomorrow).

### Compiler/Lexer Problems
- Decided to implement *indentation based scoping* (`if/else` statements, instead of pure-assembly style).
- Need to decide on **post-processing** vs. **in-processing** approach for `INDENT`, `DEDENT` generation.
- Also, need to figure out a way to avoid generating `INDENT` and `DEDENT` when near a `label` type token.



