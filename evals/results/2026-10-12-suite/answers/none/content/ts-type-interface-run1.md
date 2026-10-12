Use `interface` for object shapes that other code may extend. Use `type` for everything else. For plain object shapes, the two behave almost the same.

**What only `type` can do**
- Name unions: `type Id = string | number`
- Name primitives, tuples, and function types: `type Pair = [string, number]`
- Use mapped and conditional types: `type Readonly2<T> = { readonly [K in keyof T]: T[K] }`

**What only `interface` can do**
- Merge declarations. Two `interface User` blocks in the same scope combine into one. A second `type User` is an error.
- Extend with `extends`. The compiler checks the extension and reports a clear error on conflicts. Intersections (`&`) with `type` are less strict and can silently produce `never`.

**Other differences**
- Error messages and hover text often show `interface` names more clearly. A `type` alias may expand into its full structure.
- A class can `implements` either one, as long as the type is an object shape. It cannot implement a union.
- Interfaces are usually a little faster for the compiler to check in large codebases. The gap rarely matters.

**Rules of thumb**
1. Public object shapes, such as library APIs and classes that others extend: use `interface`. Declaration merging lets users augment them.
2. Unions, tuples, primitives, function types, and utility or mapped types: use `type`. `interface` cannot express them.
3. Everything else: pick one and stay consistent within the project. Check whether your linter enforces a choice, such as `@typescript-eslint/consistent-type-definitions`.

**Example**
```ts
interface Animal { name: string }
interface Dog extends Animal { breed: string }

type Status = "idle" | "loading" | "error";
type Handler = (event: Event) => void;
```
