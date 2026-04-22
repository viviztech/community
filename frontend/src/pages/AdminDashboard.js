import React, { useEffect, useState } from 'react';
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tab,
  Tabs,
  Alert,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  People as PeopleIcon,
  Approval as ApprovalIcon,
  Event as EventIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { fetchDashboardStats, fetchAdminMembers, fetchAdminApprovals, fetchGeographicStats, processApproval } from '../store/slices/adminSlice';

const StatCard = ({ title, value, icon, color, subtitle, onClick }) => (
  <Card sx={{ cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
    <CardContent>
      <Box display="flex" alignItems="flex-start" justifyContent="space-between">
        <Box>
          <Typography color="text.secondary" variant="body2" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight={600}>
            {value !== undefined ? value : '-'}
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

const ROLE_LABELS = {
  block: 'Block Admin',
  district: 'District Admin',
  state: 'State Admin',
  super: 'Super Admin',
};

export default function AdminDashboard() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, adminRole } = useSelector((state) => state.auth);
  const { stats, members, membersTotal, approvals, approvalsTotal, geographic, loading } = useSelector((state) => state.admin);
  const [tabValue, setTabValue] = useState(0);
  const [search, setSearch] = useState('');

  useEffect(() => {
    // Check if user is admin
    if (!user?.is_superuser && !user?.member_profile?.block && !user?.member_profile?.district && !user?.member_profile?.state) {
      // Not an admin, redirect or show error
    }
    dispatch(fetchDashboardStats());
    dispatch(fetchAdminMembers());
    dispatch(fetchAdminApprovals());
    dispatch(fetchGeographicStats());
  }, [dispatch, user]);

  const handleRefresh = () => {
    dispatch(fetchDashboardStats());
    dispatch(fetchAdminMembers());
    dispatch(fetchAdminApprovals());
    dispatch(fetchGeographicStats());
  };

  const handleSearch = (e) => {
    setSearch(e.target.value);
    dispatch(fetchAdminMembers({ search: e.target.value }));
  };

  const handleApprovalAction = (workflowId, action, comments = '') => {
    dispatch(processApproval({ workflowId, action, comments })).then(() => {
      dispatch(fetchAdminApprovals());
      dispatch(fetchDashboardStats());
    });
  };

  if (loading && !stats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Box display="flex" alignItems="center" gap={1} mb={0.5}>
            <Typography variant="h4" fontWeight={600}>
              Admin Dashboard
            </Typography>
            {adminRole && (
              <Chip
                label={ROLE_LABELS[adminRole] || adminRole}
                color="primary"
                size="small"
              />
            )}
          </Box>
          <Typography color="text.secondary">
            {user?.admin_area ? `Managing: ${user.admin_area}` : 'Manage members, approvals, and view analytics'}
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          {(adminRole === 'state' || adminRole === 'super' || user?.is_superuser) && (
            <Button variant="outlined" onClick={() => navigate('/app/admin/nominations')}>
              Manage Admins
            </Button>
          )}
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={handleRefresh}>
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Members"
            value={stats?.total_members || 0}
            icon={<PeopleIcon />}
            color="primary"
            subtitle={`${stats?.approved_members || 0} approved`}
            onClick={() => setTabValue(1)}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Approvals"
            value={stats?.pending_approvals || 0}
            icon={<ApprovalIcon />}
            color="warning"
            subtitle="Awaiting review"
            onClick={() => setTabValue(2)}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Monthly Revenue"
            value={`₹${(stats?.monthly_revenue || 0).toLocaleString('en-IN')}`}
            icon={<MoneyIcon />}
            color="success"
            subtitle="This month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Upcoming Events"
            value={stats?.upcoming_events || 0}
            icon={<EventIcon />}
            color="info"
          />
        </Grid>
      </Grid>

      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Analytics" />
        <Tab label="Members" />
        <Tab label="Approvals" />
        <Tab label="Geographic" />
      </Tabs>

      {/* Analytics Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={3}>
                  Member Growth
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stats?.member_growth || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="count" stroke="#1976d2" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={3}>
                  Membership Tiers
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={Object.entries(stats?.membership_tiers || {}).map(([name, count]) => ({ name, count }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={3}>
                  Recent Registrations
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Email</TableCell>
                        <TableCell>Organization</TableCell>
                        <TableCell>Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {stats?.recent_registrations?.map((member) => (
                        <TableRow key={member.id}>
                          <TableCell>{member.name}</TableCell>
                          <TableCell>{member.email}</TableCell>
                          <TableCell>{member.organization || '-'}</TableCell>
                          <TableCell>{new Date(member.created_at).toLocaleDateString('en-IN')}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Members Tab */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6" fontWeight={600}>
                All Members ({membersTotal})
              </Typography>
              <TextField
                placeholder="Search members..."
                value={search}
                onChange={handleSearch}
                size="small"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Organization</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {members.map((member) => (
                    <TableRow key={member.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Avatar sx={{ width: 32, height: 32, mr: 1, bgcolor: 'primary.main' }}>
                            {member.name?.[0] || 'M'}
                          </Avatar>
                          {member.name}
                        </Box>
                      </TableCell>
                      <TableCell>{member.email}</TableCell>
                      <TableCell>{member.organization || '-'}</TableCell>
                      <TableCell>{member.district || member.block || '-'}</TableCell>
                      <TableCell>
                        <Chip label={member.social_category || '-'} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={member.is_active ? 'Active' : 'Inactive'}
                          color={member.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Approvals Tab */}
      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={3}>
              Pending Approvals ({approvalsTotal})
            </Typography>
            {approvals.length === 0 ? (
              <Alert severity="success">No pending approvals</Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Member</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Organization</TableCell>
                      <TableCell>Level</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {approvals.map((approval) => (
                      <TableRow key={approval.id} hover>
                        <TableCell>{approval.member_name}</TableCell>
                        <TableCell>{approval.member_email}</TableCell>
                        <TableCell>{approval.member_organization || '-'}</TableCell>
                        <TableCell>
                          <Chip label={approval.current_level} size="small" color="primary" />
                        </TableCell>
                        <TableCell>{new Date(approval.created_at).toLocaleDateString('en-IN')}</TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            color="success"
                            variant="contained"
                            sx={{ mr: 1 }}
                            onClick={() => handleApprovalAction(approval.id, 'approve')}
                          >
                            Approve
                          </Button>
                          <Button
                            size="small"
                            color="error"
                            variant="outlined"
                            onClick={() => {
                              const reason = window.prompt('Reason for rejection (optional):') || '';
                              handleApprovalAction(approval.id, 'reject', reason);
                            }}
                          >
                            Reject
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      )}

      {/* Geographic Tab */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={3}>
                  Members by District
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={geographic?.by_district || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={3}>
                  Members by Social Category
                </Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={geographic?.by_social_category || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#dc004e" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
