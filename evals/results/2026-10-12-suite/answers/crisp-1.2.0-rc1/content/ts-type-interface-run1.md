Use `interface` for object shapes that other code will extend or implement. Use `type` for everything else, such as unions, tuples, and computed types. For plain object shapes, both work and the choice is mostly style.

## Differences

1. Type aliases can name any type: unions, tuples, primitives, and mapped or conditional types. Interfaces can only describe object shapes.
2. Interfaces support declaration merging. Two interfaces with the same name combine into one. Two type aliases with the same name cause an error.
3. Interfaces extend with `extends`. Types combine with `&`. An interface reports conflicting property types as an error. An intersection can silently reduce to `never`.
4. Interfaces usually give faster compiles and clearer error messages. The compiler caches them by name. It must re-evaluate intersections each time.
5. A type alias of an object type is assignable to `Record<string, unknown>`. An interface is not.
6. A class can `implement` either one, if it is an object type and not a union.

```ts
// Only a type can do these
type Id = string | number;
type Point = [number, number];
type Handler = (e: Event) => void;
type Readonly2<T> = { readonly [K in keyof T]: T[K] };
type Result<T> = T extends string ? "text" : "other";

// Interface-only: declaration merging
interface Window { myPlugin: () => void }  // adds to the built-in Window

// Both work for object shapes
interface User { name: string }
interface Admin extends User { role: string }

type User2 = { name: string };
type Admin2 = User2 & { role: string };
```

## When to use each

Use `interface` when:
- You define the shape of an object or class contract.
- You write a public library API that users may extend.
- You need to augment an existing type, such as a global or a third-party module.

Use `type` when:
- You need a union, tuple, primitive alias, or function type.
- You need mapped, conditional, or other computed types.
- You want a type that is closed and cannot be merged by accident.

## Practical rule

Pick one default for object shapes and stay consistent. Many teams use `interface` for objects and `type` for the rest. The TypeScript team also suggests `interface` until you need a feature that only `type` has.
