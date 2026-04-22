import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import { fetchPayments } from '../store/slices/paymentsSlice';

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const paymentId = searchParams.get('payment_id');

  useEffect(() => {
    dispatch(fetchPayments());
  }, [dispatch]);

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" p={4}>
      <Card sx={{ maxWidth: 480, width: '100%', textAlign: 'center' }}>
        <CardContent sx={{ p: 6 }}>
          <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Payment Successful!
          </Typography>
          <Typography color="text.secondary" mb={2}>
            Your payment has been processed successfully.
          </Typography>
          {paymentId && (
            <Typography variant="body2" color="text.secondary" mb={4}>
              Payment ID: {paymentId}
            </Typography>
          )}
          <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
            <Button
              variant="contained"
              onClick={() => navigate('/app/memberships')}
            >
              View Membership
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/payments')}
            >
              Payment History
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
