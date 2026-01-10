import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class EventState {
  final List<dynamic> events;
  final bool loading;
  final String? error;

  EventState({this.events = const [], this.loading = false, this.error});

  EventState copyWith({events, loading, error}) {
    return EventState(
      events: events ?? this.events,
      loading: loading ?? this.loading,
      error: error ?? this.error,
    );
  }
}

class EventProvider extends StateNotifier<EventState> {
  static const String _baseUrl = 'http://localhost:8000/api/v1';

  EventProvider() : super(EventState());

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('accessToken');
  }

  Future<void> fetchEvents({String status = 'published'}) async {
    state = state.copyWith(loading: true);
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$_baseUrl/events/?status=$status'),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        state = state.copyWith(events: data['results'] ?? [], loading: false);
      } else {
        state = state.copyWith(loading: false, error: 'Failed to fetch events');
      }
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }
}

final eventProvider = StateNotifierProvider<EventProvider, EventState>((ref) => EventProvider());
