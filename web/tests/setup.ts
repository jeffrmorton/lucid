import '@testing-library/jest-dom/vitest';

// Polyfill ResizeObserver for jsdom (needed by react-resizable-panels)
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (typeof globalThis.ResizeObserver === 'undefined') {
  globalThis.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
}
