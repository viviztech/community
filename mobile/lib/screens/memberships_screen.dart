import 'package:flutter/material.dart';

class MembershipsScreen extends StatelessWidget {
  const MembershipsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Membership Plans')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildMembershipCard('Learner', '0', 'Free', ['Basic profile', 'View events']),
          _buildMembershipCard('Beginner', '500', 'Yearly', ['Full profile', 'Event registration', 'Member directory']),
          _buildMembershipCard('Intermediate', '2000', 'Yearly', ['All Beginner features', 'Business matching', 'Priority support']),
          _buildMembershipCard('Ideal', '10000', 'Lifetime', ['All features', 'Lifetime access', 'VIP support']),
        ],
      ),
    );
  }

  Widget _buildMembershipCard(String name, String price, String type, List<String> features) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(
              name,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              '₹$price',
              style: const TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1976D2),
              ),
            ),
            Text(type, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 16),
            ...features.map((f) => Row(
              children: [
                const Icon(Icons.check, size: 16, color: Colors.green),
                const SizedBox(width: 8),
                Text(f),
              ],
            )),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {},
                child: const Text('Choose Plan'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
