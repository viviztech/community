import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:activ_mobile/providers/auth_provider.dart';
import 'package:activ_mobile/providers/member_provider.dart';
import 'package:activ_mobile/providers/event_provider.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final memberState = ref.watch(memberProvider);
    final eventState = ref.watch(eventProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => ref.read(authProvider.notifier).logout(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Welcome, ${authState.user?['first_name'] ?? 'Member'}!',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            _buildStatCard(
              'Profile Completion',
              '${memberState.profile?['profile_completion_percentage'] ?? 0}%',
              Icons.person,
              Colors.blue,
            ),
            const SizedBox(height: 16),
            _buildStatCard(
              'Upcoming Events',
              '${eventState.events.length}',
              Icons.event,
              Colors.orange,
            ),
            const SizedBox(height: 24),
            const Text(
              'Quick Actions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            GridView.count(
              shrinkWrap: true,
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildActionCard(context, 'Profile', Icons.edit, '/profile'),
                _buildActionCard(context, 'Events', Icons.event, '/events'),
                _buildActionCard(context, 'Memberships', Icons.card_membership, '/memberships'),
                _buildActionCard(context, 'Members', Icons.people, '/members'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, color: Colors.grey)),
                Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(BuildContext context, String title, IconData icon, String route) {
    return Card(
      child: InkWell(
        onTap: () => context.go(route),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 32, color: const Color(0xFF1976D2)),
              const SizedBox(height: 8),
              Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ),
    );
  }
}
