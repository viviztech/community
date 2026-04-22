import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { Cancel as CancelIcon } from '@mui/icons-material';

export default function PaymentFailed() {
  const navigate = useNavigate();

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" p={4}>
      <Card sx={{ maxWidth: 480, width: '100%', textAlign: 'center' }}>
        <CardContent sx={{ p: 6 }}>
          <CancelIcon sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Payment Failed
          </Typography>
          <Typography color="text.secondary" mb={4}>
            Your payment could not be processed. Please try again or contact support if the issue persists.
          </Typography>
          <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
            <Button
              variant="contained"
              onClick={() => navigate('/app/memberships')}
            >
              Try Again
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/')}
            >
              Go Home
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
