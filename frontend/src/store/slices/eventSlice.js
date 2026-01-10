import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
});

export const fetchEvents = createAsyncThunk('events/fetchAll', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/events/`, { ...getAuthHeader(), params });
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch events');
  }
});

export const fetchEventById = createAsyncThunk('events/fetchById', async (id, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/events/${id}/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch event');
  }
});

export const registerForEvent = createAsyncThunk('events/register', async (eventId, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/events/${eventId}/register/`, {}, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to register for event');
  }
});

const initialState = {
  events: [],
  currentEvent: null,
  loading: false,
  error: null,
};

const eventSlice = createSlice({
  name: 'events',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchEvents.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchEvents.fulfilled, (state, action) => {
        state.loading = false;
        state.events = action.payload.results || action.payload;
      })
      .addCase(fetchEvents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchEventById.fulfilled, (state, action) => {
        state.currentEvent = action.payload;
      });
  },
});

export const { clearError: clearEventError } = eventSlice.actions;
export default eventSlice.reducer;
