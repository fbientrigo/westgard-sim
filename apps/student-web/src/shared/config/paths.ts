const DEFAULT_BASE = "/";

export function normalizeBasePath(baseUrl: string | undefined): string {
  const value = baseUrl?.trim() || DEFAULT_BASE;
  if (value === "/") {
    return "/";
  }
  return value.endsWith("/") ? value : `${value}/`;
}

export function buildAssetPath(relativePath: string, baseUrl?: string): string {
  const base = normalizeBasePath(baseUrl ?? import.meta.env.BASE_URL);
  const normalizedRelative = relativePath.replace(/^\/+/, "");
  if (base === "/") {
    return `/${normalizedRelative}`;
  }
  return `${base}${normalizedRelative}`;
}
