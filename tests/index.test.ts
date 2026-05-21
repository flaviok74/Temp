import { describe, it, expect } from "vitest";
import { greet } from "../src/index.js";

describe("greet", () => {
  it("returns a greeting", () => {
    expect(greet("world")).toBe("Hello, world!");
  });

  it("supports any name", () => {
    expect(greet("Claude")).toBe("Hello, Claude!");
  });
});
