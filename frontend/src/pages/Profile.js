import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box, Card, CardContent, Typography, TextField, Button, Grid, Avatar,
  Alert, CircularProgress, MenuItem, Divider, Chip, LinearProgress,
  Tabs, Tab, IconButton, List, ListItem, ListItemText, ListItemSecondaryAction,
  FormControlLabel, Checkbox, Tooltip,
} from '@mui/material';
import {
  PhotoCamera, Upload as UploadIcon, CheckCircle, Cancel, HourglassEmpty,
  CloudUpload,
} from '@mui/icons-material';
import { fetchMemberProfile, updateMemberProfile } from '../store/slices/memberSlice';
import { fetchCurrentUser } from '../store/slices/authSlice';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// ── Option lists ────────────────────────────────────────────────────────────
const MEMBER_TYPES = [
  { value: 'individual', label: 'Individual' },
  { value: 'shg', label: 'Self Help Group (SHG)' },
  { value: 'fpo', label: 'Farmer Producer Organisation (FPO)' },
];
const GENDERS = [{ value: 'M', label: 'Male' }, { value: 'F', label: 'Female' }, { value: 'O', label: 'Other' }];
const SOCIAL_CATEGORIES = [
  { value: 'SC', label: 'Scheduled Caste' },
  { value: 'ST', label: 'Scheduled Tribe' },
  { value: 'CC', label: 'Converted Christians from SC' },
  { value: 'OBC', label: 'Other Backward Class' },
  { value: 'O', label: 'Others' },
];
const CONSTITUTIONS = [
  { value: 'PROP', label: 'Proprietorship' }, { value: 'PART', label: 'Partnership' },
  { value: 'PVT', label: 'Private Limited' }, { value: 'PUB', label: 'Public Limited' },
  { value: 'OPC', label: 'One Person Company' }, { value: 'LLP', label: 'Limited Liability Partnership' },
  { value: 'TRUST', label: 'Trust' }, { value: 'SOC', label: 'Society' },
];
const BUSINESS_TYPES = [
  { value: 'M', label: 'Manufacturing' }, { value: 'S', label: 'Service' },
  { value: 'T', label: 'Trader' }, { value: 'D', label: 'Dealer' },
];
const TURNOVER_RANGES = [
  { value: '<40L', label: '< 40 Lakhs' }, { value: '<1CR', label: '40 Lakhs – 1 Crore' },
  { value: '<5CR', label: '1 – 5 Crore' }, { value: '<50CR', label: '5 – 50 Crore' },
  { value: '<250CR', label: '50 – 250 Crore' }, { value: '<500CR', label: '250 – 500 Crore' },
  { value: '>1000CR', label: '> 1000 Crore' },
];

const DOCUMENT_TYPES = {
  individual: [
    { value: 'aadhaar', label: 'Aadhaar Card', required: true },
    { value: 'pan', label: 'PAN Card', required: true },
    { value: 'gst', label: 'GST Certificate', required: false },
    { value: 'udyam', label: 'Udyam Certificate', required: false },
    { value: 'itr', label: 'Income Tax Return', required: false },
    { value: 'business_reg', label: 'Business Registration', required: false },
  ],
  shg: [
    { value: 'aadhaar', label: 'Aadhaar Card (President)', required: true },
    { value: 'pan', label: 'PAN Card', required: true },
    { value: 'shg_reg', label: 'SHG Registration Certificate', required: true },
    { value: 'shg_bank', label: 'SHG Bank Passbook', required: true },
    { value: 'shg_members', label: 'SHG Member List', required: false },
    { value: 'other', label: 'Other', required: false },
  ],
  fpo: [
    { value: 'aadhaar', label: 'Aadhaar Card (CEO)', required: true },
    { value: 'pan', label: 'PAN Card', required: true },
    { value: 'fpo_reg', label: 'FPO Registration Certificate', required: true },
    { value: 'fpo_bylaw', label: 'FPO By-Laws', required: true },
    { value: 'fpo_shareholders', label: 'Shareholder List', required: false },
    { value: 'gst', label: 'GST Certificate', required: false },
  ],
};

