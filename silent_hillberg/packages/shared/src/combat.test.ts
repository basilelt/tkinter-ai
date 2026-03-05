import { describe, expect, it } from "vitest";
import { calculateDamage, isCriticalHit } from "./combat";

describe("combat", () => {
  it("should increase damage on headshot", () => {
    const body = calculateDamage(20, false, 5, 40);
    const head = calculateDamage(20, true, 5, 40);

    expect(head).toBeGreaterThan(body);
  });

  it("should detect critical zone", () => {
    expect(isCriticalHit(0.8)).toBe(true);
    expect(isCriticalHit(0.3)).toBe(false);
  });
});
