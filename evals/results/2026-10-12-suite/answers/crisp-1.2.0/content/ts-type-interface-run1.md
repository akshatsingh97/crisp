Use `interface` for object shapes that other code extends or implements. Use `type` for everything else, such as unions, tuples, and computed types. For plain object shapes, both work, so pick one and stay consistent.

## Differences

1. Declaration merging: Two `interface` declarations with the same name merge into one. A `type` alias with a repeated name is an error.

```ts
interface User { id: number }
interface User { name: string }   // merged: { id; name }

type Point = { x: number }
type Point = { y: number }        // Error: Duplicate identifier
```

2. Extending: An interface uses `extends`. A type uses intersection (`&`).

```ts
interface Admin extends User { role: string }
type Admin2 = User & { role: string }
```

3. Conflicting members: If `extends` finds incompatible property types, TypeScript reports an error at the declaration. An intersection does not report it. The conflicting property becomes `never`, and the error appears later when you use it.

4. What each can describe: A `type` alias can name any type. An `interface` can only describe an object shape (including functions and classes).

```ts
type ID = string | number            // union
type Pair = [string, number]         // tuple
type Keys = keyof User               // computed
type Flags<T> = { [K in keyof T]: boolean }  // mapped
type Result<T> = T extends string ? "s" : "n" // conditional
```

5. Classes: A class can `implements` either one, if the type is an object shape. It cannot implement a union type.

6. Performance and errors: Interfaces cache better in the compiler, so large codebases with deep extension chains can check faster. Interface names also tend to show up more clearly in error messages.

## When to use each

- Use `interface` for public object contracts, class shapes, and library APIs that users might extend through merging.
- Use `type` for unions, tuples, primitives aliases, mapped types, conditional types, and utility-type results.
- Use `type` if you need to combine or transform other types.

## Practical rule

Pick one default and apply it across the project. Many teams default to `interface` for objects and `type` for the rest. Others use `type` everywhere. A linter rule, such as `@typescript-eslint/consistent-type-definitions`, can enforce your choice.
