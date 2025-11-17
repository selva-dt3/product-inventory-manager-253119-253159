import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "../App";

// Mock API module
jest.mock("../api/client", () => {
  const actual = jest.requireActual("../api/client");
  return {
    ...actual,
    ProductsAPI: {
      list: jest.fn().mockResolvedValue([]),
      create: jest.fn().mockResolvedValue({}),
      update: jest.fn().mockResolvedValue({}),
      remove: jest.fn().mockResolvedValue({}),
      uploadImage: jest.fn().mockResolvedValue({}),
      deleteImage: jest.fn().mockResolvedValue({}),
      get: jest.fn().mockResolvedValue({}),
    },
  };
});

describe("App UI", () => {
  test("renders title and can open create form", async () => {
    render(<App />);
    expect(screen.getByText(/Product Inventory Manager/i)).toBeInTheDocument();
    const addBtn = screen.getByText(/\+ Add Product/i);
    fireEvent.click(addBtn);
    expect(screen.getByLabelText(/Add Product/i)).toBeInTheDocument();
  });

  test("theme toggle toggles label", () => {
    render(<App />);
    const toggle = screen.getByRole("button", { name: /Switch to dark mode/i });
    fireEvent.click(toggle);
    expect(screen.getByRole("button", { name: /Switch to light mode/i })).toBeInTheDocument();
  });
});
