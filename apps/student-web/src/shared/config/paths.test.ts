import { buildAssetPath, normalizeBasePath } from "@/shared/config/paths";

describe("paths", () => {
  it("normalizes slash handling", () => {
    expect(normalizeBasePath("/")).toBe("/");
    expect(normalizeBasePath("/repo")).toBe("/repo/");
    expect(normalizeBasePath("/repo/")).toBe("/repo/");
  });

  it("builds asset path for root base", () => {
    expect(buildAssetPath("web_data/index.json", "/")).toBe("/web_data/index.json");
  });

  it("builds asset path for repository base", () => {
    expect(buildAssetPath("web_data/index.json", "/westgard/")).toBe(
      "/westgard/web_data/index.json",
    );
  });
});
