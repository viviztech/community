import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:activ_mobile/config/theme.dart';
import 'package:activ_mobile/providers/auth_provider.dart';
import 'package:activ_mobile/screens/splash_screen.dart';
import 'package:activ_mobile/screens/login_screen.dart';
import 'package:activ_mobile/screens/register_screen.dart';
import 'package:activ_mobile/screens/dashboard_screen.dart';
import 'package:activ_mobile/screens/profile_screen.dart';
import 'package:activ_mobile/screens/events_screen.dart';
import 'package:activ_mobile/screens/memberships_screen.dart';
import 'package:activ_mobile/screens/members_screen.dart';
import 'package:activ_mobile/screens/notifications_screen.dart';

SharedPreferences? prefs;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  prefs = await SharedPreferences.getInstance();
  runApp(const ProviderScope(child: MyApp()));
}

final GoRouter _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      name: 'splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/login',
      name: 'login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/register',
      name: 'register',
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: '/dashboard',
      name: 'dashboard',
      builder: (context, state) => const DashboardScreen(),
    ),
    GoRoute(
      path: '/profile',
      name: 'profile',
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: '/events',
      name: 'events',
      builder: (context, state) => const EventsScreen(),
    ),
    GoRoute(
      path: '/memberships',
      name: 'memberships',
      builder: (context, state) => const MembershipsScreen(),
    ),
    GoRoute(
      path: '/members',
      name: 'members',
      builder: (context, state) => const MembersScreen(),
    ),
    GoRoute(
      path: '/notifications',
      name: 'notifications',
      builder: (context, state) => const NotificationsScreen(),
    ),
  ],
);

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    
    return MaterialApp.router(
      title: 'ACTIV Membership',
      theme: appTheme,
      routerConfig: _router,
      debugShowCheckedModeBanner: false,
    );
  }
}
