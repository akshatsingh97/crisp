Use `interface` for object shapes that other code can extend. Use `type` for everything else, such as unions and tuples. For a plain object shape, both work almost the same.

```ts
interface User { id: number; name: string }
interface Admin extends User { role: "admin" }

type Id = string | number;                  // union
type Pair = [string, number];               // tuple
type AdminUser = User & { role: "admin" };  // intersection
```

Differences:

- An interface can only describe an object, function, or class shape. A type alias can name any type, including unions, tuples, and primitives.
- Two interfaces with the same name merge into one. Two type aliases with the same name cause an error.
- Interfaces extend with `extends`. Types combine with `&`, an intersection that merges two types.
- Only type aliases can use mapped types and conditional types.
- A class can `implement` either one, except a type that is a union.
- Interfaces often give shorter error messages. Large `extends` chains can also type-check faster than `&` chains.

Declaration merging is a risk. If you reuse an interface name by accident, TypeScript merges both declarations without a warning.

How to choose:

1. If you need a union, tuple, primitive alias, or mapped or conditional type, use `type`.
2. If you define a public API or a class contract that others will extend, use `interface`.
3. For everything else, pick one and use it consistently across the codebase.
