import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import Home from '@/app/page';

// 1. Mock the API URL environment variable
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';

describe('Home Page', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders the search input and button', () => {
    render(<Home />);
    expect(screen.getByPlaceholderText(/What are you looking for today\?/i)).toBeDefined();
    expect(screen.getByRole('button', { name: /search/i })).toBeDefined();
  });

  it('shows loading state and displays results after search', async () => {
    // 2. Mock a successful API response
    const mockProducts = [
      { id: 1, name: 'AI Laptop', description: 'Powerful for ML' }
    ];
    
    global.fetch = vi.fn().mockResolvedValue({
      json: async () => mockProducts,
    });

    render(<Home />);
    
    const input = screen.getByPlaceholderText(/What are you looking for today\?/i);
    const button = screen.getByRole('button', { name: /search/i });

    // 3. Simulate user typing and clicking search
    fireEvent.change(input, { target: { value: 'laptop' } });
    fireEvent.click(button);

    // 4. Verify loading state (Button text changes)
    expect(screen.getByText('...')).toBeDefined();

    // 5. Verify results appear on screen
    await waitFor(() => {
      expect(screen.getByText('AI Laptop')).toBeDefined();
      expect(screen.getByText('Powerful for ML')).toBeDefined();
    });
  });
});