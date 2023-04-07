
On declaration, a parameterized type is not so different from any other 
type -- with the exception that it has a special 'parameters' namespace
with declarations that may be later referenced.

Parameterized type declarations are ignored during the linking process
since complete linking cannot be performed until a full specialization
is known. Future implementations may perform partial linking to 
better-identify issues with the type declaration (vs a given specialization).

Type specializations are full clones of the type declaration. They are
stored in a list on the unspecialized type. Consequently, the full path
to a specialized template type contains the unspecialized template
template as well. For example:

struct S1 { } // Index 0

struct S2<type T> { } // Index 1

struct S3 { // Index 2
    S2<int>    t1;
}

The path to the type of t1 is:
<ChildIndex,1> // Unspecialized parameter type
<ParamType,0>

# Creating a Specialized Type

- The entity requiring a specific type specialization must first create a 
  ITemplateParamDeclList class that describes the desired specialization. The
  default value of each parameter shall be set to the desired value.

- Next, existing specializations are searched for the desired specialization
  in case the specialization already exists. If the specialization exists,
  it is returned.

- If the desired specialization does not exist, a new specialization will be
  created and added to the list of specializations.

  - A clone of the parameterized type is created, with the exception that the
    full parameter list is used instead of the default, unspecialized one.
  - The linker is run on the new type. The link context must be the 
    newly-specialized type in order to allow the linker to find referenced
    type parameters.
  - Because the linker only runs on a specialized type, it can always assume
    that it should traverse type-parameter declarations to resolve their
    targets.

