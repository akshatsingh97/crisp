Use `interface` for object shapes that other code extends or implements. Use `type` for everything else, such as unions, tuples, and computed types. For plain object shapes, both work and you can pick one and stay consistent.

## Differences

- **Shapes:** Both describe objects, and both can describe function signatures.
- **Unions, tuples, primitives:** Only `type` can name these. An `interface` cannot.
- **Computed types:** Only `type` supports mapped, conditional, and template literal types.
- **Declaration merging:** Two `interface` declarations with the same name merge into one. Two `type` aliases with the same name cause an error.
- **Extending:** An `interface` uses `extends`. A `type` uses intersection with `&`.
- **Conflicts:** If an `interface` extends a type with an incompatible property, TypeScript reports an error. An intersection does not report it. The property silently becomes `never`.
- **Classes:** A class can `implement` either one, if it describes a single object shape. It cannot implement a union.
- **Performance and errors:** Interfaces cache better in large codebases. Their error messages often show the name instead of an expanded structure.

## Examples

```ts
// Only type can do these
type ID = string | number;
type Point = [number, number];
type Status = "idle" | "loading" | "done";
type Readonly<T> = { readonly [K in keyof T]: T[K] };

// Declaration merging works only with interface
interface Window {
  myPlugin: () => void;
}

// Extending
interface Animal { name: string }
interface Dog extends Animal { breed: string }

type Cat = Animal & { lives: number };
```

## When to use each

Use `interface` when:
- You define an object shape for a public API or library. Consumers can then extend or merge it.
- You need declaration merging, for example to augment a global or third-party type.
- A class will implement the shape.
- You build a deep hierarchy with `extends`.

Use `type` when:
- You need a union, tuple, or primitive alias.
- You need mapped, conditional, or template literal types.
- You want to block accidental merging.
- You combine or transform other types, for example with `Pick`, `Omit`, or `ReturnType`.

If your team has a style rule, follow it. A common rule is to default to `interface` for objects and use `type` when `interface` cannot express the shape.
