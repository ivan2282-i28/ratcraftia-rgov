import 'package:flutter/material.dart';

import '../core/ui.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({
    super.key,
    required this.loading,
    required this.identifierController,
    required this.secretController,
    required this.onLogin,
    required this.onOpenTokenCreator,
    required this.createdExternalAuthApp,
    required this.darkMode,
    required this.onToggleTheme,
  });

  final bool loading;
  final TextEditingController identifierController;
  final TextEditingController secretController;
  final VoidCallback onLogin;
  final VoidCallback onOpenTokenCreator;
  final Map<String, dynamic>? createdExternalAuthApp;
  final bool darkMode;
  final VoidCallback onToggleTheme;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(gradient: appBackgroundGradient(context)),
        child: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              final wide = constraints.maxWidth >= 980;

              final loginPanel = ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 560),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(28),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'RGOV',
                          style: Theme.of(context).textTheme.displaySmall
                              ?.copyWith(
                                color: appTextColor(context),
                                fontWeight: FontWeight.w700,
                              ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Ratcraftia Government Web Portal',
                          style: Theme.of(context).textTheme.titleMedium
                              ?.copyWith(
                                color: appMutedTextColor(context, 0.8),
                              ),
                        ),
                        const SizedBox(height: 24),
                        TextField(
                          controller: identifierController,
                          decoration: const InputDecoration(
                            labelText: 'Логин или УИН',
                            hintText: 'Например: root или 1.26.563372',
                          ),
                        ),
                        const SizedBox(height: 16),
                        TextField(
                          controller: secretController,
                          obscureText: true,
                          decoration: const InputDecoration(
                            labelText: 'Пароль или УАН',
                            hintText: 'Введите пароль или приватный УАН',
                          ),
                        ),
                        const SizedBox(height: 20),
                        FilledButton(
                          onPressed: loading ? null : onLogin,
                          child: const Text('Войти в RGOV'),
                        ),
                        const SizedBox(height: 12),
                        OutlinedButton(
                          onPressed: loading ? null : onOpenTokenCreator,
                          child: const Text('Создать OAuth-токены'),
                        ),
                        const SizedBox(height: 20),
                        const _LoginHint(
                          'Одна форма поддерживает вход по логину + паролю, УИН + паролю и УИН + УАН.',
                        ),
                        const SizedBox(height: 12),
                        const _LoginHint(
                          'Для сторонних сервисов можно создать OAuth client_id и client_secret прямо отсюда. Выпуск access token всё равно будет доступен только после одобрения приложения и пользовательского consent.',
                        ),
                        if (createdExternalAuthApp != null) ...[
                          const SizedBox(height: 12),
                          _CreatedOAuthClientCard(
                            data: createdExternalAuthApp!,
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              );

              final heroPanel = ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 520),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Единый гражданский портал Ratcraftia',
                      style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        color: appTextColor(context),
                        fontWeight: FontWeight.w700,
                        height: 1.08,
                      ),
                    ),
                    const SizedBox(height: 18),
                    Text(
                      'Почта, паспорт, парламент, референдумы, новости и Ratubles теперь собраны в одном мобильном интерфейсе.',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: appMutedTextColor(context, 0.8),
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 24),
                    const _HeroFeature(
                      icon: Icons.account_balance_rounded,
                      title: 'Чистая иерархия',
                      text:
                          'Разделы разведены по задачам: обзор, Ratubles, переписка, законы и управление.',
                    ),
                    const SizedBox(height: 14),
                    const _HeroFeature(
                      icon: Icons.phone_iphone_rounded,
                      title: 'Удобно с телефона',
                      text:
                          'Все карточки, формы и списки перестраиваются под узкий экран без горизонтального скролла.',
                    ),
                    const SizedBox(height: 14),
                    const _HeroFeature(
                      icon: Icons.notifications_active_rounded,
                      title: 'Push-уведомления',
                      text:
                          'После входа можно получать почту и государственные события прямо в браузер.',
                    ),
                  ],
                ),
              );

              if (wide) {
                return Center(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        Align(
                          alignment: Alignment.centerRight,
                          child: IconButton(
                            onPressed: onToggleTheme,
                            tooltip: darkMode ? 'Светлая тема' : 'Чёрная тема',
                            icon: Icon(
                              darkMode
                                  ? Icons.light_mode_rounded
                                  : Icons.dark_mode_rounded,
                            ),
                          ),
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            heroPanel,
                            const SizedBox(width: 28),
                            loginPanel,
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              }

              return Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Align(
                        alignment: Alignment.centerRight,
                        child: IconButton(
                          onPressed: onToggleTheme,
                          tooltip: darkMode ? 'Светлая тема' : 'Чёрная тема',
                          icon: Icon(
                            darkMode
                                ? Icons.light_mode_rounded
                                : Icons.dark_mode_rounded,
                          ),
                        ),
                      ),
                      heroPanel,
                      const SizedBox(height: 20),
                      loginPanel,
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _HeroFeature extends StatelessWidget {
  const _HeroFeature({
    required this.icon,
    required this.title,
    required this.text,
  });

  final IconData icon;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: isDarkTheme(context)
            ? appInsetColor(context).withValues(alpha: 0.88)
            : Colors.white.withValues(alpha: 0.72),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 22,
            backgroundColor: copper,
            foregroundColor: Colors.white,
            child: Icon(icon),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: appTextColor(context),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  text,
                  style: TextStyle(
                    color: appMutedTextColor(context, 0.8),
                    height: 1.45,
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

class _LoginHint extends StatelessWidget {
  const _LoginHint(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: appInsetColor(context),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Text(
        text,
        style: TextStyle(color: appMutedTextColor(context), height: 1.45),
      ),
    );
  }
}

class _CreatedOAuthClientCard extends StatelessWidget {
  const _CreatedOAuthClientCard({required this.data});

  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final application = Map<String, dynamic>.from(
      data['application'] as Map? ?? const {},
    );
    final clientId = application['client_id']?.toString() ?? '';
    final redirectUri = application['redirect_uri']?.toString() ?? '';
    final clientSecret = data['client_secret']?.toString() ?? '';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: appInsetColor(context),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'OAuth-клиент создан',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: appTextColor(context),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Client ID: $clientId',
            style: TextStyle(color: appMutedTextColor(context)),
          ),
          if (clientSecret.isNotEmpty) ...[
            const SizedBox(height: 4),
            SelectableText(
              'Client Secret: $clientSecret',
              style: TextStyle(color: appTextColor(context), height: 1.45),
            ),
          ],
          if (redirectUri.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Redirect URI: $redirectUri',
              style: TextStyle(color: appMutedTextColor(context)),
            ),
          ],
          const SizedBox(height: 10),
          Text(
            'Сохраните secret сейчас: после закрытия карточки он больше не будет показан сервером. Статус приложения пока ожидает одобрения администратора.',
            style: TextStyle(color: appMutedTextColor(context), height: 1.45),
          ),
        ],
      ),
    );
  }
}
