import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:activ_mobile/providers/auth_provider.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final emailController = TextEditingController();
    final passwordController = TextEditingController();

    ref.listen(authProvider, (previous, next) {
      if (next.isAuthenticated) {
        context.go('/dashboard');
      }
      if (next.error != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.error!)),
        );
      }
    });

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.business_center, size: 60, color: Color(0xFF1976D2)),
              const SizedBox(height: 16),
              const Text(
                'Welcome Back',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('Sign in to ACTIV Membership Portal'),
              const SizedBox(height: 32),
              TextField(
                controller: emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Icons.email),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: passwordController,
                decoration: const InputDecoration(
                  labelText: 'Password',
                  prefixIcon: Icon(Icons.lock),
                ),
                obscureText: true,
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: authState.loading
                      ? null
                      : () => ref.read(authProvider.notifier).login(
                            emailController.text,
                            passwordController.text,
                          ),
                  child: authState.loading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text('Sign In'),
                ),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () => context.go('/register'),
                child: const Text("Don't have an account? Sign Up"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
