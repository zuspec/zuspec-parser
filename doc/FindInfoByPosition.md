# Find Info By Position

What could we find?
What can we do with what we find?
- Is the element a type or an instance?
- Can we (meaningfully) navigate to its declaration/definition?
  - If so, where is that?
- Is a doc comment associated with the element
  - For now, we the return value doesn't say what the comment might be associated with
  - We allow the finder to prioritize between variable and declared type

/**
 * Doc Comment for C
 */
component C {
    /**
     * Doc Comment for A
     */
    action A {

    }
}

component pss_top {
    /**
     * Doc Comment for c1
     */
    C     c1;
    C     c2;

    action Entry {
        activity {
            do C::A with {comp == this.comp.c1;};
        }
    }
}

- Hovering over the field declaration of 'c1' should return
  - isInstance
  - cannotGotoDecl
  - haveDocComment (Doc Comment for c1)
- Hovering over the type C in that declaration should return
  - isType
  - canGotoDecl (component C declaration)
  - haveDocComment (Doc Comment for C)
- Hovering over 'A' in 'C::A' should return
  - isType
  - canGotoDecl (action C::A declaration)
  - haveDocComment(Doc Comment for A)
- Hovering over 'this.comp.c1'
  - isInstance
  - canGotoDecl (c1 field declaration)
  - haveDocComment (Doc Comment for c1)

