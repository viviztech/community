import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:activ_mobile/providers/member_provider.dart';

class MembersScreen extends ConsumerWidget {
  const MembersScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final memberState = ref.watch(memberProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Members Directory')),
      body: memberState.loading
          ? const Center(child: CircularProgressIndicator())
          : memberState.members.isEmpty
              ? const Center(child: Text('No members found'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: memberState.members.length,
                  itemBuilder: (context, index) {
                    final member = memberState.members[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: const Color(0xFF1976D2),
                          child: Text(
                            (member['full_name'] ?? 'M')[0].toUpperCase(),
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),
                        title: Text(member['full_name'] ?? 'Unknown'),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(member['email'] ?? ''),
                            Text(member['organization_name'] ?? 'No organization'),
                          ],
                        ),
                        trailing: Chip(
                          label: Text(member['social_category'] ?? '-'),
                          size: Small,
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
