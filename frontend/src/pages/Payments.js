import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
} from '@mui/material';
import {
  Payment as PaymentIcon,
  Receipt as ReceiptIcon,
  CheckCircle as CheckCircleIcon,
  Pending as PendingIcon,
} from '@mui/icons-material';
import { fetchPayments, initiatePayment, downloadReceipt } from '../store/slices/paymentsSlice';

export default function Payments() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { payments = [], loading, downloading, error, paymentUrl } = useSelector((state) => state.payments || {});
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState(null);

  useEffect(() => {
    dispatch(fetchPayments());
  }, [dispatch]);

  useEffect(() => {
    if (paymentUrl) {
      window.location.href = paymentUrl;
    }
  }, [paymentUrl]);

  const openPaymentDialog = (paymentData) => {
    setSelectedPayment(paymentData);
    setPaymentDialogOpen(true);
  };

  const handleConfirmPayment = () => {
    if (selectedPayment) {
      dispatch(initiatePayment(selectedPayment));
    }
    setPaymentDialogOpen(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'pending': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon color="success" />;
      case 'pending': return <PendingIcon color="warning" />;
      default: return <PaymentIcon />;
    }
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" fontWeight={600} gutterBottom>
          Payment History
        </Typography>
        <Typography color="text.secondary">
          View your payment transactions and receipts
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </Alert>
      )}

      {/* Payment Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <PaymentIcon color="primary" fontSize="large" />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Total Payments
                  </Typography>
                  <Typography variant="h4" fontWeight={600}>
                    {payments.length || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <CheckCircleIcon color="success" fontSize="large" />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Completed
                  </Typography>
                  <Typography variant="h4" fontWeight={600}>
                    {payments.filter(p => p?.status === 'completed').length || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <PendingIcon color="warning" fontSize="large" />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Pending
                  </Typography>
                  <Typography variant="h4" fontWeight={600}>
                    {payments.filter(p => p?.status === 'pending').length || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Payment History Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Transaction History
          </Typography>
          {loading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : payments.length > 0 ? (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {payments.map((payment) => (
                    <TableRow key={payment.id}>
                      <TableCell>
                        {new Date(payment.created_at).toLocaleDateString('en-IN')}
                      </TableCell>
                      <TableCell>
                        <Typography fontWeight={500}>
                          {payment.description || payment.membership_type}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {payment.transaction_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography fontWeight={600}>
                          ₹{parseFloat(payment.amount).toLocaleString('en-IN')}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(payment.status)}
                          label={payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                          color={getStatusColor(payment.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={downloading ? <CircularProgress size={14} /> : <ReceiptIcon />}
                          disabled={downloading || payment.status !== 'completed'}
                          onClick={() => dispatch(downloadReceipt(payment.id))}
                        >
                          PDF
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box textAlign="center" p={4}>
              <Typography color="text.secondary">
                No payment history found
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Payment Dialog */}
      <Dialog open={paymentDialogOpen} onClose={() => setPaymentDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Confirm Payment</DialogTitle>
        <DialogContent>
          {selectedPayment && (
            <Box>
              <Typography variant="body1" gutterBottom>
                You are about to make a payment for:
              </Typography>
              <Card variant="outlined" sx={{ mt: 2, p: 2 }}>
                <Typography variant="h6" fontWeight={600}>
                  {selectedPayment.description}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Box display="flex" justifyContent="space-between">
                  <Typography>Amount:</Typography>
                  <Typography variant="h6" fontWeight={600}>
                    ₹{parseFloat(selectedPayment.amount).toLocaleString('en-IN')}
                  </Typography>
                </Box>
              </Card>
              <Alert severity="info" sx={{ mt: 2 }}>
                You will be redirected to Instamojo payment gateway to complete your payment securely.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleConfirmPayment}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Proceed to Payment'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
