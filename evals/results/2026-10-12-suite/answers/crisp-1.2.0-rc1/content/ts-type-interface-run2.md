Use `interface` for object shapes and class contracts. Use `type` for everything else, such as unions, tuples, primitives, and mapped or conditional types. For plain object shapes, both work almost the same.

## Differences

1. **Declaration merging.** Two interfaces with the same name merge into one. Two type aliases with the same name cause a "Duplicate identifier" error.

```ts
interface User { name: string }
interface User { age: number }   // merges: User has name and age

type Point = { x: number }
type Point = { y: number }       // error: Duplicate identifier 'Point'
```

2. **Extending.** Interfaces use `extends`. Types use the `&` intersection operator.

```ts
interface Admin extends User { role: string }
type AdminT = User & { role: string }
```

3. **Conflict handling.** If a property has incompatible types, `extends` reports an error. An intersection does not report it. The property silently becomes `never`.

4. **What each can describe.** An interface can describe only object shapes, including callable objects. A type alias can name any type.

```ts
type ID = string | number                    // union
type Pair = [string, number]                 // tuple
type Name = string                           // primitive alias
type Keys = keyof User                       // keyof
type Flags<T> = { [K in keyof T]: boolean }  // mapped
type Unwrap<T> = T extends Promise<infer U> ? U : T  // conditional
```

5. **Classes.** A class can `implement` an interface. It can also implement a type alias, but only if the alias is an object type, not a union.

6. **Index signatures.** A type alias of an object is assignable to `Record<string, unknown>`. An interface is not. This can matter when you pass an interface to a function that expects a dictionary.

7. **Performance and messages.** The compiler caches interface relationships, so large codebases with deep `extends` chains can check faster. Hover text and error messages also show the interface name instead of an expanded structure.

## When to use each

- Use `interface` for public object shapes, library APIs, and class contracts. Merging lets other code augment them, for example when you add fields to a third-party type.
- Use `type` for unions, tuples, function types, mapped types, conditional types, and aliases of primitives.
- If you need declaration merging, you must use `interface`.
- If you need a union, you must use `type`.
- If neither need applies, pick one and stay consistent across the project. Many teams default to `interface` for objects and `type` for the rest.
