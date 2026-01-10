import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Avatar,
  Alert,
  CircularProgress,
  MenuItem,
  Divider,
} from '@mui/material';
import { PhotoCamera } from '@mui/icons-material';
import { fetchMemberProfile, updateMemberProfile } from '../store/slices/memberSlice';

const genderOptions = [
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' },
  { value: 'O', label: 'Other' },
];

const socialCategoryOptions = [
  { value: 'SC', label: 'Scheduled Caste' },
  { value: 'ST', label: 'Scheduled Tribe' },
  { value: 'CC', label: 'Converted Christians from SC' },
  { value: 'OBC', label: 'Other Backward Class' },
  { value: 'O', label: 'Others' },
];

const constitutionOptions = [
  { value: 'PROP', label: 'Proprietorship' },
  { value: 'PART', label: 'Partnership' },
  { value: 'PVT', label: 'Private Limited' },
  { value: 'PUB', label: 'Public Limited' },
  { value: 'OPC', label: 'One Person Company' },
  { value: 'LLP', label: 'Limited Liability Partnership' },
  { value: 'TRUST', label: 'Trust' },
  { value: 'SOC', label: 'Society' },
];

export default function Profile() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { profile, loading, error } = useSelector((state) => state.members);
  const [formData, setFormData] = useState({
    date_of_birth: '',
    gender: '',
    social_category: '',
    address_line_1: '',
    address_line_2: '',
    pincode: '',
    educational_qualification: '',
    organization_name: '',
    constitution: '',
    pan_number: '',
    gst_number: '',
    udyam_number: '',
    msme_registered: false,
    msme_number: '',
    gst_registered: false,
  });
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    dispatch(fetchMemberProfile());
  }, [dispatch]);

  useEffect(() => {
    if (profile) {
      setFormData({
        date_of_birth: profile.date_of_birth || '',
        gender: profile.gender || '',
        social_category: profile.social_category || '',
        address_line_1: profile.address_line_1 || '',
        address_line_2: profile.address_line_2 || '',
        pincode: profile.pincode || '',
        educational_qualification: profile.educational_qualification || '',
        organization_name: profile.organization_name || '',
        constitution: profile.constitution || '',
        pan_number: profile.pan_number || '',
        gst_number: profile.gst_number || '',
        udyam_number: profile.udyam_number || '',
        msme_registered: profile.msme_registered || false,
        msme_number: profile.msme_number || '',
        gst_registered: profile.gst_registered || false,
      });
    }
  }, [profile]);

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
    setSuccess(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(updateMemberProfile(formData)).then(() => {
      setSuccess(true);
    });
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        My Profile
      </Typography>
      <Typography color="text.secondary" mb={4}>
        Manage your personal and business information
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Profile updated successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 4 }}>
          <Box display="flex" alignItems="center" mb={4}>
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'primary.main' }}>
              {user?.first_name?.[0] || 'U'}
            </Avatar>
            <Box>
              <Typography variant="h6">{user?.full_name}</Typography>
              <Typography color="text.secondary">{user?.email}</Typography>
              <Button startIcon={<PhotoCamera />} sx={{ mt: 1 }}>
                Change Photo
              </Button>
            </Box>
          </Box>

          <Divider sx={{ mb: 4 }} />

          <form onSubmit={handleSubmit}>
            <Typography variant="h6" fontWeight={600} mb={3}>
              Personal Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Date of Birth"
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                >
                  <MenuItem value="">Select</MenuItem>
                  {genderOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Social Category"
                  name="social_category"
                  value={formData.social_category}
                  onChange={handleChange}
                >
                  <MenuItem value="">Select</MenuItem>
                  {socialCategoryOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Educational Qualification"
                  name="educational_qualification"
                  value={formData.educational_qualification}
                  onChange={handleChange}
                />
              </Grid>
            </Grid>

            <Typography variant="h6" fontWeight={600} mt={4} mb={3}>
              Address Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address Line 1"
                  name="address_line_1"
                  value={formData.address_line_1}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address Line 2"
                  name="address_line_2"
                  value={formData.address_line_2}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Pincode"
                  name="pincode"
                  value={formData.pincode}
                  onChange={handleChange}
                />
              </Grid>
            </Grid>

            <Typography variant="h6" fontWeight={600} mt={4} mb={3}>
              Business Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Organization Name"
                  name="organization_name"
                  value={formData.organization_name}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Constitution"
                  name="constitution"
                  value={formData.constitution}
                  onChange={handleChange}
                >
                  <MenuItem value="">Select</MenuItem>
                  {constitutionOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
            </Grid>

            <Typography variant="h6" fontWeight={600} mt={4} mb={3}>
              Registration Numbers
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="PAN Number"
                  name="pan_number"
                  value={formData.pan_number}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="GST Number"
                  name="gst_number"
                  value={formData.gst_number}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Udyam Number"
                  name="udyam_number"
                  value={formData.udyam_number}
                  onChange={handleChange}
                />
              </Grid>
            </Grid>

            <Box mt={4}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
