import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class MemberState {
  final dynamic profile;
  final List<dynamic> members;
  final bool loading;
  final String? error;

  MemberState({this.profile, this.members = const [], this.loading = false, this.error});

  MemberState copyWith({profile, members, loading, error}) {
    return MemberState(
      profile: profile ?? this.profile,
      members: members ?? this.members,
      loading: loading ?? this.loading,
      error: error ?? this.error,
    );
  }
}

class MemberProvider extends StateNotifier<MemberState> {
  static const String _baseUrl = 'http://localhost:8000/api/v1';

  MemberProvider() : super(MemberState());

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('accessToken');
  }

  Future<void> fetchProfile() async {
    state = state.copyWith(loading: true);
    try {
      final token = await _getToken();
      final response = await http.get(
        Uri.parse('$_baseUrl/members/profile/'),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        state = state.copyWith(profile: jsonDecode(response.body), loading: false);
      } else {
        state = state.copyWith(loading: false, error: 'Failed to fetch profile');
      }
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }

  Future<void> fetchMembers({String? search}) async {
    state = state.copyWith(loading: true);
    try {
      final token = await _getToken();
      String url = '$_baseUrl/members/';
      if (search != null) url += '?search=$search';
      
      final response = await http.get(
        Uri.parse(url),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        state = state.copyWith(members: data['results'] ?? [], loading: false);
      } else {
        state = state.copyWith(loading: false, error: 'Failed to fetch members');
      }
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }

  Future<void> updateProfile(Map<String, dynamic> data) async {
    state = state.copyWith(loading: true);
    try {
      final token = await _getToken();
      final response = await http.put(
        Uri.parse('$_baseUrl/members/profile/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(data),
      );
      
      if (response.statusCode == 200) {
        state = state.copyWith(profile: jsonDecode(response.body), loading: false);
      } else {
        state = state.copyWith(loading: false, error: 'Failed to update profile');
      }
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }
}

final memberProvider = StateNotifierProvider<MemberProvider, MemberState>((ref) => MemberProvider());
