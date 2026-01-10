import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:activ_mobile/providers/event_provider.dart';
import 'package:intl/intl.dart';

class EventsScreen extends ConsumerWidget {
  const EventsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventState = ref.watch(eventProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Events')),
      body: eventState.loading
          ? const Center(child: CircularProgressIndicator())
          : eventState.events.isEmpty
              ? const Center(child: Text('No events available'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: eventState.events.length,
                  itemBuilder: (context, index) {
                    final event = eventState.events[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 16),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    event['title'] ?? 'Untitled',
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                Chip(
                                  label: Text(
                                    event['ticket_price'] > 0
                                        ? '₹${event['ticket_price']}'
                                        : 'Free',
                                  ),
                                  color: event['ticket_price'] > 0
                                      ? WidgetStateProperty.all(Colors.blue)
                                      : WidgetStateProperty.all(Colors.green),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                const Icon(Icons.calendar_today, size: 16),
                                const SizedBox(width: 4),
                                Text(
                                  DateFormat('dd MMM yyyy, hh:mm a').format(
                                    DateTime.parse(event['event_date']),
                                  ),
                                  style: const TextStyle(color: Colors.grey),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                const Icon(Icons.location_on, size: 16),
                                const SizedBox(width: 4),
                                Text(
                                  event['venue'] ?? 'Venue not specified',
                                  style: const TextStyle(color: Colors.grey),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            Text(
                              event['description'] ?? '',
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(color: Colors.grey),
                            ),
                            const SizedBox(height: 12),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () {},
                                child: const Text('Register Now'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
