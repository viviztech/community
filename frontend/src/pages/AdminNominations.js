import React, { useState, useEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Avatar,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Check as CheckIcon,
  Block as RevokeIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const LEVEL_COLORS = {
  block: 'info',
  district: 'warning',
  state: 'success',
  super: 'error',
};

const STATUS_COLORS = {
  active: 'success',
  pending: 'warning',
  revoked: 'default',
};

function NominateDialog({ open, onClose, onSuccess }) {
  const [userId, setUserId] = useState('');
  const [adminLevel, setAdminLevel] = useState('block');
  const [areaId, setAreaId] = useState('');
  const [notes, setNotes] = useState('');
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { adminRole } = useSelector((state) => state.auth);

  // Determine which levels this admin can nominate
  const nominatableLevels = adminRole === 'super' || adminRole === null
    ? ['block', 'district', 'state', 'super']
    : adminRole === 'state'
    ? ['block', 'district']
    : adminRole === 'district'
    ? ['block']
    : [];

  useEffect(() => {
    if (!open) return;
    const token = localStorage.getItem('accessToken');
    const areaTypeMap = { block: 'block', district: 'district', state: 'state' };
    const areaType = areaTypeMap[adminLevel];
    if (!areaType) return;

    axios.get(`${API_URL}/members/areas/?type=${areaType}`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((r) => setAreas(r.data.results || r.data)).catch(() => setAreas([]));
  }, [adminLevel, open]);

  const handleSubmit = async () => {
    if (!userId.trim()) { setError('User ID is required.'); return; }
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('accessToken');
      const payload = { user_id: userId, admin_level: adminLevel, nomination_notes: notes };
      if (adminLevel !== 'super') payload.area_id = areaId;
      await axios.post(`${API_URL}/auth/admins/nominate/`, payload, {
        headers: { Authorization: `Bearer ${token}` },
      });
      onSuccess();
      onClose();
      setUserId(''); setAdminLevel('block'); setAreaId(''); setNotes('');
    } catch (err) {
      const data = err.response?.data;
      setError(typeof data === 'string' ? data : data?.error || JSON.stringify(data) || 'Failed to nominate admin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Nominate New Admin</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <TextField
          fullWidth
          label="User ID (UUID)"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          sx={{ mt: 1, mb: 2 }}
          helperText="Copy the user's ID from the Members list"
        />
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Admin Level</InputLabel>
          <Select value={adminLevel} label="Admin Level" onChange={(e) => { setAdminLevel(e.target.value); setAreaId(''); }}>
            {nominatableLevels.map((level) => (
              <MenuItem key={level} value={level}>
                {level.charAt(0).toUpperCase() + level.slice(1)} Admin
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {adminLevel !== 'super' && (
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Geographic Area</InputLabel>
            <Select value={areaId} label="Geographic Area" onChange={(e) => setAreaId(e.target.value)}>
              {areas.map((area) => (
                <MenuItem key={area.id} value={area.id}>{area.name} ({area.code})</MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        <TextField
          fullWidth
          label="Nomination Notes (optional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          multiline
          rows={2}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? <CircularProgress size={20} /> : 'Nominate'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default function AdminNominations() {
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [nominateOpen, setNominateOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  const statusFilter = ['', 'pending', 'active', 'revoked'][tabValue];

  const fetchAdmins = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('accessToken');
      const params = statusFilter ? `?status=${statusFilter}` : '';
      const response = await axios.get(`${API_URL}/auth/admins/${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAdmins(response.data);
    } catch (err) {
      setError('Failed to load admin list.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => { fetchAdmins(); }, [fetchAdmins]);

  const handleApprove = async (id) => {
    try {
      const token = localStorage.getItem('accessToken');
      await axios.post(`${API_URL}/auth/admins/${id}/approve/`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccessMsg('Admin approved successfully.');
      fetchAdmins();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to approve admin.');
    }
  };

  const handleRevoke = async (id) => {
    const reason = window.prompt('Reason for revocation (optional):') ?? '';
    if (reason === null) return;
    try {
      const token = localStorage.getItem('accessToken');
      await axios.post(`${API_URL}/auth/admins/${id}/revoke/`, { revoke_reason: reason }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccessMsg('Admin revoked.');
      fetchAdmins();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to revoke admin.');
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Manage Admins
          </Typography>
          <Typography color="text.secondary">
            Nominate, approve, and revoke admin roles
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setNominateOpen(true)}>
          Nominate Admin
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {successMsg && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMsg('')}>{successMsg}</Alert>}

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="All" />
        <Tab label="Pending" />
        <Tab label="Active" />
        <Tab label="Revoked" />
      </Tabs>

      <Card>
        <CardContent>
          {loading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : admins.length === 0 ? (
            <Alert severity="info">No admins found.</Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Admin</TableCell>
                    <TableCell>Level</TableCell>
                    <TableCell>Area</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Nominated By</TableCell>
                    <TableCell>Since</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {admins.map((admin) => (
                    <TableRow key={admin.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Avatar sx={{ width: 32, height: 32, mr: 1, bgcolor: 'primary.main' }}>
                            {admin.user_name?.[0] || 'A'}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={500}>{admin.user_name}</Typography>
                            <Typography variant="caption" color="text.secondary">{admin.user_email}</Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={admin.admin_level_display}
                          color={LEVEL_COLORS[admin.admin_level] || 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{admin.area_name || '—'}</TableCell>
                      <TableCell>
                        <Chip
                          label={admin.status_display}
                          color={STATUS_COLORS[admin.status] || 'default'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">{admin.nominated_by_email || '—'}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {admin.activated_at
                            ? new Date(admin.activated_at).toLocaleDateString('en-IN')
                            : new Date(admin.created_at).toLocaleDateString('en-IN')}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {admin.status === 'pending' && (
                          <Button
                            size="small"
                            color="success"
                            variant="contained"
                            startIcon={<CheckIcon />}
                            onClick={() => handleApprove(admin.id)}
                            sx={{ mr: 1 }}
                          >
                            Approve
                          </Button>
                        )}
                        {admin.status === 'active' && (
                          <Button
                            size="small"
                            color="error"
                            variant="outlined"
                            startIcon={<RevokeIcon />}
                            onClick={() => handleRevoke(admin.id)}
                          >
                            Revoke
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <NominateDialog
        open={nominateOpen}
        onClose={() => setNominateOpen(false)}
        onSuccess={() => { setSuccessMsg('Admin nominated successfully!'); fetchAdmins(); }}
      />
    </Box>
  );
}
