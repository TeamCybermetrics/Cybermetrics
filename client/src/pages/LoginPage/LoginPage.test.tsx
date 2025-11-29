import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';

// Mock dependencies
vi.mock('@/actions/auth');

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderLoginPage = () => {
    return render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
  };

it('renders login page w all web elements', () => {
  renderLoginPage();
  
  expect(screen.getByText('Cybermetrics')).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument(); // ✅ Specify it's a heading
  expect(screen.getByText('Welcome back to Cybermetrics')).toBeInTheDocument();
  expect(screen.getByLabelText('Email')).toBeInTheDocument();
  expect(screen.getByLabelText('Password')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Sign up' })).toHaveAttribute('href', ROUTES.SIGNUP);
});

  it('updates email input bar when user types', async () => {
    const user = userEvent.setup();
    renderLoginPage();
    
    const emailInput = screen.getByLabelText('Email') as HTMLInputElement;
    await user.type(emailInput, 'jaela@example.com');
    
    expect(emailInput.value).toBe('jaela@example.com');
  });

  it('updates password input value when user types', async () => {
    const user = userEvent.setup();
    renderLoginPage();
    
    const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;
    await user.type(passwordInput, '123');
    
    expect(passwordInput.value).toBe('123');
  });

  it('disables form inputs while loading', async () => {
    const user = userEvent.setup();
    vi.mocked(authActions.login).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ 
        success: true,
        data: { token: 'fake-token' } as any 
      }), 100))
    );
    
    renderLoginPage();
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'jaela@example.com');
    await user.type(passwordInput, '123');
    await user.click(submitButton);
    
    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
    expect(screen.getByText('Logging in...')).toBeInTheDocument();
  });

  it('shows success message and navigates on successful login', async () => {
    const user = userEvent.setup();
    vi.mocked(authActions.login).mockResolvedValue({ 
      success: true,
      data: { token: 'fake-token' } as any
    });
    
    renderLoginPage();
    
    await user.type(screen.getByLabelText('Email'), 'test@example.com');
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Login' }));
    
    await waitFor(() => {
      expect(screen.getByText('Login successful!')).toBeInTheDocument();
    });
    
    expect(authActions.login).toHaveBeenCalledWith('test@example.com', 'password123');
  });

  it('shows error message on failed login', async () => {
    const user = userEvent.setup();
    vi.mocked(authActions.login).mockResolvedValue({ 
      success: false, 
      error: 'Invalid credentials' 
    });

    renderLoginPage();
    
    await user.type(screen.getByLabelText('Email'), 'test@example.com');
    await user.type(screen.getByLabelText('Password'), 'password');
    await user.click(screen.getByRole('button', { name: 'Login' }));
    
    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  it('shows generic error when error is undefined', async () => {
  const user = userEvent.setup();
  vi.mocked(authActions.login).mockResolvedValue({ 
    success: false
  } as any);

  renderLoginPage();
  
  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.type(screen.getByLabelText('Password'), 'password');
  await user.click(screen.getByRole('button', { name: 'Login' }));
  
  await waitFor(() => {
    expect(screen.getByText('An error occurred')).toBeInTheDocument();
  });
});

  it('prevents form submission when fields are empty', () => {
    renderLoginPage();
    
    const emailInput = screen.getByLabelText('Email') as HTMLInputElement;
    const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;
    
    expect(emailInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });

  it('clears previous errors when submitting again', async () => {
    const user = userEvent.setup();
    vi.mocked(authActions.login)
      .mockResolvedValueOnce({ success: false, error: 'First error' })
      .mockResolvedValueOnce({ success: false, error: 'Second error' });
    
    renderLoginPage();
    
    await user.type(screen.getByLabelText('Email'), 'test@example.com');
    await user.type(screen.getByLabelText('Password'), 'password');
    await user.click(screen.getByRole('button', { name: 'Login' }));
    
    await waitFor(() => {
      expect(screen.getByText('First error')).toBeInTheDocument();
    });
    
    await user.click(screen.getByRole('button', { name: 'Login' }));
    
    await waitFor(() => {
      expect(screen.queryByText('First error')).not.toBeInTheDocument();
      expect(screen.getByText('Second error')).toBeInTheDocument();
    });
  });

  it('has correct autocomplete attributes', () => {
    renderLoginPage();
    
    expect(screen.getByLabelText('Email')).toHaveAttribute('autocomplete', 'email');
    expect(screen.getByLabelText('Password')).toHaveAttribute('autocomplete', 'current-password');
  });

  it('navigates to team builder after successful login', async () => {
  const user = userEvent.setup();
  
  vi.mocked(authActions.login).mockResolvedValue({ 
    success: true,
    data: { token: 'fake-token' } as any
  });
  
  renderLoginPage();
  
  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.type(screen.getByLabelText('Password'), 'password123');
  await user.click(screen.getByRole('button', { name: 'Login' }));
  
  await waitFor(() => {
    expect(screen.getByText('Login successful!')).toBeInTheDocument();
  });
  
  // ✅ Wait for the actual 1000ms timeout + navigation
  await waitFor(() => {
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.LINEUP_CONSTRUCTOR);
  }, { timeout: 2000 }); // Give it 2 seconds to complete
});

});