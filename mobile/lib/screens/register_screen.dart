import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:activ_mobile/providers/auth_provider.dart';

class RegisterScreen extends ConsumerWidget {
  const RegisterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final firstNameController = TextEditingController();
    final lastNameController = TextEditingController();
    final emailController = TextEditingController();
    final passwordController = TextEditingController();

    ref.listen(authProvider, (previous, next) {
      if (next.error != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.error!)),
        );
      }
    });

    return Scaffold(
      appBar: AppBar(title: const Text('Create Account')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(
              controller: firstNameController,
              decoration: const InputDecoration(labelText: 'First Name', prefixIcon: Icon(Icons.person)),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: lastNameController,
              decoration: const InputDecoration(labelText: 'Last Name'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email)),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: passwordController,
              decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock)),
              obscureText: true,
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: authState.loading
                    ? null
                    : () => ref.read(authProvider.notifier).register({
                      'first_name': firstNameController.text,
                      'last_name': lastNameController.text,
                      'email': emailController.text,
                      'password': passwordController.text,
                    }),
                child: authState.loading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('Create Account'),
              ),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => context.go('/login'),
              child: const Text('Already have an account? Sign In'),
            ),
          ],
        ),
      ),
    );
  }
}
