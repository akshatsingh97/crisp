Use `interface` for object shapes that other code will extend or implement. Use `type` for everything else, such as unions, tuples, and computed types. For plain object shapes, both work, and the choice is mostly style.

Differences:

- Declaration merging: Two `interface` declarations with the same name merge into one. A `type` alias with a repeated name is an error.
- Extending: An `interface` uses `extends`. A `type` uses intersection (`&`).
- Unions, primitives, and tuples: Only `type` can name these.
- Mapped and conditional types: Only `type` can define these.
- Classes: A class can `implements` either one, if the shape is an object type.
- Error messages: `interface` names often show up clearer in errors and hovers. Large intersections of `type` aliases can be harder to read.

```ts
// Both describe an object
interface User { id: number; name: string }
type UserT = { id: number; name: string }

// Extending
interface Admin extends User { role: "admin" }
type AdminT = UserT & { role: "admin" }

// Declaration merging (interface only)
interface Window { myPlugin: string }

// type only
type Id = string | number
type Point = [number, number]
type Keys = keyof User
type Nullable<T> = T | null
```

When to use each:

1. Use `interface` for public object shapes, class contracts, and library types that users may need to augment.
2. Use `type` for unions, tuples, function types, mapped types, conditional types, and aliases of primitives.
3. If your team already has a convention, follow it. Consistency matters more than the choice.

Watch for one risk. Declaration merging can silently change an `interface` if another file declares the same name. This is useful for augmenting global or library types. It can also cause surprises in large codebases.
