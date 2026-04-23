import React, { useCallback, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  Approval as ApprovalIcon,
  AttachMoney as MoneyIcon,
  CheckCircle as CheckCircleIcon,
  Event as EventIcon,
  Female as FemaleIcon,
  FilterList as FilterIcon,
  Group as GroupIcon,
  HourglassEmpty as HourglassIcon,
  Male as MaleIcon,
  People as PeopleIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  fetchAdminApprovals,
  fetchAdminAreas,
  fetchAdminMembers,
  fetchDashboardStats,
  fetchGeographicStats,
  processApproval,
} from '../store/slices/adminSlice';

// ─── constants ───────────────────────────────────────────────────────────────

const ROLE_LABELS = {
  block: 'Block Admin',
  district: 'District Admin',
  state: 'State Admin',
  super: 'Super Admin',
};

const GENDER_LABELS = { M: 'Male', F: 'Female', O: 'Other', 'Not set': 'Not Set' };
const GENDER_COLORS = { M: '#1976d2', F: '#e91e63', O: '#ff9800', 'Not set': '#9e9e9e' };

const CATEGORY_COLORS = ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#0288d1'];

const TYPE_COLORS = { individual: '#1976d2', shg: '#388e3c', fpo: '#f57c00' };
const TYPE_LABELS = { individual: 'Individual', shg: 'SHG', fpo: 'FPO' };

const LEVEL_COLOR = { block: 'default', district: 'primary', state: 'secondary', final: 'warning' };

// ─── sub-components ──────────────────────────────────────────────────────────