const DOC_STATUS_ICON = {
  verified: <CheckCircle color="success" fontSize="small" />,
  rejected: <Cancel color="error" fontSize="small" />,
  pending: <HourglassEmpty color="warning" fontSize="small" />,
  not_uploaded: <CloudUpload color="disabled" fontSize="small" />,
};

// ── Initial form state ───────────────────────────────────────────────────────
const EMPTY_FORM = {
  member_type: 'individual',
  date_of_birth: '', gender: '', social_category: '',
  address_line_1: '', address_line_2: '', pincode: '',
  educational_qualification: '', occupation: '',
  // Individual
  is_doing_business: false, organization_name: '', constitution: '',
  business_type: '', business_activities: '', business_commencement_year: '',
  number_of_employees: '', pan_number: '', gst_number: '', udyam_number: '',
  msme_registered: false, msme_number: '', nsic_registered: false, nsic_number: '',
  gst_registered: false, ie_code: '', has_filed_itr: false, itr_filing_years: '',
  turnover_range: '', member_of_other_chambers: false, other_chamber_details: '',
  // SHG
  shg_name: '', shg_registration_number: '', shg_formation_date: '',
  shg_member_count: '', shg_bank_linked: false, shg_bank_name: '',
  shg_bank_account_number: '', shg_promoting_institution: '', shg_federation_name: '',
  // FPO
  fpo_name: '', fpo_registration_number: '', fpo_registration_date: '',
  fpo_farmer_count: '', fpo_total_land_area_acres: '', fpo_crop_types: '',
  fpo_annual_turnover: '', fpo_ceo_name: '', fpo_ceo_phone: '', fpo_commodity: '',
};

