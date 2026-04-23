import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
});

export const fetchDashboardStats = createAsyncThunk(
  'admin/fetchStats',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/admin/dashboard/stats/`, {
        ...getAuthHeader(),
        params,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch stats');
    }
  },
);

export const fetchAdminMembers = createAsyncThunk(
  'admin/fetchMembers',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/admin/members/`, {
        ...getAuthHeader(),
        params,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch members');
    }
  },
);

export const fetchAdminApprovals = createAsyncThunk(
  'admin/fetchApprovals',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/admin/approvals/`, {
        ...getAuthHeader(),
        params,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch approvals');
    }
  },
);

export const fetchGeographicStats = createAsyncThunk(
  'admin/fetchGeographic',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/admin/geographic-stats/`, {
        ...getAuthHeader(),
        params,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch geographic stats');
    }
  },
);

export const fetchAdminAreas = createAsyncThunk(
  'admin/fetchAreas',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/admin/areas/`, getAuthHeader());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch areas');
    }
  },
);

export const fetchRevenueStats = createAsyncThunk(
  'admin/fetchRevenue',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/admin/revenue/`, getAuthHeader());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch revenue stats');
    }
  },
);

export const processApproval = createAsyncThunk(
  'admin/processApproval',
  async ({ workflowId, action, comments }, { rejectWithValue }) => {
    try {
      const response = await axios.post(
        `${API_URL}/approvals/${workflowId}/process_action/`,
        { action, comments },
        getAuthHeader(),
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to process approval');
    }
  },
);

const initialState = {
  stats: null,
  members: [],
  membersTotal: 0,
  approvals: [],
  approvalsTotal: 0,
  revenue: null,
  geographic: null,
  areas: { blocks: [], districts: [] },
  loading: false,
  error: null,
};

const adminSlice = createSlice({
  name: 'admin',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardStats.pending, (state) => { state.loading = true; })
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload;
      })
      .addCase(fetchDashboardStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchAdminMembers.fulfilled, (state, action) => {
        state.members = action.payload.results || [];
        state.membersTotal = action.payload.count || 0;
      })
      .addCase(fetchAdminApprovals.fulfilled, (state, action) => {
        state.approvals = action.payload.results || [];
        state.approvalsTotal = action.payload.count || 0;
      })
      .addCase(fetchRevenueStats.fulfilled, (state, action) => {
        state.revenue = action.payload;
      })
      .addCase(fetchGeographicStats.fulfilled, (state, action) => {
        state.geographic = action.payload;
      })
      .addCase(fetchAdminAreas.fulfilled, (state, action) => {
        state.areas = action.payload;
      });
  },
});

export const { clearError } = adminSlice.actions;
export default adminSlice.reducer;
