import backend from "@oasira-matter/backend/package.json" with {
  type: "json",
};
import common from "@oasira-matter/common/package.json" with {
  type: "json",
};
import { mapValues, pickBy } from "lodash-es";
import { describe, expect, it } from "vitest";
import own from "../package.json" with { type: "json" };

describe("oasira-matter", () => {
  it("should include all necessary dependencies", () => {
    const expected = pickBy(
      { ...backend.dependencies, ...common.dependencies },
      (_, key) => !key.startsWith("@oasira-matter/"),
    );
    expect(own.dependencies).toEqual(expected);
  });

  it("should pin all dependencies", () => {
    const expected = mapValues(own.dependencies, (value) =>
      value.replace(/^\D+/, ""),
    );
    expect(own.dependencies).toEqual(expected);
  });
});
