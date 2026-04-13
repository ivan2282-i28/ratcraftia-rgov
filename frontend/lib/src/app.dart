import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/ui.dart';
import 'screens/portal_screen.dart';

class RgovApp extends StatefulWidget {
  const RgovApp({super.key});

  @override
  State<RgovApp> createState() => _RgovAppState();
}

class _RgovAppState extends State<RgovApp> {
  static const _themeModeKey = 'rgov_theme_mode';

  ThemeMode _themeMode = ThemeMode.light;

  @override
  void initState() {
    super.initState();
    _restoreThemeMode();
  }

  Future<void> _restoreThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_themeModeKey);
    if (!mounted) {
      return;
    }
    setState(() {
      _themeMode = raw == 'dark' ? ThemeMode.dark : ThemeMode.light;
    });
  }

  Future<void> _setThemeMode(ThemeMode mode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _themeModeKey,
      mode == ThemeMode.dark ? 'dark' : 'light',
    );
    if (!mounted) {
      return;
    }
    setState(() => _themeMode = mode);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'RGOV',
      theme: buildRgovTheme(),
      darkTheme: buildRgovDarkTheme(),
      themeMode: _themeMode,
      home: PortalScreen(
        themeMode: _themeMode,
        onThemeModeChanged: _setThemeMode,
      ),
    );
  }
}
