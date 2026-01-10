import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
});

export const fetchNotifications = createAsyncThunk('notifications/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/notifications/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch notifications');
  }
});

export const markNotificationRead = createAsyncThunk('notifications/markRead', async (id, { rejectWithValue }) => {
  try {
    await axios.patch(`${API_URL}/notifications/${id}/read/`, {}, getAuthHeader());
    return id;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to mark as read');
  }
});

const initialState = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
};

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    addNotification: (state, action) => {
      state.notifications.unshift(action.payload);
      state.unreadCount += 1;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNotifications.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.loading = false;
        state.notifications = action.payload.results || action.payload;
        state.unreadCount = state.notifications.filter((n) => !n.is_read).length;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(markNotificationRead.fulfilled, (state, action) => {
        const notification = state.notifications.find((n) => n.id === action.payload);
        if (notification && !notification.is_read) {
          notification.is_read = true;
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
      });
  },
});

export const { clearError, addNotification } = notificationSlice.actions;
export default notificationSlice.reducer;
