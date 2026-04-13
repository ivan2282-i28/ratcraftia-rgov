import 'dart:math' as math;

import 'package:flutter/material.dart';

const Color parchment = Color(0xFFF6EFE3);
const Color parchmentStrong = Color(0xFFE5D6C4);
const Color lacquer = Color(0xFF2E1B14);
const Color copper = Color(0xFF9B3D28);
const Color brick = Color(0xFFB95C3D);
const Color moss = Color(0xFF5D7A57);
const Color sky = Color(0xFF4A7A8C);
const Color emberDark = Color(0xFF16110F);
const Color smokeDark = Color(0xFF221A16);
const Color ashText = Color(0xFFF1E6D8);
const Color sageGlow = Color(0xFF8CA89D);

ThemeData buildRgovTheme() {
  return _buildTheme(Brightness.light);
}

ThemeData buildRgovDarkTheme() {
  return _buildTheme(Brightness.dark);
}

ThemeData _buildTheme(Brightness brightness) {
  final dark = brightness == Brightness.dark;
  final colorScheme =
      ColorScheme.fromSeed(seedColor: copper, brightness: brightness).copyWith(
        primary: dark ? const Color(0xFFE5C8AA) : copper,
        onPrimary: dark ? emberDark : Colors.white,
        secondary: dark ? sageGlow : moss,
        onSecondary: dark ? emberDark : Colors.white,
        surface: dark ? smokeDark : Colors.white,
        onSurface: dark ? ashText : lacquer,
        outline: dark
            ? Colors.white.withValues(alpha: 0.14)
            : lacquer.withValues(alpha: 0.12),
      );

  return ThemeData(
    useMaterial3: true,
    fontFamily: 'Georgia',
    colorScheme: colorScheme,
    canvasColor: dark ? smokeDark : Colors.white,
    scaffoldBackgroundColor: dark ? emberDark : parchment,
    appBarTheme: AppBarTheme(
      backgroundColor: Colors.transparent,
      foregroundColor: dark ? ashText : lacquer,
      centerTitle: false,
      elevation: 0,
    ),
    cardTheme: CardThemeData(
      color: dark
          ? const Color(0xFF1C1512).withValues(alpha: 0.94)
          : Colors.white.withValues(alpha: 0.94),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(28),
        side: BorderSide(
          color: (dark ? Colors.white : lacquer).withValues(alpha: 0.08),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: dark ? const Color(0xFF261E1A) : Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: BorderSide(
          color: (dark ? Colors.white : lacquer).withValues(alpha: 0.14),
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: BorderSide(
          color: (dark ? Colors.white : lacquer).withValues(alpha: 0.14),
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(18)),
        borderSide: BorderSide(
          color: dark ? const Color(0xFFE5C8AA) : copper,
          width: 1.5,
        ),
      ),
      labelStyle: TextStyle(color: dark ? ashText : lacquer),
      hintStyle: TextStyle(
        color: dark
            ? ashText.withValues(alpha: 0.56)
            : lacquer.withValues(alpha: 0.48),
      ),
    ),
    drawerTheme: DrawerThemeData(
      backgroundColor: dark ? const Color(0xFF191310) : Colors.white,
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: dark ? const Color(0xFF1E1713) : Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
    ),
    listTileTheme: ListTileThemeData(
      iconColor: dark ? ashText : lacquer,
      textColor: dark ? ashText : lacquer,
    ),
    navigationRailTheme: NavigationRailThemeData(
      backgroundColor: dark
          ? const Color(0xFF191310).withValues(alpha: 0.96)
          : Colors.white.withValues(alpha: 0.9),
      indicatorColor: dark ? const Color(0xFF2B221D) : parchmentStrong,
      selectedIconTheme: IconThemeData(
        color: dark ? const Color(0xFFE5C8AA) : copper,
      ),
      selectedLabelTextStyle: TextStyle(
        color: dark ? const Color(0xFFE5C8AA) : copper,
        fontWeight: FontWeight.w700,
      ),
      unselectedIconTheme: IconThemeData(
        color: dark
            ? ashText.withValues(alpha: 0.72)
            : lacquer.withValues(alpha: 0.72),
      ),
      unselectedLabelTextStyle: TextStyle(
        color: dark
            ? ashText.withValues(alpha: 0.72)
            : lacquer.withValues(alpha: 0.72),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: dark ? const Color(0xFFE5C8AA) : copper,
        foregroundColor: dark ? emberDark : Colors.white,
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: dark ? ashText : lacquer,
        side: BorderSide(
          color: dark
              ? Colors.white.withValues(alpha: 0.16)
              : lacquer.withValues(alpha: 0.14),
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: dark ? const Color(0xFFE5C8AA) : copper,
      ),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: dark ? const Color(0xFF2A1F19) : lacquer,
      contentTextStyle: TextStyle(color: dark ? ashText : Colors.white),
    ),
    dividerColor: (dark ? Colors.white : lacquer).withValues(alpha: 0.08),
  );
}

bool isDarkTheme(BuildContext context) =>
    Theme.of(context).brightness == Brightness.dark;

Color appTextColor(BuildContext context) =>
    isDarkTheme(context) ? ashText : lacquer;

Color appMutedTextColor(BuildContext context, [double alpha = 0.76]) =>
    appTextColor(context).withValues(alpha: alpha);

Color appInsetColor(BuildContext context) =>
    isDarkTheme(context) ? const Color(0xFF241C18) : parchment;

Color appSoftFillColor(BuildContext context) =>
    isDarkTheme(context) ? const Color(0xFF312620) : parchmentStrong;

Color appRailColor(BuildContext context) => isDarkTheme(context)
    ? const Color(0xFF191310).withValues(alpha: 0.96)
    : Colors.white.withValues(alpha: 0.9);

LinearGradient appBackgroundGradient(BuildContext context) =>
    isDarkTheme(context)
    ? const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Color(0xFF15100E), Color(0xFF1E1714), Color(0xFF2B1D17)],
      )
    : const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Color(0xFFF6EFE3), Color(0xFFE7D7C6), Color(0xFFF0E4D3)],
      );

