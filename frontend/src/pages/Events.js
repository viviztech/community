import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Grid,
  Chip,
  TextField,
  InputAdornment,
  Tab,
  Tabs,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  Event as EventIcon,
  LocationOn as LocationIcon,
  CalendarMonth as CalendarIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { fetchEvents } from '../store/slices/eventSlice';

export default function Events() {
  const dispatch = useDispatch();
  const { events, loading } = useSelector((state) => state.events);
  const [search, setSearch] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    let status = 'published';
    if (tabValue === 1) status = 'ongoing';
    else if (tabValue === 2) status = 'completed';
    dispatch(fetchEvents({ status, search }));
  }, [dispatch, tabValue, search]);

  const getStatusColor = (event) => {
    const eventDate = new Date(event.event_date);
    if (eventDate < new Date()) return 'default';
    return 'primary';
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" fontWeight={600} gutterBottom>
          Events
        </Typography>
        <Typography color="text.secondary">
          Browse and register for ACTIV events
        </Typography>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search events..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Upcoming" />
        <Tab label="Ongoing" />
        <Tab label="Past Events" />
      </Tabs>

      {loading ? (
        <Typography textAlign="center" py={4}>Loading events...</Typography>
      ) : events.length === 0 ? (
        <Alert severity="info">No events found</Alert>
      ) : (
        <Grid container spacing={3}>
          {events.map((event) => (
            <Grid item xs={12} sm={6} md={4} key={event.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                {event.image && (
                  <CardMedia
                    component="img"
                    height="180"
                    image={event.image}
                    alt={event.title}
                  />
                )}
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Typography variant="h6" fontWeight={600}>
                      {event.title}
                    </Typography>
                    <Chip
                      label={event.ticket_price > 0 ? `₹${event.ticket_price}` : 'Free'}
                      color={event.ticket_price > 0 ? 'primary' : 'success'}
                      size="small"
                    />
                  </Box>
                  
                  <Box display="flex" alignItems="center" mb={1}>
                    <CalendarIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {new Date(event.event_date).toLocaleDateString('en-IN', {
                        weekday: 'short',
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" alignItems="center" mb={2}>
                    <LocationIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {event.venue}
                    </Typography>
                  </Box>

                  <Box display="flex" alignItems="center" mb={2}>
                    <GroupIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {event.available_tickets || event.max_delegates} spots available
                    </Typography>
                  </Box>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      mb: 2,
                    }}
                  >
                    {event.description}
                  </Typography>
                </CardContent>
                <Box p={2} pt={0}>
                  <Button variant="contained" fullWidth>
                    Register Now
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
