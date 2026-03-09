import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Typography,
  Link,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Button,
} from '@mui/material';
import { Email, ArrowBack, Visibility, VisibilityOff } from '@mui/icons-material';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [isResetMode, setIsResetMode] = useState(false);
  const dispatch = useDispatch();
  const { loading, error, successMessage } = useSelector((state) => state.auth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isResetMode) {
      if (newPassword !== confirmPassword) {
        alert('Passwords do not match');
        return;
      }
    } else {
      // Handle forgot password request
      console.log('Forgot password request for:', email);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 440, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Box textAlign="center" mb={4}>
            <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
              {isResetMode ? 'Reset Password' : 'Forgot Password'}
            </Typography>
            <Typography color="text.secondary">
              {isResetMode
                ? 'Enter your new password'
                : 'Enter your email to reset your password'}
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </Alert>
          )}

          {successMessage && (
            <Alert severity="success" sx={{ mb: 3 }}>
              {successMessage}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
            />

            {isResetMode && (
              <>
                <TextField
                  fullWidth
                  label="New Password"
                  type={showPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  margin="normal"
                  required
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  label="Confirm New Password"
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  margin="normal"
                  required
                />
              </>
            )}

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2, py: 1.5 }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : isResetMode ? (
                'Reset Password'
              ) : (
                'Send Reset Link'
              )}
            </Button>
          </form>

          <Box textAlign="center" mt={3}>
            <Link
              component={RouterLink}
              to="/login"
              fontWeight={500}
              sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}
            >
              <ArrowBack fontSize="small" /> Back to Login
            </Link>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
