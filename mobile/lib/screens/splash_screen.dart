import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(seconds: 2), () {
      context.go('/login');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.business_center, size: 80, color: Color(0xFF1976D2)),
            const SizedBox(height: 20),
            const Text(
              'ACTIV',
              style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF1976D2)),
            ),
            const SizedBox(height: 10),
            const Text(
              'Membership Portal',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
