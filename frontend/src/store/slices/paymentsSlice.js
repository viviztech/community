import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
});

export const fetchPayments = createAsyncThunk('payments/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/payments/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch payments');
  }
});

export const initiatePayment = createAsyncThunk('payments/initiate', async (paymentData, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/payments/initiate/`, paymentData, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to initiate payment');
  }
});

export const fetchReceipt = createAsyncThunk('payments/receipt', async (paymentId, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/payments/${paymentId}/receipt/`, getAuthHeader());
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data || 'Failed to fetch receipt');
  }
});

const initialState = {
  payments: [],
  currentReceipt: null,
  paymentUrl: null,
  loading: false,
  error: null,
  successMessage: null,
};

const paymentsSlice = createSlice({
  name: 'payments',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null; },
    clearSuccess: (state) => { state.successMessage = null; },
    clearPaymentUrl: (state) => { state.paymentUrl = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPayments.pending, (state) => { state.loading = true; })
      .addCase(fetchPayments.fulfilled, (state, action) => {
        state.loading = false;
        state.payments = action.payload.results || action.payload;
      })
      .addCase(fetchPayments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(initiatePayment.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(initiatePayment.fulfilled, (state, action) => {
        state.loading = false;
        state.paymentUrl = action.payload.payment_url;
        state.successMessage = 'Payment initiated. Redirecting...';
      })
      .addCase(initiatePayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchReceipt.fulfilled, (state, action) => {
        state.currentReceipt = action.payload;
      });
  },
});

export const { clearError: clearPaymentError, clearSuccess: clearPaymentSuccess, clearPaymentUrl } = paymentsSlice.actions;
export default paymentsSlice.reducer;
