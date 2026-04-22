import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import memberReducer from './slices/memberSlice';
import eventReducer from './slices/eventSlice';
import membershipReducer from './slices/membershipSlice';
import notificationReducer from './slices/notificationSlice';
import adminReducer from './slices/adminSlice';
import paymentsReducer from './slices/paymentsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    members: memberReducer,
    events: eventReducer,
    memberships: membershipReducer,
    notifications: notificationReducer,
    admin: adminReducer,
    payments: paymentsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;
