Use `interface` for object shapes that other code will extend or implement. Use `type` for everything else, such as unions, tuples, and mapped types.

## Differences

1. Only `type` can name a union, a primitive alias, or a tuple.
2. Only `type` can express mapped types and conditional types.
3. Interfaces with the same name merge into one. Types with the same name cause an error.
4. Interfaces extend with `extends`. Types combine with `&` (an intersection).
5. Both can describe an object, and a class can implement either one.
6. For object shapes, interfaces often give clearer error messages and faster checking in large codebases.

```ts
// Only type can do these
type Id = string | number;
type Point = [number, number];
type Readonly2<T> = { readonly [K in keyof T]: T[K] };

// Interface: extension and merging
interface User { name: string }
interface Admin extends User { role: string }
interface User { email: string } // merges into User

// Type: same extension with an intersection
type Admin2 = User & { role: string };
```

## When to use each

- Use `interface` for public object shapes, class contracts, and library APIs. Declaration merging lets users augment them.
- Use `type` for unions, tuples, function types, and any computed type.
- If both work, pick one and stay consistent across the project.

Declaration merging can hide mistakes. If you accidentally reuse an interface name, TypeScript will merge the two without warning.
