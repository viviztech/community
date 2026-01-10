import 'package:flutter/material.dart';

ThemeData appTheme = ThemeData(
  primarySwatch: Colors.blue,
  primaryColor: const Color(0xFF1976D2),
  scaffoldBackgroundColor: Colors.grey[100],
  appBarTheme: const AppBarTheme(
    backgroundColor: Color(0xFF1976D2),
    foregroundColor: Colors.white,
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: const Color(0xFF1976D2),
      foregroundColor: Colors.white,
    ),
  ),
  inputDecorationTheme: InputDecorationTheme(
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
    ),
    filled: true,
    fillColor: Colors.white,
  ),
  cardTheme: CardTheme(
    elevation: 2,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
);
