import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';

// Mock dependencies
vi.mock('@/actions/auth');