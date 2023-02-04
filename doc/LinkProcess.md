
Several steps are involved in linking references in a PSS description to their
references. These steps must be interleaved with evaluating code conditionals
and apply type extension.

## 1.) Collect Declarations
Each type declaration scope (eg package, component) is given a symbol scope,
and declarations within that scope are registered with the scope symbol
table.

## 2.) Apply specialization-independent type extension
Symbol resolution for type-extension statements that do not target type
specializations is performed. The impact of this type resolution
must be observed in all specializations of a given type, so must be
performed prior to specialization.

## 3.) Resolve Type Names
Resolve type references at the type level:
- Base class names
- Field type names

Both of these may cause template types to be specialized

## 3.5) Template Types
A template type is a copy of the base type with parameter references
resolved to the specialized values of the template parameters instead
of the abstract parameters of the parameter list.

- The template type has its own location in the type hierarchy
  - Type
    - Specializations
      - Specialization
- Create a parameter declaration list with proper values filled in
- Push the new type onto the resolution stack as normal
- As features are copied into the new type, re-run name resolution
  so that they are bound to the appropriate parameter+value if they
  are template references
- Rerun name resolution with 


## 4.) Resolve names in local scopes
Resolve name references in:
- Constraint blocks
- Activity blocks
- Exec blocks
- Functions

Resolving these names may also result in template types being specialized

## 5.) 


Linking of specialized template types is performed as a single step.
The type is linked using a pre-specialized parameter declaration with


Ref resolution occurs up a pre-loaded stack of possibilities. Visitors know
how to handle each of the scope types -- for example, searching in
scope-specific areas.