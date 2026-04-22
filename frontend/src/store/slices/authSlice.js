import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Helper: extract admin role from user object returned by API
export const extractAdminRole = (user) => {
  if (!user) return null;
  if (user.is_superuser) return 'super';
  return user.admin_role || null; // 'block' | 'district' | 'state' | 'super' | null
};

// Async thunks
export const login = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/auth/login/`, credentials);
    const { access, refresh } = response.data;
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Login failed');
  }
});

export const register = createAsyncThunk('auth/register', async (userData, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/auth/register/`, userData);
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Registration failed');
  }
});

export const fetchCurrentUser = createAsyncThunk('auth/fetchCurrentUser', async (_, { rejectWithValue }) => {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await axios.get(`${API_URL}/auth/profile/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch user');
  }
});

export const logout = createAsyncThunk('auth/logout', async () => {
  try {
    const token = localStorage.getItem('refreshToken');
    await axios.post(`${API_URL}/auth/logout/`, { refresh_token: token });
  } catch (error) {
    // Ignore logout errors
  } finally {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }
});

export const resetPasswordRequest = createAsyncThunk('auth/resetPasswordRequest', async (email, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/auth/password/reset/`, { email });
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to send reset email');
  }
});

export const resetPasswordConfirm = createAsyncThunk('auth/resetPasswordConfirm', async (data, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/auth/password/reset/confirm/`, data);
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to reset password');
  }
});

const initialState = {
  user: null,
  token: localStorage.getItem('accessToken'),
  isAuthenticated: !!localStorage.getItem('accessToken'),
  adminRole: null, // 'block' | 'district' | 'state' | 'super' | null
  loading: false,
  error: null,
  successMessage: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access;
        state.user = action.payload.user;
        state.adminRole = extractAdminRole(action.payload.user);
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
        state.adminRole = extractAdminRole(action.payload);
        state.isAuthenticated = true;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.adminRole = null;
      })
      .addCase(resetPasswordRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.successMessage = null;
      })
      .addCase(resetPasswordRequest.fulfilled, (state) => {
        state.loading = false;
        state.successMessage = 'Password reset email sent. Check your inbox.';
      })
      .addCase(resetPasswordRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(resetPasswordConfirm.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.successMessage = null;
      })
      .addCase(resetPasswordConfirm.fulfilled, (state) => {
        state.loading = false;
        state.successMessage = 'Password reset successful. You can now log in.';
      })
      .addCase(resetPasswordConfirm.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
