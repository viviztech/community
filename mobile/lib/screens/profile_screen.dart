import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:activ_mobile/providers/member_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final memberState = ref.watch(memberProvider);
    final profile = memberState.profile;
    final TextEditingController orgController = TextEditingController(text: profile?['organization_name'] ?? '');

    return Scaffold(
      appBar: AppBar(title: const Text('My Profile')),
      body: memberState.loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (profile != null) ...[
                    _buildSectionHeader('Personal Details'),
                    _buildDetailRow('Name', '${profile['full_name']}'),
                    _buildDetailRow('Email', '${profile['email']}'),
                    _buildDetailRow('Date of Birth', '${profile['date_of_birth'] ?? 'Not set'}'),
                    _buildDetailRow('Gender', '${profile['gender'] ?? 'Not set'}'),
                    _buildDetailRow('Social Category', '${profile['social_category'] ?? 'Not set'}'),
                    
                    const SizedBox(height: 24),
                    _buildSectionHeader('Address'),
                    _buildDetailRow('Address', '${profile['address_line_1'] ?? ''}'),
                    _buildDetailRow('Pincode', '${profile['pincode'] ?? 'Not set'}'),
                    
                    const SizedBox(height: 24),
                    _buildSectionHeader('Business Details'),
                    _buildDetailRow('Organization', '${profile['organization_name'] ?? 'Not set'}'),
                    _buildDetailRow('Constitution', '${profile['constitution'] ?? 'Not set'}'),
                    _buildDetailRow('PAN', '${profile['pan_number'] ?? 'Not set'}'),
                    _buildDetailRow('GST', '${profile['gst_number'] ?? 'Not set'}'),
                    _buildDetailRow('Udyam', '${profile['udyam_number'] ?? 'Not set'}'),
                    
                    const SizedBox(height: 24),
                    Center(
                      child: ElevatedButton(
                        onPressed: () {
                          ref.read(memberProvider.notifier).updateProfile({
                            'organization_name': orgController.text,
                          });
                        },
                        child: const Text('Save Changes'),
                      ),
                    ),
                  ] else ...[
                    const Center(child: Text('No profile data available')),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const Divider(),
        const SizedBox(height: 8),
      ],
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
