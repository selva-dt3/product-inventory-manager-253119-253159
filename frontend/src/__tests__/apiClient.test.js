import { apiFetch, getApiBase, ProductsAPI, ApiError } from "../api/client";

describe("api client", () => {
  const OLD_ENV = process.env;

  beforeEach(() => {
    jest.resetAllMocks();
    process.env = { ...OLD_ENV };
    global.fetch = jest.fn();
  });

  afterAll(() => {
    process.env = OLD_ENV;
  });

  test("getApiBase uses env and trims trailing slash", () => {
    process.env.REACT_APP_API_BASE = "http://localhost:8000/";
    expect(getApiBase()).toBe("http://localhost:8000");
  });

  test("apiFetch returns json body for ok", async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: new Map([["content-type", "application/json"]]),
      json: async () => ({ status: "ok" }),
    });
    const res = await apiFetch("/health");
    expect(res).toEqual({ status: "ok" });
  });

  test("apiFetch throws ApiError on non-ok", async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      status: 404,
      headers: new Map([["content-type", "application/json"]]),
      json: async () => ({ error: { message: "Not found" } }),
    });
    await expect(apiFetch("/nope")).rejects.toBeInstanceOf(ApiError);
  });

  test("ProductsAPI.list builds query params", async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      headers: new Map([["content-type", "application/json"]]),
      json: async () => ([]),
    });
    await ProductsAPI.list({ q: "abc", limit: 10, offset: 0 });
    const url = global.fetch.mock.calls[0][0];
    expect(url).toContain("/products?q=abc&limit=10&offset=0");
  });
});
