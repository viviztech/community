import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
});

export const fetchMembershipTiers = createAsyncThunk('memberships/fetchTiers', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/memberships/tiers/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch tiers');
  }
});

export const fetchMyMemberships = createAsyncThunk('memberships/fetchMy', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/memberships/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch memberships');
  }
});

export const applyForMembership = createAsyncThunk('memberships/apply', async (data, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/memberships/apply/`, data, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to apply');
  }
});

const initialState = {
  tiers: [],
  myMemberships: [],
  currentMembership: null,
  loading: false,
  error: null,
};

const membershipSlice = createSlice({
  name: 'memberships',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMembershipTiers.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchMembershipTiers.fulfilled, (state, action) => {
        state.loading = false;
        state.tiers = action.payload.results || action.payload;
      })
      .addCase(fetchMembershipTiers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchMyMemberships.fulfilled, (state, action) => {
        state.myMemberships = action.payload.results || action.payload;
        if (state.myMemberships.length > 0) {
          state.currentMembership = state.myMemberships[0];
        }
      })
      .addCase(applyForMembership.fulfilled, (state, action) => {
        state.myMemberships.push(action.payload);
      });
  },
});

export const { clearError: clearMembershipError } = membershipSlice.actions;
export default membershipSlice.reducer;
