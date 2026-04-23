import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Alert,
  CircularProgress,
  Divider,
  TextField,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Check as CheckIcon,
  Download as DownloadIcon,
  CardMembership as CertIcon,
  Receipt as ReceiptIcon,
  VolunteerActivism as DonateIcon,
} from '@mui/icons-material';
import { fetchMembershipTiers, fetchMyMemberships } from '../store/slices/membershipSlice';
import { initiatePayment, downloadReceipt, downloadCertificate, clearPaymentError } from '../store/slices/paymentsSlice';
import { fetchPayments } from '../store/slices/paymentsSlice';

export default function Memberships() {
  const dispatch = useDispatch();
  const { tiers, myMemberships, currentMembership, loading: membershipLoading } = useSelector((state) => state.memberships);
  const { loading: paymentLoading, downloading, error: paymentError, paymentUrl } = useSelector((state) => state.payments || {});

  const [selectedTier, setSelectedTier] = useState(null);
  const [membershipType, setMembershipType] = useState('yearly');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [donateDialogOpen, setDonateDialogOpen] = useState(false);
  const [donationAmount, setDonationAmount] = useState('');
  const [donationNote, setDonationNote] = useState('');
  const [tab, setTab] = useState(0);

  const { payments = [] } = useSelector((state) => state.payments || {});

  useEffect(() => {
    dispatch(fetchMembershipTiers());
    dispatch(fetchMyMemberships());
    dispatch(fetchPayments());
  }, [dispatch]);

  // Redirect to Instamojo once we have a payment URL
  useEffect(() => {
    if (paymentUrl) {
      window.location.href = paymentUrl;
    }
  }, [paymentUrl]);

  const handleChoosePlan = (tier) => {
    setSelectedTier(tier);
    setDialogOpen(true);
  };

  const handleConfirmPayment = () => {
    if (!selectedTier) return;
    dispatch(initiatePayment({
      payment_type: membershipType === 'yearly' ? 'membership_yearly' : 'membership_lifetime',
      tier_id: selectedTier.id,
    }));
    setDialogOpen(false);
  };

  const handleDonate = () => {
    const amt = parseFloat(donationAmount);
    if (!amt || amt <= 0) return;
    dispatch(initiatePayment({
      payment_type: 'donation',
      amount: amt,
      description: donationNote || 'Donation to ACTIV',
    }));
    setDonateDialogOpen(false);
    setDonationAmount('');
    setDonationNote('');
  };

  const formatPrice = (price) =>
    price ? `₹${parseFloat(price).toLocaleString('en-IN')}` : 'N/A';

  const loading = membershipLoading || paymentLoading;

  return (
    <Box>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Membership & Payments
          </Typography>
          <Typography color="text.secondary">
            Choose a plan, make donations, and download your documents
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<DonateIcon />}
          onClick={() => setDonateDialogOpen(true)}
        >
          Donate
        </Button>
      </Box>

      {paymentError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearPaymentError())}>
          {typeof paymentError === 'string' ? paymentError : JSON.stringify(paymentError)}
        </Alert>
      )}

      {currentMembership && (
        <Alert
          severity={currentMembership.status === 'active' ? 'success' : 'info'}
          sx={{ mb: 3 }}
          action={
            currentMembership.status === 'active' && (
              <Box display="flex" gap={1}>
                {currentMembership.payment && (
                  <Button
                    size="small"
                    startIcon={downloading ? <CircularProgress size={14} /> : <ReceiptIcon />}
                    disabled={downloading}
                    onClick={() => dispatch(downloadReceipt(currentMembership.payment))}
                  >
                    Receipt
                  </Button>
                )}
                <Button
                  size="small"
                  startIcon={downloading ? <CircularProgress size={14} /> : <CertIcon />}
                  disabled={downloading}
                  onClick={() => dispatch(downloadCertificate(currentMembership.id))}
                >
                  Certificate
                </Button>
              </Box>
            )
          }
        >
          Your current membership: <strong>{currentMembership.tier?.name}</strong> ({currentMembership.status})
          {currentMembership.end_date &&
            ` — Valid until ${new Date(currentMembership.end_date).toLocaleDateString('en-IN')}`}
        </Alert>
      )}

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Plans" />
        <Tab label="My Memberships" />
      </Tabs>

      {/* ── Tab 0: Plans ── */}
      {tab === 0 && (
        <>
          {/* Yearly / Lifetime toggle */}
          <FormControl sx={{ mb: 3 }}>
            <RadioGroup
              row
              value={membershipType}
              onChange={(e) => setMembershipType(e.target.value)}
            >
              <FormControlLabel value="yearly" control={<Radio />} label="Yearly" />
              <FormControlLabel value="lifetime" control={<Radio />} label="Lifetime" />
            </RadioGroup>
          </FormControl>

          <Grid container spacing={3}>
            {tiers.map((tier) => {
              const isCurrent = currentMembership?.tier?.id === tier.id && currentMembership?.status === 'active';
              const price = membershipType === 'yearly' ? tier.yearly_price : tier.lifetime_price;

              return (
                <Grid item xs={12} sm={6} md={3} key={tier.id}>
                  <Card
                    sx={{
                      height: '100%',
                      position: 'relative',
                      border: isCurrent ? 2 : 1,
                      borderColor: isCurrent ? 'primary.main' : 'divider',
                    }}
                  >
                    {isCurrent && (
                      <Chip
                        label="Current Plan"
                        color="primary"
                        size="small"
                        sx={{ position: 'absolute', top: 16, right: 16 }}
                      />
                    )}
                    <CardContent>
                      <Typography variant="h5" fontWeight={600} gutterBottom>
                        {tier.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" mb={2}>
                        {tier.description}
                      </Typography>

                      <Box mb={3}>
                        <Typography variant="h4" fontWeight={700}>
                          {formatPrice(price)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {membershipType === 'yearly' ? 'per year' : 'one-time lifetime'}
                        </Typography>
                      </Box>

                      <Divider sx={{ mb: 2 }} />

                      {Array.isArray(tier.features) &&
                        tier.features.map((feature, index) => (
                          <Box key={index} display="flex" alignItems="center" mb={1}>
                            <CheckIcon color="success" fontSize="small" sx={{ mr: 1 }} />
                            <Typography variant="body2">{feature}</Typography>
                          </Box>
                        ))}

                      <Box mt={3}>
                        <Button
                          variant={isCurrent ? 'outlined' : 'contained'}
                          fullWidth
                          disabled={isCurrent || loading || !price}
                          onClick={() => handleChoosePlan(tier)}
                          startIcon={loading && selectedTier?.id === tier.id ? <CircularProgress size={18} color="inherit" /> : null}
                        >
                          {isCurrent ? 'Current Plan' : 'Proceed to Payment'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>

          {tiers.length === 0 && !loading && (
            <Box textAlign="center" py={8}>
              <Typography color="text.secondary">No membership tiers available.</Typography>
            </Box>
          )}
        </>
      )}

      {/* ── Tab 1: My Memberships ── */}
      {tab === 1 && (
        <Grid container spacing={2}>
          {myMemberships.length === 0 && (
            <Grid item xs={12}>
              <Box textAlign="center" py={8}>
                <Typography color="text.secondary">No memberships found.</Typography>
              </Box>
            </Grid>
          )}
          {myMemberships.map((membership) => {
            const isActive = membership.status === 'active';
            // Find the payment associated with this membership
            const relatedPayment = payments.find(
              (p) => p.id === membership.payment || (membership.payment && p.id === membership.payment)
            );

            return (
              <Grid item xs={12} sm={6} md={4} key={membership.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                      <Box>
                        <Typography fontWeight={600}>{membership.tier?.name}</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                          {membership.membership_type} membership
                        </Typography>
                      </Box>
                      <Chip
                        label={membership.status}
                        color={isActive ? 'success' : 'default'}
                        size="small"
                        sx={{ textTransform: 'capitalize' }}
                      />
                    </Box>

                    {membership.start_date && (
                      <Typography variant="caption" color="text.secondary" display="block" mb={2}>
                        From: {new Date(membership.start_date).toLocaleDateString('en-IN')}
                        {membership.end_date
                          ? `  To: ${new Date(membership.end_date).toLocaleDateString('en-IN')}`
                          : '  (Lifetime)'}
                      </Typography>
                    )}

                    {isActive && (
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {membership.payment && (
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={downloading ? <CircularProgress size={14} /> : <ReceiptIcon />}
                            disabled={downloading}
                            onClick={() => dispatch(downloadReceipt(membership.payment))}
                          >
                            Receipt
                          </Button>
                        )}
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={downloading ? <CircularProgress size={14} /> : <CertIcon />}
                          disabled={downloading}
                          onClick={() => dispatch(downloadCertificate(membership.id))}
                        >
                          Certificate
                        </Button>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* ── Confirm Payment Dialog ── */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Confirm Membership Payment</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            You are about to subscribe to <strong>{selectedTier?.name}</strong>
          </Typography>

          <FormControl component="fieldset" sx={{ mb: 2 }}>
            <RadioGroup value={membershipType} onChange={(e) => setMembershipType(e.target.value)}>
              <FormControlLabel
                value="yearly"
                control={<Radio />}
                label={
                  <Box>
                    <Typography>Yearly Membership</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedTier?.yearly_price
                        ? `${formatPrice(selectedTier.yearly_price)} / year`
                        : 'N/A'}
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="lifetime"
                control={<Radio />}
                label={
                  <Box>
                    <Typography>Lifetime Membership</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedTier?.lifetime_price
                        ? `${formatPrice(selectedTier.lifetime_price)} one-time`
                        : 'N/A'}
                    </Typography>
                  </Box>
                }
              />
            </RadioGroup>
          </FormControl>

          <Alert severity="info">
            You will be redirected to Instamojo to complete your payment securely. A receipt and membership
            certificate will be emailed to you automatically.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleConfirmPayment} disabled={loading}>
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Pay Now'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ── Donate Dialog ── */}
      <Dialog open={donateDialogOpen} onClose={() => setDonateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <DonateIcon color="primary" />
            Make a Donation
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Your donation supports ACTIV's mission to empower Adidravidar communities.
          </Typography>
          <TextField
            label="Donation Amount (₹)"
            type="number"
            fullWidth
            value={donationAmount}
            onChange={(e) => setDonationAmount(e.target.value)}
            inputProps={{ min: 1 }}
            sx={{ mb: 2 }}
          />
          <TextField
            label="Note (optional)"
            fullWidth
            value={donationNote}
            onChange={(e) => setDonationNote(e.target.value)}
            placeholder="e.g. In memory of..."
          />
          <Alert severity="info" sx={{ mt: 2 }}>
            You will be redirected to Instamojo. A receipt will be emailed to you after payment.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDonateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleDonate}
            disabled={loading || !donationAmount || parseFloat(donationAmount) <= 0}
            startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <DonateIcon />}
          >
            Donate ₹{donationAmount || '0'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
