import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Avatar,
  Chip,
  IconButton,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search as SearchIcon,
  MoreVert as MoreVertIcon,
  PersonAdd as PersonAddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { fetchMembers, fetchMemberById } from '../store/slices/memberSlice';

export default function Members() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { members, loading, totalCount, currentMember } = useSelector((state) => state.members);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedMember, setSelectedMember] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchMembers({ page: page + 1, search }));
  }, [dispatch, page, search]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuOpen = (event, member) => {
    setAnchorEl(event.currentTarget);
    setSelectedMember(member);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAddMember = () => {
    navigate('/register');
  };

  const handleViewDetails = () => {
    setViewDialogOpen(true);
    handleMenuClose();
  };

  const handleEdit = () => {
    setEditDialogOpen(true);
    handleMenuClose();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'pending': return 'warning';
      case 'expired': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Members Directory
          </Typography>
          <Typography color="text.secondary">
            Browse and manage ACTIV members
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<PersonAddIcon />} onClick={handleAddMember}>
          Add Member
        </Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search members by name, email, or organization..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{ maxWidth: 400 }}
          />
        </CardContent>
      </Card>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Member</TableCell>
                <TableCell>Organization</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" py={4}>
                    Loading...
                  </TableCell>
                </TableRow>
              ) : members.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" py={4}>
                    No members found
                  </TableCell>
                </TableRow>
              ) : (
                members.map((member) => (
                  <TableRow key={member.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                          {member.user?.first_name?.[0] || 'M'}
                        </Avatar>
                        <Box>
                          <Typography fontWeight={500}>
                            {member.user?.full_name || 'N/A'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {member.user?.email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography fontWeight={500}>
                        {member.organization_name || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {member.district?.name || member.block?.name || 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={member.social_category || 'N/A'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={member.status || 'Active'}
                        color={getStatusColor(member.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton onClick={(e) => handleMenuOpen(e, member)}>
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Card>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleViewDetails}>
          <ListItemIcon><ViewIcon fontSize="small" /></ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleEdit}>
          <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
}
