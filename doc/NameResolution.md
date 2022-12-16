# Name Resolution

After creating a simple AST for each source file using the parser, the next
step in processing is typically to (optionally) create type declarations
and resolve symbol references. In the process of doing so, name resolution
errors may be discovered and flagged to the user.

The Zuspec parser is designed to support these operations for a variety of
clients. Some clients may work in terms of the AST. These clients will
treat simple declaration as a NOP, and resolve names to AST nodes present 
in the description.

Other clients perform special-purpose work to declare types, and will
resolve name references back to paths within client-specific data 
structures.

While it's necessary to support multiple clients, we don't want each client
to implement its own name resolver. Consequently, interface types are declared
between the core name resolver and a client.

One client that poses some challenges is an incremental resolver, such as 
is used in an IDE. During active editing, we want to resolve symbols declared
in the file against symbols declared by other files. In this case, the 
resolver client maintains the state of the symbol table, excepting that 
of the active file.

The NameResolver and Client interact in terms of a set of data structures:
- Symbol    - Entity that does not act as a type namespace (field, method, etc)
  - Has a 'kind'
- Namespace - Type namespace (eg package)
  - Has a 'kind', but currently only one
- TypeDecl  - Type declaration that may hold symbols and acts as a type namespace
  - Has a 'kind'

We want the name resolver to ask relatively simple things of the client:
- Find a named symbol in the global scope
- Find a named symbol in a specified scope context
- Define a new TypeDecl inside a namespace


# Perhaps a simpler approach...

- Single name resolver that works with a symbol table
- Symbol table maintains lookup information
  - Holds dynamically-created types (template specializations)
- RefTarget holds navigation instructions on how to reach the target



We have
- Named scopes with an associated AST node (Type, some Package)
- Named scopes without an associated AST node (some Package)
- Unnamed scopes with semantic meaning (some activity, some function)

Think we only need to visit anonymous scopes once during resolution since
declarations are order-dependent.

Need a way to navigate scopes search path. Notion of a 'cursor'.
- Notion of bottom-up and top-down scopes
- What instructions can we provide?
- What do those instructions assume, in terms of an aggregate structure?
  - Always step down from root <root>.<idx1>.<idx2>

- Let's say we smash all ASTs together. This provides us a unified address space.
- Let's call this a 'cannonical' AST
  - Unified and elaborated package namespaces
  - 

Let's say we perform per-file checking 


# Name Resolution Steps
- Build a symbol-table tree from declarations. Collect imports at the same time
- Apply type extensions
  - Resolve package-level import references
  - Resolve extend targets
- Resolve remaining names
