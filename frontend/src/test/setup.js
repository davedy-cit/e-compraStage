// Mock axios globally before any module loads it
// Use a simple approach without vi.mock to avoid transform issues
const mockAxiosInstance = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    request: { use: vi.fn(), eject: vi.fn() },
    response: { use: vi.fn(), eject: vi.fn() },
  },
  create: vi.fn(() => mockAxiosInstance),
}

// Replace axios module in the module cache
vi.doMock('axios', () => ({
  default: mockAxiosInstance,
  create: vi.fn(() => mockAxiosInstance),
}))

// Also mock the services/api module since it's already loaded
vi.doMock('@/services/api', () => ({
  default: mockAxiosInstance,
}))