import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
});

export const fetchMembers = createAsyncThunk('members/fetchAll', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/members/`, { ...getAuthHeader(), params });
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch members');
  }
});

export const fetchMemberProfile = createAsyncThunk('members/fetchProfile', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/members/profile/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch profile');
  }
});

export const updateMemberProfile = createAsyncThunk('members/updateProfile', async (data, { rejectWithValue }) => {
  try {
    const response = await axios.put(`${API_URL}/members/profile/`, data, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to update profile');
  }
});

export const fetchMemberById = createAsyncThunk('members/fetchById', async (id, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/members/${id}/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch member');
  }
});

const initialState = {
  members: [],
  profile: null,
  currentMember: null,
  totalCount: 0,
  loading: false,
  error: null,
};

const memberSlice = createSlice({
  name: 'members',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMembers.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchMembers.fulfilled, (state, action) => {
        state.loading = false;
        state.members = action.payload.results || action.payload;
        state.totalCount = action.payload.count || action.payload.length;
      })
      .addCase(fetchMembers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchMemberProfile.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchMemberProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(fetchMemberProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(updateMemberProfile.fulfilled, (state, action) => {
        state.profile = action.payload;
      })
      .addCase(fetchMemberById.fulfilled, (state, action) => {
        state.currentMember = action.payload;
      });
  },
});

export const { clearError } = memberSlice.actions;
export default memberSlice.reducer;
