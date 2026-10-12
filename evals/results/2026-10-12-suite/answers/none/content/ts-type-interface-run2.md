Use `interface` for object shapes that other code might extend. Use `type` for everything else. For plain object shapes, the two are almost the same.

## What differs

| | `interface` | `type` |
|---|---|---|
| Object shapes | Yes | Yes |
| Unions (`A \| B`) | No | Yes |
| Primitives, tuples, function types | Only as object members | Yes |
| Mapped and conditional types | No | Yes |
| Extend another type | `extends` | `&` (intersection) |
| Declaration merging | Yes | No |
| Implemented by a class | Yes | Yes, if it is an object type |

## Declaration merging

If you declare an interface twice with the same name, TypeScript merges the two. A `type` with a repeated name is an error.

```ts
interface User { id: string }
interface User { name: string }   // merged: User has id and name

type Point = { x: number }
type Point = { y: number }        // Error: duplicate identifier
```

Merging is why libraries use interfaces for public types. You can add fields to them, for example to extend `Window` or Express's `Request`.

## Extending

`interface extends` reports conflicting property types as an error at the declaration. An intersection with `&` does not. It silently reduces a conflicting property to `never`. Interfaces also check faster on large codebases, because TypeScript caches them by name.

```ts
interface Admin extends User { role: "admin" }
type Admin2 = User & { role: "admin" }
```

## What only `type` can do

```ts
type Id = string | number                      // union
type Pair = [string, number]                   // tuple
type Handler = (e: Event) => void              // function type
type Keys = keyof User                         // derived type
type Readonly2<T> = { readonly [K in keyof T]: T[K] }   // mapped type
type Result<T> = T extends string ? "text" : "other"    // conditional type
```

## When to use each

- **Use `interface`** for object shapes, class contracts, and public library types that users may need to extend.
- **Use `type`** for unions, tuples, function signatures, and any mapped or conditional type.
- **Pick one for plain objects and stay consistent.** Either choice works. A common rule is `interface` by default and `type` when you need its extra features.

One more difference: an `interface` has an implicit open shape, so it is not assignable to an index-signature type such as `Record<string, unknown>`. A `type` alias of an object literal is. If you hit that error, switching to `type` fixes it.
