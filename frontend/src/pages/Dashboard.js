import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Person as PersonIcon,
  Event as EventIcon,
  CardMembership as MembershipIcon,
  TrendingUp as TrendingUpIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { fetchMemberProfile } from '../store/slices/memberSlice';
import { fetchEvents } from '../store/slices/eventSlice';
import { fetchMyMemberships } from '../store/slices/membershipSlice';

const StatCard = ({ title, value, icon, color, subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="flex-start" justifyContent="space-between">
        <Box>
          <Typography color="text.secondary" variant="body2" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight={600}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main` }}>
          {icon}
        </Avatar>
      </Box>
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const { profile } = useSelector((state) => state.members);
  const { events } = useSelector((state) => state.events);
  const { myMemberships, currentMembership } = useSelector((state) => state.memberships);

  useEffect(() => {
    dispatch(fetchMemberProfile());
    dispatch(fetchEvents({ status: 'published' }));
    dispatch(fetchMyMemberships());
  }, [dispatch]);

  const upcomingEvents = events.filter((e) => new Date(e.event_date) > new Date()).slice(0, 3);

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" fontWeight={600} gutterBottom>
          Welcome, {user?.first_name || 'Member'}!
        </Typography>
        <Typography color="text.secondary">
          Here's an overview of your ACTIV membership
        </Typography>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Profile Completion"
            value={`${profile?.profile_completion_percentage || 0}%`}
            icon={<PersonIcon />}
            color="primary"
            subtitle="Keep your profile updated"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Upcoming Events"
            value={upcomingEvents.length}
            icon={<EventIcon />}
            color="secondary"
            subtitle="Events to attend"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Membership Status"
            value={currentMembership?.status === 'active' ? 'Active' : 'Inactive'}
            icon={<MembershipIcon />}
            color={currentMembership?.status === 'active' ? 'success' : 'warning'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Membership Tier"
            value={currentMembership?.tier?.name || 'None'}
            icon={<TrendingUpIcon />}
            color="info"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" fontWeight={600}>
                  Upcoming Events
                </Typography>
                <Button
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/events')}
                >
                  View All
                </Button>
              </Box>
              {upcomingEvents.length > 0 ? (
                upcomingEvents.map((event) => (
                  <Box
                    key={event.id}
                    p={2}
                    mb={2}
                    bgcolor="background.default"
                    borderRadius={1}
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Box>
                      <Typography fontWeight={500}>{event.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(event.event_date).toLocaleDateString('en-IN', {
                          weekday: 'short',
                          day: 'numeric',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </Typography>
                    </Box>
                    <Chip
                      label={event.ticket_price > 0 ? `₹${event.ticket_price}` : 'Free'}
                      color={event.ticket_price > 0 ? 'primary' : 'success'}
                      size="small"
                    />
                  </Box>
                ))
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography color="text.secondary">
                    No upcoming events
                  </Typography>
                  <Button
                    variant="outlined"
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/events')}
                  >
                    Browse Events
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Your Membership
              </Typography>
              {currentMembership ? (
                <Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">
                      Tier
                    </Typography>
                    <Typography fontWeight={500}>
                      {currentMembership.tier?.name || 'N/A'}
                    </Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">
                      Status
                    </Typography>
                    <Chip
                      label={currentMembership.status}
                      color={currentMembership.status === 'active' ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  {currentMembership.end_date && (
                    <Box mb={2}>
                      <Typography variant="body2" color="text.secondary">
                        Expires On
                      </Typography>
                      <Typography fontWeight={500}>
                        {new Date(currentMembership.end_date).toLocaleDateString('en-IN')}
                      </Typography>
                    </Box>
                  )}
                  <Button
                    fullWidth
                    variant="outlined"
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/memberships')}
                  >
                    Manage Membership
                  </Button>
                </Box>
              ) : (
                <Box textAlign="center" py={2}>
                  <Typography color="text.secondary" gutterBottom>
                    No active membership
                  </Typography>
                  <Button
                    variant="contained"
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/memberships')}
                  >
                    Apply Now
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>

          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Profile Progress
              </Typography>
              <Box mt={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" color="text.secondary">
                    Completion
                  </Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {profile?.profile_completion_percentage || 0}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={profile?.profile_completion_percentage || 0}
                  sx={{ height: 8, borderRadius: 4 }}
                />
                {profile?.profile_completion_percentage < 80 && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Complete 80% to become eligible for membership approval
                  </Typography>
                )}
                <Button
                  fullWidth
                  variant="outlined"
                  sx={{ mt: 2 }}
                  onClick={() => navigate('/profile')}
                >
                  Complete Profile
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