export default function Profile() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { profile, loading, error } = useSelector((state) => state.members);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [tabValue, setTabValue] = useState(0);
  const [success, setSuccess] = useState(false);
  const [docUploading, setDocUploading] = useState(false);
  const [docError, setDocError] = useState('');
  const [docSuccess, setDocSuccess] = useState('');
  const [documents, setDocuments] = useState([]);
  const fileInputRef = useRef(null);
  const photoInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [selectedDocType, setSelectedDocType] = useState('');

  useEffect(() => { dispatch(fetchMemberProfile()); }, [dispatch]);

  useEffect(() => {
    if (profile) {
      setFormData({
        ...EMPTY_FORM,
        member_type: profile.member_type || 'individual',
        date_of_birth: profile.date_of_birth || '',
        gender: profile.gender || '',
        social_category: profile.social_category || '',
        address_line_1: profile.address_line_1 || '',
        address_line_2: profile.address_line_2 || '',
        pincode: profile.pincode || '',
        educational_qualification: profile.educational_qualification || '',
        occupation: profile.occupation || '',
        is_doing_business: profile.is_doing_business || false,
        organization_name: profile.organization_name || '',
        constitution: profile.constitution || '',
        business_type: profile.business_type || '',
        business_activities: profile.business_activities || '',
        business_commencement_year: profile.business_commencement_year || '',
        number_of_employees: profile.number_of_employees || '',
        pan_number: profile.pan_number || '',
        gst_number: profile.gst_number || '',
        udyam_number: profile.udyam_number || '',
        msme_registered: profile.msme_registered || false,
        msme_number: profile.msme_number || '',
        nsic_registered: profile.nsic_registered || false,
        nsic_number: profile.nsic_number || '',
        gst_registered: profile.gst_registered || false,
        ie_code: profile.ie_code || '',
        has_filed_itr: profile.has_filed_itr || false,
        itr_filing_years: profile.itr_filing_years || '',
        turnover_range: profile.turnover_range || '',
        member_of_other_chambers: profile.member_of_other_chambers || false,
        other_chamber_details: profile.other_chamber_details || '',
        shg_name: profile.shg_name || '',
        shg_registration_number: profile.shg_registration_number || '',
        shg_formation_date: profile.shg_formation_date || '',
        shg_member_count: profile.shg_member_count || '',
        shg_bank_linked: profile.shg_bank_linked || false,
        shg_bank_name: profile.shg_bank_name || '',
        shg_bank_account_number: profile.shg_bank_account_number || '',
        shg_promoting_institution: profile.shg_promoting_institution || '',
        shg_federation_name: profile.shg_federation_name || '',
        fpo_name: profile.fpo_name || '',
        fpo_registration_number: profile.fpo_registration_number || '',
        fpo_registration_date: profile.fpo_registration_date || '',
        fpo_farmer_count: profile.fpo_farmer_count || '',
        fpo_total_land_area_acres: profile.fpo_total_land_area_acres || '',
        fpo_crop_types: profile.fpo_crop_types || '',
        fpo_annual_turnover: profile.fpo_annual_turnover || '',
        fpo_ceo_name: profile.fpo_ceo_name || '',
        fpo_ceo_phone: profile.fpo_ceo_phone || '',
        fpo_commodity: profile.fpo_commodity || '',
      });
      setDocuments(profile.documents || []);
    }
  }, [profile]);

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    setSuccess(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(updateMemberProfile(formData)).then((res) => {
      if (!res.error) setSuccess(true);
    });
  };

  const handlePhotoChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append('profile_image', file);
    try {
      const token = localStorage.getItem('accessToken');
      await axios.put(`${API_URL}/auth/profile/`, fd, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' },
      });
      dispatch(fetchCurrentUser());
    } catch (err) { /* silent */ }
    finally { setUploading(false); }
  };

  const handleDocUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedDocType) return;
    setDocUploading(true);
    setDocError('');
    setDocSuccess('');
    const fd = new FormData();
    fd.append('file', file);
    fd.append('document_type', selectedDocType);
    try {
      const token = localStorage.getItem('accessToken');
      await axios.post(`${API_URL}/members/documents/`, fd, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' },
      });
      setDocSuccess(`${selectedDocType.toUpperCase()} uploaded successfully.`);
      dispatch(fetchMemberProfile());
    } catch (err) {
      setDocError(err.response?.data?.error || 'Upload failed.');
    } finally {
      setDocUploading(false);
      fileInputRef.current.value = '';
    }
  };

  const docTypes = DOCUMENT_TYPES[formData.member_type] || DOCUMENT_TYPES.individual;
  const completionPct = profile?.profile_completion_percentage || 0;

  const SelectField = ({ label, name, options, required = false }) => (
    <TextField fullWidth select label={label} name={name} value={formData[name]} onChange={handleChange} required={required}>
      <MenuItem value="">Select</MenuItem>
      {options.map((o) => <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>)}
    </TextField>
  );

  const Field = ({ label, name, type = 'text', required = false, helperText = '' }) => (
    <TextField fullWidth label={label} name={name} type={type} value={formData[name]}
      onChange={handleChange} required={required} helperText={helperText}
      InputLabelProps={type === 'date' ? { shrink: true } : undefined} />
  );

  const Check = ({ label, name }) => (
    <FormControlLabel control={<Checkbox checked={!!formData[name]} onChange={handleChange} name={name} />} label={label} />
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>My Profile</Typography>
          <Typography color="text.secondary">Manage your personal and business information</Typography>
        </Box>
        <Box textAlign="right">
          <Typography variant="body2" color="text.secondary" mb={0.5}>
            Profile Completion: {completionPct}%
          </Typography>
          <LinearProgress variant="determinate" value={completionPct} sx={{ width: 200, height: 8, borderRadius: 4 }}
            color={completionPct >= 80 ? 'success' : completionPct >= 50 ? 'warning' : 'error'} />
        </Box>
      </Box>

      {success && <Alert severity="success" sx={{ mb: 3 }}>Profile updated successfully!</Alert>}
      {error && <Alert severity="error" sx={{ mb: 3 }}>{typeof error === 'string' ? error : JSON.stringify(error)}</Alert>}

      {/* Profile Photo */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center">
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'primary.main' }}
              src={user?.profile_image ? `${API_URL.replace('/api/v1', '')}${user.profile_image}` : undefined}>
              {user?.first_name?.[0] || 'U'}
            </Avatar>
            <Box>
              <Typography variant="h6">{user?.full_name}</Typography>
              <Typography color="text.secondary" variant="body2">{user?.email}</Typography>
              <Chip label={MEMBER_TYPES.find(t => t.value === formData.member_type)?.label || 'Individual'}
                color="primary" size="small" sx={{ mt: 1 }} />
              <input type="file" ref={photoInputRef} style={{ display: 'none' }} accept="image/*" onChange={handlePhotoChange} />
              <Button startIcon={uploading ? <CircularProgress size={16} /> : <PhotoCamera />}
                onClick={() => photoInputRef.current.click()} sx={{ mt: 1, ml: 1 }} disabled={uploading} size="small">
                Change Photo
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Personal Info" />
        <Tab label={formData.member_type === 'shg' ? 'SHG Details' : formData.member_type === 'fpo' ? 'FPO Details' : 'Business Info'} />
        <Tab label="Documents" />
      </Tabs>

      <form onSubmit={handleSubmit}>
        {/* ── TAB 0: Personal Info ─────────────────────────────────────── */}
        {tabValue === 0 && (
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" fontWeight={600} mb={3}>Member Type</Typography>
              <Grid container spacing={3} mb={4}>
                <Grid item xs={12} sm={6}>
                  <SelectField label="Member Type" name="member_type" options={MEMBER_TYPES} required />
                </Grid>
              </Grid>

              <Divider sx={{ mb: 3 }} />
              <Typography variant="h6" fontWeight={600} mb={3}>Personal Information</Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}><Field label="Date of Birth" name="date_of_birth" type="date" /></Grid>
                <Grid item xs={12} sm={6}><SelectField label="Gender" name="gender" options={GENDERS} /></Grid>
                <Grid item xs={12} sm={6}><SelectField label="Social Category" name="social_category" options={SOCIAL_CATEGORIES} /></Grid>
                <Grid item xs={12} sm={6}><Field label="Educational Qualification" name="educational_qualification" /></Grid>
                <Grid item xs={12} sm={6}><Field label="Occupation" name="occupation" /></Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" fontWeight={600} mb={3}>Address</Typography>
              <Grid container spacing={3}>
                <Grid item xs={12}><Field label="Address Line 1" name="address_line_1" /></Grid>
                <Grid item xs={12}><Field label="Address Line 2" name="address_line_2" /></Grid>
                <Grid item xs={12} sm={4}><Field label="Pincode" name="pincode" /></Grid>
              </Grid>

              <Box mt={4}>
                <Button type="submit" variant="contained" size="large" disabled={loading}>
                  {loading ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* ── TAB 1: Business / SHG / FPO ─────────────────────────────── */}
        {tabValue === 1 && (
          <Card>
            <CardContent sx={{ p: 4 }}>
              {/* ── INDIVIDUAL ── */}
              {formData.member_type === 'individual' && (
                <>
                  <Typography variant="h6" fontWeight={600} mb={3}>Business Details</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12}><Check label="Currently doing business" name="is_doing_business" /></Grid>
                    <Grid item xs={12}><Field label="Organization Name" name="organization_name" /></Grid>
                    <Grid item xs={12} sm={6}><SelectField label="Constitution" name="constitution" options={CONSTITUTIONS} /></Grid>
                    <Grid item xs={12} sm={6}><SelectField label="Business Type" name="business_type" options={BUSINESS_TYPES} /></Grid>
                    <Grid item xs={12}><Field label="Business Activities" name="business_activities" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Commencement Year" name="business_commencement_year" type="number" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Number of Employees" name="number_of_employees" type="number" /></Grid>
                    <Grid item xs={12} sm={6}><SelectField label="Turnover Range" name="turnover_range" options={TURNOVER_RANGES} /></Grid>
                  </Grid>

                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" fontWeight={600} mb={3}>Registration Numbers</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}><Field label="PAN Number" name="pan_number" helperText="e.g. ABCDE1234F" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="GST Number" name="gst_number" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Udyam Number (Optional)" name="udyam_number" helperText="e.g. UDYAM-TN-01-0000001" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="IE Code" name="ie_code" /></Grid>
                    <Grid item xs={12} sm={6}><Check label="MSME Registered" name="msme_registered" /></Grid>
                    {formData.msme_registered && <Grid item xs={12} sm={6}><Field label="MSME Number" name="msme_number" /></Grid>}
                    <Grid item xs={12} sm={6}><Check label="NSIC Registered" name="nsic_registered" /></Grid>
                    {formData.nsic_registered && <Grid item xs={12} sm={6}><Field label="NSIC Number" name="nsic_number" /></Grid>}
                    <Grid item xs={12} sm={6}><Check label="Filed ITR" name="has_filed_itr" /></Grid>
                    {formData.has_filed_itr && <Grid item xs={12} sm={6}><Field label="ITR Filing Years" name="itr_filing_years" type="number" /></Grid>}
                  </Grid>
                </>
              )}

              {/* ── SHG ── */}
              {formData.member_type === 'shg' && (
                <>
                  <Typography variant="h6" fontWeight={600} mb={3}>SHG Details</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}><Field label="SHG Name *" name="shg_name" required /></Grid>
                    <Grid item xs={12} sm={6}><Field label="SHG Registration Number *" name="shg_registration_number" required /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Formation Date" name="shg_formation_date" type="date" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Number of Members" name="shg_member_count" type="number" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Promoting Institution" name="shg_promoting_institution" helperText="e.g. NABARD, NGO name" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Federation Name" name="shg_federation_name" /></Grid>
                  </Grid>

                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" fontWeight={600} mb={3}>Bank Linkage</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12}><Check label="Bank Linked" name="shg_bank_linked" /></Grid>
                    {formData.shg_bank_linked && (
                      <>
                        <Grid item xs={12} sm={6}><Field label="Bank Name" name="shg_bank_name" /></Grid>
                        <Grid item xs={12} sm={6}><Field label="Account Number" name="shg_bank_account_number" /></Grid>
                      </>
                    )}
                  </Grid>

                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" fontWeight={600} mb={3}>Tax & Registration</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}><Field label="PAN Number" name="pan_number" helperText="e.g. ABCDE1234F" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Udyam Number (Optional)" name="udyam_number" helperText="e.g. UDYAM-TN-01-0000001" /></Grid>
                  </Grid>
                </>
              )}

              {/* ── FPO ── */}
              {formData.member_type === 'fpo' && (
                <>
                  <Typography variant="h6" fontWeight={600} mb={3}>FPO Details</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}><Field label="FPO Name *" name="fpo_name" required /></Grid>
                    <Grid item xs={12} sm={6}><Field label="FPO Registration Number *" name="fpo_registration_number" required /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Registration Date" name="fpo_registration_date" type="date" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Number of Farmers" name="fpo_farmer_count" type="number" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Total Land Area (Acres)" name="fpo_total_land_area_acres" type="number" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Primary Commodity" name="fpo_commodity" /></Grid>
                    <Grid item xs={12}><Field label="Crop Types" name="fpo_crop_types" helperText="Comma-separated: e.g. Rice, Wheat, Sugarcane" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Annual Turnover (₹)" name="fpo_annual_turnover" type="number" /></Grid>
                  </Grid>

                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" fontWeight={600} mb={3}>CEO / Representative</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}><Field label="CEO Name" name="fpo_ceo_name" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="CEO Phone" name="fpo_ceo_phone" /></Grid>
                  </Grid>

                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" fontWeight={600} mb={3}>Tax & Registration</Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}><Field label="PAN Number" name="pan_number" helperText="e.g. ABCDE1234F" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="GST Number" name="gst_number" /></Grid>
                    <Grid item xs={12} sm={6}><Field label="Udyam Number (Optional)" name="udyam_number" helperText="e.g. UDYAM-TN-01-0000001" /></Grid>
                  </Grid>
                </>
              )}

              <Box mt={4}>
                <Button type="submit" variant="contained" size="large" disabled={loading}>
                  {loading ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* ── TAB 2: Documents ─────────────────────────────────────────── */}
        {tabValue === 2 && (
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" fontWeight={600} mb={1}>Document Upload</Typography>
              <Typography color="text.secondary" variant="body2" mb={3}>
                Documents marked <strong>Required</strong> must be verified before your membership is approved.
                Udyam registration is optional.
              </Typography>

              {docError && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setDocError('')}>{docError}</Alert>}
              {docSuccess && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setDocSuccess('')}>{docSuccess}</Alert>}

              {/* Upload section */}
              <Box display="flex" gap={2} alignItems="center" mb={4} flexWrap="wrap">
                <TextField select label="Select Document Type" value={selectedDocType}
                  onChange={(e) => setSelectedDocType(e.target.value)} sx={{ minWidth: 260 }} size="small">
                  <MenuItem value="">-- Choose --</MenuItem>
                  {docTypes.map((d) => (
                    <MenuItem key={d.value} value={d.value}>
                      {d.label} {d.required ? '(Required)' : '(Optional)'}
                    </MenuItem>
                  ))}
                </TextField>
                <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleDocUpload}
                  accept=".pdf,.jpg,.jpeg,.png" />
                <Button variant="contained" startIcon={docUploading ? <CircularProgress size={16} color="inherit" /> : <UploadIcon />}
                  onClick={() => selectedDocType && fileInputRef.current.click()}
                  disabled={!selectedDocType || docUploading}>
                  Upload File
                </Button>
              </Box>

              {/* Document status list */}
              <Typography variant="subtitle1" fontWeight={600} mb={2}>Required Documents</Typography>
              <List disablePadding>
                {docTypes.filter(d => d.required).map((docType) => {
                  const uploaded = documents.find(d => d.document_type === docType.value);
                  const statusKey = uploaded?.status || 'not_uploaded';
                  return (
                    <ListItem key={docType.value} divider sx={{ px: 0 }}>
                      <ListItemText
                        primary={<Box display="flex" alignItems="center" gap={1}>
                          {DOC_STATUS_ICON[statusKey]}
                          <span>{docType.label}</span>
                          <Chip label="Required" size="small" color="error" variant="outlined" />
                        </Box>}
                        secondary={uploaded
                          ? `Uploaded: ${uploaded.original_filename} — Status: ${uploaded.status_display || uploaded.status}`
                          : 'Not uploaded yet'}
                      />
                      {uploaded?.status === 'rejected' && (
                        <ListItemSecondaryAction>
                          <Tooltip title={uploaded.notes || 'Rejected'}>
                            <Chip label="Rejected — Re-upload" size="small" color="error"
                              onClick={() => { setSelectedDocType(docType.value); fileInputRef.current.click(); }} />
                          </Tooltip>
                        </ListItemSecondaryAction>
                      )}
                    </ListItem>
                  );
                })}
              </List>

              {docTypes.some(d => !d.required) && (
                <>
                  <Typography variant="subtitle1" fontWeight={600} mt={3} mb={2}>Optional Documents</Typography>
                  <List disablePadding>
                    {docTypes.filter(d => !d.required).map((docType) => {
                      const uploaded = documents.find(d => d.document_type === docType.value);
                      const statusKey = uploaded?.status || 'not_uploaded';
                      return (
                        <ListItem key={docType.value} divider sx={{ px: 0 }}>
                          <ListItemText
                            primary={<Box display="flex" alignItems="center" gap={1}>
                              {DOC_STATUS_ICON[statusKey]}
                              <span>{docType.label}</span>
                              <Chip label="Optional" size="small" variant="outlined" />
                            </Box>}
                            secondary={uploaded
                              ? `Uploaded: ${uploaded.original_filename} — Status: ${uploaded.status_display || uploaded.status}`
                              : 'Not uploaded yet'}
                          />
                        </ListItem>
                      );
                    })}
                  </List>
                </>
              )}
            </CardContent>
          </Card>
        )}
      </form>
    </Box>
  );
}
