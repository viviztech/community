import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Receipt as ReceiptIcon,
  CardMembership as CertIcon,
} from '@mui/icons-material';
import { fetchPayments, downloadReceipt, downloadCertificate } from '../store/slices/paymentsSlice';

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const paymentId = searchParams.get('payment_id');

  const { payments = [], downloading, error } = useSelector((state) => state.payments || {});
  const [membership, setMembership] = useState(null);

  useEffect(() => {
    dispatch(fetchPayments());
  }, [dispatch]);

  useEffect(() => {
    if (paymentId && payments.length > 0) {
      const payment = payments.find((p) => String(p.id) === String(paymentId));
      if (payment?.membership) {
        setMembership(payment.membership);
      }
    }
  }, [payments, paymentId]);

  const isMembership = membership !== null;

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" p={4}>
      <Card sx={{ maxWidth: 520, width: '100%', textAlign: 'center' }}>
        <CardContent sx={{ p: 6 }}>
          <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Payment Successful!
          </Typography>
          <Typography color="text.secondary" mb={1}>
            Your payment has been processed. A receipt
            {isMembership ? ' and membership certificate have' : ' has'} been sent to your email.
          </Typography>

          {paymentId && (
            <Typography variant="body2" color="text.secondary" mb={3}>
              Payment ID: {paymentId}
            </Typography>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2, textAlign: 'left' }}>
              {typeof error === 'string' ? error : 'Download failed. Please try from your payment history.'}
            </Alert>
          )}

          <Box display="flex" flexDirection="column" gap={2} mb={3}>
            {paymentId && (
              <Button
                variant="contained"
                fullWidth
                startIcon={downloading ? <CircularProgress size={18} color="inherit" /> : <ReceiptIcon />}
                disabled={downloading}
                onClick={() => dispatch(downloadReceipt(paymentId))}
              >
                Download Receipt PDF
              </Button>
            )}
            {isMembership && (
              <Button
                variant="contained"
                color="secondary"
                fullWidth
                startIcon={downloading ? <CircularProgress size={18} color="inherit" /> : <CertIcon />}
                disabled={downloading}
                onClick={() => dispatch(downloadCertificate(membership.id || membership))}
              >
                Download Membership Certificate
              </Button>
            )}
          </Box>

          <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
            <Button variant="outlined" onClick={() => navigate('/app/memberships')}>
              View Membership
            </Button>
            <Button variant="outlined" onClick={() => navigate('/app/payments')}>
              Payment History
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
