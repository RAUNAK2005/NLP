import { describe, expect, it } from "vitest";
import { pct, scoreLabel } from "./format";

describe("format helpers", () => {
  it("formats similarity scores as percentages", () => {
    expect(pct(0.824)).toBe("82.4%");
  });

  it("labels composite scores", () => {
    expect(scoreLabel(90)).toBe("Excellent");
    expect(scoreLabel(72)).toBe("Good");
    expect(scoreLabel(58)).toBe("Moderate");
    expect(scoreLabel(40)).toBe("Needs Review");
  });
});

