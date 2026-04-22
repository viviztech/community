import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  InputAdornment,
  Grid,
  Chip,
  Avatar,
  CircularProgress,
  Alert,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Pagination,
} from '@mui/material';
import { Search as SearchIcon, Business as BusinessIcon, LocationOn as LocationIcon } from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const SOCIAL_CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'SC', label: 'Scheduled Caste' },
  { value: 'ST', label: 'Scheduled Tribe' },
  { value: 'CC', label: 'Converted Christians' },
  { value: 'OBC', label: 'Other Backward Class' },
  { value: 'O', label: 'Others' },
];

export default function MemberDirectory() {
  const [members, setMembers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [socialCategory, setSocialCategory] = useState('');
  const [memberType, setMemberType] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const fetchMembers = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('accessToken');
      const params = new URLSearchParams({ page, page_size: pageSize });
      if (search) params.append('search', search);
      if (socialCategory) params.append('social_category', socialCategory);
      if (memberType) params.append('member_type', memberType);

      const response = await axios.get(`${API_URL}/members/directory/?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMembers(response.data.results || []);
      setTotal(response.data.count || 0);
    } catch (err) {
      setError('Failed to load member directory.');
    } finally {
      setLoading(false);
    }
  }, [search, socialCategory, page]);

  useEffect(() => {
    const timer = setTimeout(fetchMembers, 400);
    return () => clearTimeout(timer);
  }, [fetchMembers]);

  const handleSearchChange = (e) => { setSearch(e.target.value); setPage(1); };
  const handleCategoryChange = (e) => { setSocialCategory(e.target.value); setPage(1); };
  const handleTypeChange = (e) => { setMemberType(e.target.value); setPage(1); };

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" fontWeight={600} gutterBottom>
          Member Directory
        </Typography>
        <Typography color="text.secondary">
          Browse approved ACTIV members
        </Typography>
      </Box>

      {/* Filters */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            placeholder="Search by name, organization or location..."
            value={search}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth>
            <InputLabel>Member Type</InputLabel>
            <Select value={memberType} label="Member Type" onChange={handleTypeChange}>
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value="individual">Individual</MenuItem>
              <MenuItem value="shg">SHG</MenuItem>
              <MenuItem value="fpo">FPO</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth>
            <InputLabel>Social Category</InputLabel>
            <Select value={socialCategory} label="Social Category" onChange={handleCategoryChange}>
              {SOCIAL_CATEGORIES.map((c) => (
                <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <Typography variant="body2" color="text.secondary" mb={2}>
        {total} member{total !== 1 ? 's' : ''} found
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" py={6}>
          <CircularProgress />
        </Box>
      ) : members.length === 0 ? (
        <Alert severity="info">No approved members found matching your search.</Alert>
      ) : (
        <>
          <Grid container spacing={2}>
            {members.map((member) => (
              <Grid item xs={12} sm={6} md={4} key={member.id}>
                <Card sx={{ height: '100%', '&:hover': { boxShadow: 4 } }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 48, height: 48 }}>
                        {member.name?.[0] || 'M'}
                      </Avatar>
                      <Box>
                        <Typography fontWeight={600}>{member.name}</Typography>
                        <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                          {member.member_type_display && (
                            <Chip label={member.member_type_display} size="small" color="primary" variant="outlined" />
                          )}
                          {member.social_category && (
                            <Chip label={member.social_category} size="small" variant="outlined" />
                          )}
                        </Box>
                      </Box>
                    </Box>

                    {member.organization && (
                      <Box display="flex" alignItems="center" mb={1}>
                        <BusinessIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                        <Typography variant="body2" color="text.secondary" noWrap>
                          {member.organization}
                        </Typography>
                      </Box>
                    )}

                    {(member.block || member.district || member.state) && (
                      <Box display="flex" alignItems="center" mb={1}>
                        <LocationIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          {[member.block, member.district, member.state].filter(Boolean).join(', ')}
                        </Typography>
                      </Box>
                    )}

                    {member.business_type && (
                      <Chip
                        label={member.business_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                        sx={{ mt: 1 }}
                      />
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {total > pageSize && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={Math.ceil(total / pageSize)}
                page={page}
                onChange={(_, v) => setPage(v)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}
    </Box>
  );
}
