import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class NotificationState {
  final List<dynamic> notifications;
  final int unreadCount;
  final bool loading;

  NotificationState({this.notifications = const [], this.unreadCount = 0, this.loading = false});

  NotificationState copyWith({notifications, unreadCount, loading}) {
    return NotificationState(
      notifications: notifications ?? this.notifications,
      unreadCount: unreadCount ?? this.unreadCount,
      loading: loading ?? this.loading,
    );
  }
}

class NotificationProvider extends StateNotifier<NotificationState> {
  static const String _baseUrl = 'http://localhost:8000/api/v1';

  NotificationProvider() : super(NotificationState());

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('accessToken');
  }

  Future<void> fetchNotifications() async {
    state = state.copyWith(loading: true);
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$_baseUrl/notifications/'),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final unread = (data['results'] as List).where((n) => n['status'] == 'sent').length;
        state = state.copyWith(notifications: data['results'] ?? [], unreadCount: unread, loading: false);
      } else {
        state = state.copyWith(loading: false);
      }
    } catch (e) {
      state = state.copyWith(loading: false);
    }
  }
}

final notificationProvider = StateNotifierProvider<NotificationProvider, NotificationState>((ref) => NotificationProvider());
