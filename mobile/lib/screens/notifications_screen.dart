import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:activ_mobile/providers/notification_provider.dart';
import 'package:intl/intl.dart';

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notificationState = ref.watch(notificationProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          if (notificationState.unreadCount > 0)
            TextButton(
              onPressed: () {},
              child: const Text('Mark all read'),
            ),
        ],
      ),
      body: notificationState.loading
          ? const Center(child: CircularProgressIndicator())
          : notificationState.notifications.isEmpty
              ? const Center(child: Text('No notifications'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: notificationState.notifications.length,
                  itemBuilder: (context, index) {
                    final notification = notificationState.notifications[index];
                    final isUnread = notification['status'] == 'sent';
                    return Card(
                      color: isUnread ? Colors.blue[50] : Colors.white,
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: isUnread ? Colors.blue : Colors.grey,
                          child: const Icon(
                            Icons.notifications,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                        title: Text(
                          notification['body'] ?? 'Notification',
                          style: TextStyle(
                            fontWeight: isUnread ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                        subtitle: Text(
                          DateFormat('dd MMM yyyy, hh:mm a').format(
                            DateTime.parse(notification['created_at']),
                          ),
                        ),
                        onTap: isUnread ? () {} : null,
                      ),
                    );
                  },
                ),
    );
  }
}