function StatCard({ title, value, icon, color, subtitle, onClick, alert }) {
  return (
    <Card
      sx={{ height: '100%', cursor: onClick ? 'pointer' : 'default', border: alert ? '2px solid' : 'none', borderColor: 'error.main' }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" justifyContent="space-between">
          <Box>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={700} color={alert ? 'error.main' : 'text.primary'}>
              {value !== undefined ? value : '-'}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color={alert ? 'error.main' : 'text.secondary'}>
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
}

function FilterBar({ filters, onChange, areas, adminLevel }) {
  const showDistrictFilter = adminLevel !== 'block';
  const showBlockFilter = true;

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={1.5}>
          <FilterIcon fontSize="small" color="action" />
          <Typography variant="subtitle2" fontWeight={600}>Filters</Typography>
          {Object.values(filters).some(Boolean) && (
            <Button size="small" onClick={() => onChange({})}>Clear all</Button>
          )}
        </Box>
        <Grid container spacing={2}>
          {showDistrictFilter && (
            <Grid item xs={6} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>District</InputLabel>
                <Select
                  value={filters.district || ''}
                  label="District"
                  onChange={(e) => onChange({ ...filters, district: e.target.value, block: '' })}
                >
                  <MenuItem value="">All Districts</MenuItem>
                  {areas.districts.map((d) => (
                    <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}
          {showBlockFilter && (
            <Grid item xs={6} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Block</InputLabel>
                <Select
                  value={filters.block || ''}
                  label="Block"
                  onChange={(e) => onChange({ ...filters, block: e.target.value })}
                >
                  <MenuItem value="">All Blocks</MenuItem>
                  {areas.blocks.map((b) => (
                    <MenuItem key={b.id} value={b.id}>{b.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}
          <Grid item xs={6} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Gender</InputLabel>
              <Select
                value={filters.gender || ''}
                label="Gender"
                onChange={(e) => onChange({ ...filters, gender: e.target.value })}
              >
                <MenuItem value="">All Genders</MenuItem>
                <MenuItem value="M">Male</MenuItem>
                <MenuItem value="F">Female</MenuItem>
                <MenuItem value="O">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Member Type</InputLabel>
              <Select
                value={filters.member_type || ''}
                label="Member Type"
                onChange={(e) => onChange({ ...filters, member_type: e.target.value })}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="individual">Individual</MenuItem>
                <MenuItem value="shg">SHG</MenuItem>
                <MenuItem value="fpo">FPO</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}

// ─── main component ───────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, adminRole } = useSelector((state) => state.auth);
  const { stats, members, membersTotal, approvals, approvalsTotal, geographic, areas, loading } =
    useSelector((state) => state.admin);

  const [tabValue, setTabValue] = useState(0);
  const [filters, setFilters] = useState({});
  const [memberSearch, setMemberSearch] = useState('');
  const [approvalSearch, setApprovalSearch] = useState('');

  const adminLevel = stats?.admin_level || adminRole || 'block';
  const isSuperOrState = adminLevel === 'super' || adminLevel === 'state' || user?.is_superuser;

  const loadAll = useCallback(
    (f = filters) => {
      const params = Object.fromEntries(Object.entries(f).filter(([, v]) => v));
      dispatch(fetchDashboardStats(params));
      dispatch(fetchAdminMembers(params));
      dispatch(fetchAdminApprovals(params));
      dispatch(fetchGeographicStats(params));
    },
    [dispatch, filters],
  );

  useEffect(() => {
    dispatch(fetchAdminAreas());
    loadAll({});
  }, [dispatch]); // eslint-disable-line

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    const params = Object.fromEntries(Object.entries(newFilters).filter(([, v]) => v));
    dispatch(fetchDashboardStats(params));
    dispatch(fetchAdminMembers({ ...params, search: memberSearch }));
    dispatch(fetchAdminApprovals({ ...params, search: approvalSearch }));
    dispatch(fetchGeographicStats(params));
  };

  const handleMemberSearch = (e) => {
    setMemberSearch(e.target.value);
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
    dispatch(fetchAdminMembers({ ...params, search: e.target.value }));
  };

  const handleApprovalSearch = (e) => {
    setApprovalSearch(e.target.value);
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
    dispatch(fetchAdminApprovals({ ...params, search: e.target.value }));
  };

  const handleApprovalAction = (workflowId, action, comments = '') => {
    dispatch(processApproval({ workflowId, action, comments })).then(() => {
      const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
      dispatch(fetchAdminApprovals(params));
      dispatch(fetchDashboardStats(params));
    });
  };

  // ── gender pie data ──────────────────────────────────────────────────────
  const genderPieData = stats
    ? Object.entries(stats.gender_breakdown || {})
        .filter(([, v]) => v > 0)
        .map(([k, v]) => ({ name: GENDER_LABELS[k] || k, value: v, color: GENDER_COLORS[k] || '#9e9e9e' }))
    : [];

  // ── member type pie data ─────────────────────────────────────────────────
  const typePieData = stats
    ? Object.entries(stats.type_breakdown || {})
        .filter(([, v]) => v > 0)
        .map(([k, v]) => ({ name: TYPE_LABELS[k] || k, value: v, color: TYPE_COLORS[k] || '#607d8b' }))
    : [];

  if (loading && !stats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* ── Header ── */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Box display="flex" alignItems="center" gap={1} mb={0.5}>
            <Typography variant="h4" fontWeight={700}>Admin Dashboard</Typography>
            {adminRole && (
              <Chip label={ROLE_LABELS[adminRole] || adminRole} color="primary" size="small" />
            )}
            {stats?.admin_area && (
              <Chip label={stats.admin_area} variant="outlined" size="small" />
            )}
          </Box>
          <Typography color="text.secondary" variant="body2">
            {isSuperOrState
              ? 'Organisation-wide view — all areas'
              : `Showing data for your ${adminLevel} area`}
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          {isSuperOrState && (
            <Button variant="outlined" size="small" onClick={() => navigate('/app/admin/nominations')}>
              Manage Admins
            </Button>
          )}
          <Button variant="outlined" size="small" startIcon={<RefreshIcon />} onClick={() => loadAll()}>
            Refresh
          </Button>
        </Box>
      </Box>

      {/* ── Filter Bar ── */}
      <FilterBar filters={filters} onChange={handleFilterChange} areas={areas} adminLevel={adminLevel} />

      {/* ── Stat Cards ── */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} sm={4} md={2}>
          <StatCard
            title="Total Members"
            value={stats?.total_members ?? 0}
            icon={<PeopleIcon />}
            color="primary"
            onClick={() => setTabValue(1)}
          />
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <StatCard
            title="Approved"
            value={stats?.approved_members ?? 0}
            icon={<CheckCircleIcon />}
            color="success"
            subtitle={`${stats?.total_members ? Math.round((stats.approved_members / stats.total_members) * 100) : 0}%`}
          />
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <StatCard
            title="Pending Approval"
            value={stats?.pending_approvals ?? 0}
            icon={<HourglassIcon />}
            color="warning"
            onClick={() => setTabValue(2)}
          />
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <StatCard
            title="SLA Breached"
            value={stats?.sla_breached ?? 0}
            icon={<WarningIcon />}
            color="error"
            alert={(stats?.sla_breached ?? 0) > 0}
            subtitle="> 24h waiting"
            onClick={() => setTabValue(2)}
          />
        </Grid>
        {isSuperOrState && (
          <Grid item xs={6} sm={4} md={2}>
            <StatCard
              title="Monthly Revenue"
              value={`₹${(stats?.monthly_revenue ?? 0).toLocaleString('en-IN')}`}
              icon={<MoneyIcon />}
              color="info"
            />
          </Grid>
        )}
        <Grid item xs={6} sm={4} md={2}>
          <StatCard
            title="Upcoming Events"
            value={stats?.upcoming_events ?? 0}
            icon={<EventIcon />}
            color="secondary"
          />
        </Grid>
      </Grid>

      {/* ── Tabs ── */}
      <Tabs
        value={tabValue}
        onChange={(_, v) => setTabValue(v)}
        sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
        variant="scrollable"
      >
        <Tab label="Overview" />
        <Tab label={`Members (${membersTotal})`} />
        <Tab
          label={
            <Box display="flex" alignItems="center" gap={0.5}>
              Approvals ({approvalsTotal})
              {(stats?.sla_breached ?? 0) > 0 && (
                <Chip label={stats.sla_breached} color="error" size="small" sx={{ height: 18, fontSize: 10 }} />
              )}
            </Box>
          }
        />
        <Tab label="Geographic" />
      </Tabs>

      {/* ════════════════════ TAB 0 — OVERVIEW ════════════════════ */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Member Growth */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Member Growth (Last 6 Months)</Typography>
                <Box height={260}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stats?.member_growth || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                      <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                      <RechartsTooltip />
                      <Line type="monotone" dataKey="count" stroke="#1976d2" strokeWidth={2} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Gender Pie */}
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Gender Distribution</Typography>
                {genderPieData.length > 0 ? (
                  <Box height={220}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={genderPieData} dataKey="value" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                          {genderPieData.map((entry, i) => (
                            <Cell key={i} fill={entry.color} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                ) : (
                  <Box display="flex" justifyContent="center" alignItems="center" height={220}>
                    <Typography color="text.secondary" variant="body2">No data</Typography>
                  </Box>
                )}
                <Divider sx={{ my: 1 }} />
                <Box display="flex" gap={1} flexWrap="wrap">
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <MaleIcon fontSize="small" sx={{ color: '#1976d2' }} />
                    <Typography variant="caption">{stats?.gender_breakdown?.male ?? 0} Male</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <FemaleIcon fontSize="small" sx={{ color: '#e91e63' }} />
                    <Typography variant="caption">{stats?.gender_breakdown?.female ?? 0} Female</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Member Type Pie */}
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Member Type Breakdown</Typography>
                {typePieData.length > 0 ? (
                  <Box height={220}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={typePieData} dataKey="value" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                          {typePieData.map((entry, i) => (
                            <Cell key={i} fill={entry.color} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                ) : (
                  <Box display="flex" justifyContent="center" alignItems="center" height={220}>
                    <Typography color="text.secondary" variant="body2">No data</Typography>
                  </Box>
                )}
                <Divider sx={{ my: 1 }} />
                <Box display="flex" gap={1} flexWrap="wrap">
                  {Object.entries(stats?.type_breakdown || {}).map(([k, v]) => (
                    <Chip key={k} label={`${TYPE_LABELS[k] || k}: ${v}`} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Area Breakdown (role-specific) */}
          {stats?.area_breakdown?.length > 0 && (
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight={600} mb={2}>
                    Members {stats.area_label}
                  </Typography>
                  <Box height={260}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={stats.area_breakdown} layout="vertical" margin={{ left: 80 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
                        <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
                        <RechartsTooltip />
                        <Bar dataKey="count" fill="#1976d2" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Social Category Bar */}
          {Object.keys(stats?.category_breakdown || {}).length > 0 && (
            <Grid item xs={12} sm={6} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight={600} mb={2}>Social Category</Typography>
                  <Box height={260}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={Object.entries(stats.category_breakdown).map(([k, v]) => ({ name: k, count: v }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                        <RechartsTooltip />
                        <Bar dataKey="count" fill="#7b1fa2" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Recent Registrations */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Recent Registrations</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Block</TableCell>
                        <TableCell>District</TableCell>
                        <TableCell>Gender</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(stats?.recent_registrations || []).map((m) => (
                        <TableRow key={m.id} hover>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Avatar sx={{ width: 28, height: 28, bgcolor: 'primary.main', fontSize: 12 }}>
                                {m.name?.[0] || 'M'}
                              </Avatar>
                              {m.name}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip label={TYPE_LABELS[m.member_type] || m.member_type} size="small" variant="outlined" />
                          </TableCell>
                          <TableCell>{m.block || '-'}</TableCell>
                          <TableCell>{m.district || '-'}</TableCell>
                          <TableCell>{GENDER_LABELS[m.gender] || '-'}</TableCell>
                          <TableCell>
                            <Chip
                              label={m.is_approved ? 'Approved' : 'Pending'}
                              color={m.is_approved ? 'success' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{new Date(m.created_at).toLocaleDateString('en-IN')}</TableCell>
                        </TableRow>
                      ))}
                      {!(stats?.recent_registrations?.length) && (
                        <TableRow>
                          <TableCell colSpan={7} align="center">
                            <Typography variant="body2" color="text.secondary" py={2}>No recent registrations</Typography>
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* ════════════════════ TAB 1 — MEMBERS ════════════════════ */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} flexWrap="wrap" gap={1}>
              <Typography variant="h6" fontWeight={600}>
                Members ({membersTotal})
              </Typography>
              <TextField
                placeholder="Search name, email, org..."
                value={memberSearch}
                onChange={handleMemberSearch}
                size="small"
                sx={{ width: 280 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <GroupIcon fontSize="small" color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Block</TableCell>
                    <TableCell>District</TableCell>
                    <TableCell>Gender</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Profile %</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Joined</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {members.map((m) => (
                    <TableRow key={m.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Avatar sx={{ width: 28, height: 28, bgcolor: 'primary.main', fontSize: 12 }}>
                            {m.name?.[0] || 'M'}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={500}>{m.name}</Typography>
                            <Typography variant="caption" color="text.secondary">{m.email}</Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label={TYPE_LABELS[m.member_type] || m.member_type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>{m.block || '-'}</TableCell>
                      <TableCell>{m.district || '-'}</TableCell>
                      <TableCell>{GENDER_LABELS[m.gender] || '-'}</TableCell>
                      <TableCell>
                        <Chip label={m.social_category || '-'} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={0.5}>
                          <Box
                            sx={{
                              width: 40,
                              height: 6,
                              borderRadius: 3,
                              bgcolor: m.profile_completion >= 80 ? 'success.main' : m.profile_completion >= 50 ? 'warning.main' : 'error.main',
                            }}
                          />
                          <Typography variant="caption">{m.profile_completion}%</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={m.is_approved ? 'Approved' : 'Pending'}
                          color={m.is_approved ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{new Date(m.created_at).toLocaleDateString('en-IN')}</TableCell>
                    </TableRow>
                  ))}
                  {members.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        <Typography variant="body2" color="text.secondary" py={3}>No members found</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* ════════════════════ TAB 2 — APPROVALS ════════════════════ */}
      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} flexWrap="wrap" gap={1}>
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="h6" fontWeight={600}>Approval Queue ({approvalsTotal})</Typography>
                {(stats?.sla_breached ?? 0) > 0 && (
                  <Alert severity="error" sx={{ py: 0, px: 1 }} icon={<WarningIcon fontSize="small" />}>
                    {stats.sla_breached} application{stats.sla_breached > 1 ? 's' : ''} past 24h SLA
                  </Alert>
                )}
              </Box>
              <TextField
                placeholder="Search member..."
                value={approvalSearch}
                onChange={handleApprovalSearch}
                size="small"
                sx={{ width: 240 }}
              />
            </Box>

            {approvals.length === 0 ? (
              <Alert severity="success" icon={<CheckCircleIcon />}>
                No pending approvals — you're all caught up!
              </Alert>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Member</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Block / District</TableCell>
                      <TableCell>Gender</TableCell>
                      <TableCell>Level</TableCell>
                      <TableCell>Waiting</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {approvals.map((a) => (
                      <TableRow
                        key={a.id}
                        hover
                        sx={{ bgcolor: a.sla_breached ? 'error.50' : 'inherit' }}
                      >
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight={500}>{a.member_name}</Typography>
                            <Typography variant="caption" color="text.secondary">{a.member_email}</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip label={TYPE_LABELS[a.member_type] || a.member_type} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{a.block || '-'}</Typography>
                          <Typography variant="caption" color="text.secondary">{a.district || ''}</Typography>
                        </TableCell>
                        <TableCell>{GENDER_LABELS[a.member_gender] || '-'}</TableCell>
                        <TableCell>
                          <Chip label={a.current_level} color={LEVEL_COLOR[a.current_level] || 'default'} size="small" />
                          {a.escalation_count > 0 && (
                            <Chip label={`↑${a.escalation_count}`} size="small" color="warning" sx={{ ml: 0.5 }} />
                          )}
                        </TableCell>
                        <TableCell>
                          <Tooltip title={a.sla_breached ? 'SLA breached — action required' : ''}>
                            <Box display="flex" alignItems="center" gap={0.5}>
                              {a.sla_breached && <WarningIcon fontSize="small" color="error" />}
                              <Typography
                                variant="body2"
                                color={a.sla_breached ? 'error' : a.hours_waiting >= 12 ? 'warning.main' : 'text.primary'}
                                fontWeight={a.sla_breached ? 700 : 400}
                              >
                                {a.hours_waiting}h
                              </Typography>
                            </Box>
                          </Tooltip>
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            color="success"
                            variant="contained"
                            sx={{ mr: 0.5, minWidth: 0, px: 1.5 }}
                            onClick={() => handleApprovalAction(a.id, 'approve')}
                          >
                            Approve
                          </Button>
                          <Button
                            size="small"
                            color="error"
                            variant="outlined"
                            sx={{ minWidth: 0, px: 1.5 }}
                            onClick={() => {
                              const reason = window.prompt('Reason for rejection (optional):') || '';
                              handleApprovalAction(a.id, 'reject', reason);
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

      {/* ════════════════════ TAB 3 — GEOGRAPHIC ════════════════════ */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Members by District</Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={geographic?.by_district || []} layout="vertical" margin={{ left: 80 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
                      <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
                      <RechartsTooltip />
                      <Bar dataKey="count" fill="#1976d2" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Members by Block</Typography>
                <Box height={300}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={geographic?.by_block || []} layout="vertical" margin={{ left: 80 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
                      <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
                      <RechartsTooltip />
                      <Bar dataKey="count" fill="#388e3c" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Gender Split</Typography>
                <Box height={260}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={(geographic?.by_gender || []).filter(d => d.count > 0)}
                        dataKey="count"
                        nameKey="gender"
                        cx="50%" cy="50%"
                        outerRadius={90}
                        label={({ gender, percent }) => `${GENDER_LABELS[gender] || gender} ${(percent * 100).toFixed(0)}%`}
                      >
                        {(geographic?.by_gender || []).map((entry, i) => (
                          <Cell key={i} fill={GENDER_COLORS[entry.gender] || CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Social Category</Typography>
                <Box height={260}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={geographic?.by_social_category || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                      <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                      <RechartsTooltip />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {(geographic?.by_social_category || []).map((_, i) => (
                          <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} mb={2}>Member Type</Typography>
                <Box height={260}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={(geographic?.by_member_type || []).filter(d => d.count > 0)}
                        dataKey="count"
                        nameKey="type"
                        cx="50%" cy="50%"
                        outerRadius={90}
                        label={({ type, percent }) => `${TYPE_LABELS[type] || type} ${(percent * 100).toFixed(0)}%`}
                      >
                        {(geographic?.by_member_type || []).map((entry, i) => (
                          <Cell key={i} fill={TYPE_COLORS[entry.type] || CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
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
