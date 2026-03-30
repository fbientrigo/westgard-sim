export class ApiError extends Error {
  readonly status?: number;
  readonly statusText?: string;
  readonly path: string;

  constructor(message: string, path: string, status?: number, statusText?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.statusText = statusText;
    this.path = path;
  }
}

export async function fetchJson(path: string): Promise<unknown> {
  const response = await fetch(path, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiError(
      `No se pudo cargar ${path}`,
      path,
      response.status,
      response.statusText,
    );
  }

  return response.json();
}
