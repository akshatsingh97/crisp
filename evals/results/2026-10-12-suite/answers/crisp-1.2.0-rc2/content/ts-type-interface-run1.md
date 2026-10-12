Use `interface` for object shapes that other code will extend or implement. Use `type` for everything else, such as unions, tuples, and mapped types. For plain object shapes, both work, so pick one and stay consistent.

## Differences

- **Declaration merging:** Two `interface` declarations with the same name merge into one. A `type` with a repeated name is an error. Libraries use merging to let you augment their types.
- **Non-object types:** Only `type` can name a union, primitive, tuple, or function alias. It also supports mapped and conditional types.
- **Extending:** An `interface` uses `extends`. A `type` uses intersection (`&`). Both can combine shapes.
- **Conflicts:** If two extended `interface` members have incompatible types, the compiler reports an error at once. With `&`, the conflict can silently produce `never`.
- **Performance:** The compiler caches `interface` relationships by name. Deep `&` chains can be slower and give harder error messages in large codebases.
- **Classes:** A class can `implement` either one, if it is an object shape and not a union.

## Examples

```ts
// Merging: only interface
interface Window { myPlugin: string }
interface Window { version: number }  // merged

// Union, tuple, mapped: only type
type Id = string | number;
type Point = [number, number];
type Flags<T> = { [K in keyof T]: boolean };

// Extending
interface Animal { name: string }
interface Dog extends Animal { breed: string }

type Cat = Animal & { lives: number };
```

## When to use each

1. Use `interface` for public object shapes, class contracts, and library types that users may need to augment.
2. Use `type` for unions, tuples, function types, mapped types, and conditional types.
3. If your team has a style rule, follow it. Many teams use `type` everywhere. Others use `interface` for objects and `type` for the rest.

If you are unsure, start with `interface` for objects. Switch to `type` when you need a feature that only `type` supports.