String formatTimestamp(dynamic value) {
  if (value == null || value.toString().isEmpty) {
    return 'не указано';
  }

  try {
    final parsed = DateTime.parse(value.toString()).toLocal();
    return '${_two(parsed.day)}.${_two(parsed.month)}.${parsed.year} '
        '${_two(parsed.hour)}:${_two(parsed.minute)}';
  } catch (_) {
    return value.toString();
  }
}

String initialsFromName(String value) {
  final parts = value
      .split(' ')
      .where((part) => part.trim().isNotEmpty)
      .take(2)
      .map((part) => part.substring(0, 1).toUpperCase())
      .join();
  return parts.isEmpty ? 'RG' : parts;
}

int? maybeInt(String value) {
  final trimmed = value.trim();
  if (trimmed.isEmpty) {
    return null;
  }
  return int.tryParse(trimmed);
}

int unreadInboxCount(List<Map<String, dynamic>> messages) {
  return messages.where((item) => item['read_at'] == null).length;
}

class PageBody extends StatelessWidget {
  const PageBody({super.key, required this.loading, required this.children});

  final bool loading;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter,
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1240),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (loading)
                const Padding(
                  padding: EdgeInsets.only(bottom: 12),
                  child: LinearProgressIndicator(),
                ),
              ...children,
            ],
          ),
        ),
      ),
    );
  }
}

class SectionCard extends StatelessWidget {
  const SectionCard({
    super.key,
    required this.title,
    required this.child,
    this.subtitle,
  });

  final String title;
  final String? subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: appTextColor(context),
                fontWeight: FontWeight.w700,
              ),
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 6),
              Text(
                subtitle!,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: appMutedTextColor(context),
                  height: 1.45,
                ),
              ),
            ],
            const SizedBox(height: 18),
            child,
          ],
        ),
      ),
    );
  }
}

class AdaptivePaneGrid extends StatelessWidget {
  const AdaptivePaneGrid({
    super.key,
    required this.children,
    this.minChildWidth = 320,
    this.spacing = 18,
  });

  final List<Widget> children;
  final double minChildWidth;
  final double spacing;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final availableWidth = constraints.maxWidth;
        final columns = math.max(
          1,
          ((availableWidth + spacing) / (minChildWidth + spacing)).floor(),
        );
        final itemWidth = columns == 1
            ? availableWidth
            : (availableWidth - spacing * (columns - 1)) / columns;

        return Wrap(
          spacing: spacing,
          runSpacing: spacing,
          children: [
            for (final child in children)
              SizedBox(width: itemWidth.clamp(0, availableWidth), child: child),
          ],
        );
      },
    );
  }
}

class MetricPill extends StatelessWidget {
  const MetricPill({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
    this.note,
  });

  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final String? note;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 260,
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: isDarkTheme(context) ? 0.18 : 0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: color,
            foregroundColor: Colors.white,
            child: Icon(icon),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: appTextColor(context),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(title),
                if (note != null)
                  Text(
                    note!,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: appMutedTextColor(context, 0.7),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class InfoRow extends StatelessWidget {
  const InfoRow({super.key, required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 300;
          if (compact) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    color: appMutedTextColor(context, 0.7),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: TextStyle(
                    color: appTextColor(context),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            );
          }

          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 96,
                child: Text(
                  '$label:',
                  style: TextStyle(
                    color: appMutedTextColor(context, 0.7),
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              Expanded(
                child: Text(
                  value,
                  style: TextStyle(
                    color: appTextColor(context),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class EmptyStateMessage extends StatelessWidget {
  const EmptyStateMessage(this.message, {super.key});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: appInsetColor(context),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        message,
        style: TextStyle(color: appMutedTextColor(context, 0.82)),
      ),
    );
  }
}

String _two(int value) => value.toString().padLeft(2, '0');
