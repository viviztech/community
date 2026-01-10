import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthState {
  final bool isAuthenticated;
  final String? token;
  final dynamic user;
  final bool loading;
  final String? error;

  AuthState({
    this.isAuthenticated = false,
    this.token,
    this.user,
    this.loading = false,
    this.error,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    String? token,
    dynamic user,
    bool? loading,
    String? error,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      token: token ?? this.token,
      user: user ?? this.user,
      loading: loading ?? this.loading,
      error: error,
    );
  }
}

class AuthProvider extends StateNotifier<AuthState> {
  static const String _baseUrl = 'http://localhost:8000/api/v1';
  
  AuthProvider() : super(AuthState()) {
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('accessToken');
    if (token != null) {
      state = state.copyWith(isAuthenticated: true, token: token);
      fetchUser();
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(loading: true, error: null);
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('accessToken', data['access']);
        await prefs.setString('refreshToken', data['refresh']);
        
        state = state.copyWith(
          isAuthenticated: true,
          token: data['access'],
          user: data,
          loading: false,
        );
      } else {
        state = state.copyWith(
          loading: false,
          error: jsonDecode(response.body)['detail'] ?? 'Login failed',
        );
      }
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }

  Future<void> register(Map<String, dynamic> userData) async {
    state = state.copyWith(loading: true, error: null);
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(userData),
      );
      
      if (response.statusCode == 201) {
        state = state.copyWith(loading: false);
      } else {
        state = state.copyWith(
          loading: false,
          error: jsonDecode(response.body).toString(),
        );
      }
    } catch (e) {
      state = state.copyWith(loading: false, error: e.toString());
    }
  }

  Future<void> fetchUser() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('accessToken');
    if (token == null) return;
    
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/auth/me'),
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        state = state.copyWith(user: jsonDecode(response.body));
      }
    } catch (e) {
      print('Error fetching user: $e');
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('accessToken');
    await prefs.remove('refreshToken');
    state = AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthProvider, AuthState>((ref) => AuthProvider());
