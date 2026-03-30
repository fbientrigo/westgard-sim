import { render, screen, waitFor } from "@testing-library/react";
import { HomePage } from "@/pages/HomePage";
import * as studentApi from "@/shared/api/studentDataApi";

vi.mock("@/shared/api/studentDataApi", async () => {
  const original = await vi.importActual<typeof studentApi>("@/shared/api/studentDataApi");
  return {
    ...original,
    listExperiments: vi.fn(),
  };
});

describe("HomePage states", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders empty state when no experiments", async () => {
    vi.mocked(studentApi.listExperiments).mockResolvedValueOnce({ experiments: [] });
    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText(/Sin datos/i)).toBeInTheDocument();
    });
  });

  it("renders error state when fetch fails", async () => {
    vi.mocked(studentApi.listExperiments).mockRejectedValueOnce(new Error("boom"));
    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText(/Error de carga/i)).toBeInTheDocument();
    });
  });
});
