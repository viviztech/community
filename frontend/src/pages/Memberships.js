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
} from '@mui/material';
import { Check as CheckIcon } from '@mui/icons-material';
import { fetchMembershipTiers, fetchMyMemberships, applyForMembership } from '../store/slices/membershipSlice';

export default function Memberships() {
  const dispatch = useDispatch();
  const { tiers, myMemberships, currentMembership, loading } = useSelector((state) => state.memberships);
  const [selectedTier, setSelectedTier] = useState(null);
  const [membershipType, setMembershipType] = useState('yearly');
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchMembershipTiers());
    dispatch(fetchMyMemberships());
  }, [dispatch]);

  const handleApplyClick = (tier) => {
    setSelectedTier(tier);
    setDialogOpen(true);
  };

  const handleConfirmApply = () => {
    if (selectedTier) {
      const data = {
        tier_id: selectedTier.id,
        membership_type: membershipType,
      };
      dispatch(applyForMembership(data)).then(() => {
        setDialogOpen(false);
        dispatch(fetchMyMemberships());
      });
    }
  };

  const formatPrice = (price) => {
    return price ? `₹${parseFloat(price).toLocaleString('en-IN')}` : 'Free';
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" fontWeight={600} gutterBottom>
          Membership Plans
        </Typography>
        <Typography color="text.secondary">
          Choose the right membership tier for you
        </Typography>
      </Box>

      {currentMembership && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Your current membership: <strong>{currentMembership.tier?.name}</strong> ({currentMembership.status})
          {currentMembership.end_date && ` - Valid until ${new Date(currentMembership.end_date).toLocaleDateString('en-IN')}`}
        </Alert>
      )}

      <Grid container spacing={3}>
        {tiers.map((tier) => {
          const isCurrent = currentMembership?.tier?.id === tier.id;
          const price = membershipType === 'yearly' ? tier.yearly_price : tier.lifetime_price;
          
          return (
            <Grid item xs={12} md={3} key={tier.id}>
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
                      {membershipType === 'yearly' ? 'per year' : 'lifetime'}
                    </Typography>
                  </Box>

                  <Divider sx={{ mb: 2 }} />

                  {Array.isArray(tier.features) && tier.features.map((feature, index) => (
                    <Box key={index} display="flex" alignItems="center" mb={1}>
                      <CheckIcon color="success" fontSize="small" sx={{ mr: 1 }} />
                      <Typography variant="body2">{feature}</Typography>
                    </Box>
                  ))}

                  <Box mt={3}>
                    <Button
                      variant={isCurrent ? 'outlined' : 'contained'}
                      fullWidth
                      disabled={isCurrent || loading}
                      onClick={() => handleApplyClick(tier)}
                    >
                      {isCurrent ? 'Current Plan' : 'Choose Plan'}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Membership History */}
      {myMemberships.length > 0 && (
        <Box mt={4}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Membership History
          </Typography>
          <Grid container spacing={2}>
            {myMemberships.map((membership) => (
              <Grid item xs={12} sm={6} md={4} key={membership.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography fontWeight={600}>{membership.tier?.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {membership.membership_type} • {membership.status}
                        </Typography>
                      </Box>
                      <Chip
                        label={membership.status}
                        color={membership.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                    {membership.start_date && (
                      <Typography variant="caption" color="text.secondary">
                        From: {new Date(membership.start_date).toLocaleDateString('en-IN')}
                        {membership.end_date && ` - To: ${new Date(membership.end_date).toLocaleDateString('en-IN')}`}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Apply Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Select Membership Type</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            You selected <strong>{selectedTier?.name}</strong>
          </Typography>
          
          <FormControl component="fieldset">
            <RadioGroup
              value={membershipType}
              onChange={(e) => setMembershipType(e.target.value)}
            >
              <FormControlLabel
                value="yearly"
                control={<Radio />}
                label={
                  <Box>
                    <Typography>Yearly Membership</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedTier?.yearly_price ? `₹${parseFloat(selectedTier.yearly_price).toLocaleString('en-IN')}/year` : 'N/A'}
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
                      {selectedTier?.lifetime_price ? `₹${parseFloat(selectedTier.lifetime_price).toLocaleString('en-IN')} one-time` : 'N/A'}
                    </Typography>
                  </Box>
                }
              />
            </RadioGroup>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleConfirmApply}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Proceed to Payment'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
