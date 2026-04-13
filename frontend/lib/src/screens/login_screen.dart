import 'package:flutter/material.dart';

import '../core/ui.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({
    super.key,
    required this.loading,
    required this.passwordIdentifierController,
    required this.passwordSecretController,
    required this.uanIdentifierController,
    required this.uanSecretController,
    required this.onPasswordLogin,
    required this.onUanLogin,
    required this.darkMode,
    required this.onToggleTheme,
  });

  final bool loading;
  final TextEditingController passwordIdentifierController;
  final TextEditingController passwordSecretController;
  final TextEditingController uanIdentifierController;
  final TextEditingController uanSecretController;
  final VoidCallback onPasswordLogin;
  final VoidCallback onUanLogin;
  final bool darkMode;
  final VoidCallback onToggleTheme;

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
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
                          Container(
                            decoration: BoxDecoration(
                              color: appInsetColor(context),
                              borderRadius: BorderRadius.circular(18),
                            ),
                            child: const TabBar(
                              dividerColor: Colors.transparent,
                              tabs: [
                                Tab(text: 'Пароль'),
                                Tab(text: 'УИН / УАН'),
                              ],
                            ),
                          ),
                          const SizedBox(height: 24),
                          SizedBox(
                            height: wide ? 344 : 372,
                            child: TabBarView(
                              children: [
                                _PasswordTab(
                                  loading: loading,
                                  identifierController:
                                      passwordIdentifierController,
                                  secretController: passwordSecretController,
                                  onLogin: onPasswordLogin,
                                ),
                                _UanTab(
                                  loading: loading,
                                  uinController: uanIdentifierController,
                                  uanController: uanSecretController,
                                  onLogin: onUanLogin,
                                ),
                              ],
                            ),
                          ),
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
                        style: Theme.of(context).textTheme.displaySmall
                            ?.copyWith(
                              color: appTextColor(context),
                              fontWeight: FontWeight.w700,
                              height: 1.08,
                            ),
                      ),
                      const SizedBox(height: 18),
                      Text(
                        'Почта, паспорт, парламент, референдумы, новости и Ratubles теперь собраны в одном мобильном интерфейсе.',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(
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
                              tooltip: darkMode
                                  ? 'Светлая тема'
                                  : 'Чёрная тема',
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
      ),
    );
  }
}

class _PasswordTab extends StatelessWidget {
  const _PasswordTab({
    required this.loading,
    required this.identifierController,
    required this.secretController,
    required this.onLogin,
  });

  final bool loading;
  final TextEditingController identifierController;
  final TextEditingController secretController;
  final VoidCallback onLogin;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: identifierController,
          decoration: const InputDecoration(
            labelText: 'УИН или логин',
            hintText: 'Например: ROOT или root',
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: secretController,
          obscureText: true,
          decoration: const InputDecoration(labelText: 'Пароль'),
        ),
        const SizedBox(height: 20),
        FilledButton(
          onPressed: loading ? null : onLogin,
          child: const Text('Войти в RGOV'),
        ),
        const SizedBox(height: 20),
        _LoginHint(
          'Логин и Пароль по умолчанию это УИН и УАН. Также можно использовать связку УИН + УАН.',
        ),
      ],
    );
  }
}

class _UanTab extends StatelessWidget {
  const _UanTab({
    required this.loading,
    required this.uinController,
    required this.uanController,
    required this.onLogin,
  });

  final bool loading;
  final TextEditingController uinController;
  final TextEditingController uanController;
  final VoidCallback onLogin;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: uinController,
          decoration: const InputDecoration(
            labelText: 'УИН',
            hintText: 'Например: 1.26.563372',
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: uanController,
          decoration: const InputDecoration(
            labelText: 'УАН',
            hintText: 'Приватный идентификатор',
          ),
        ),
        const SizedBox(height: 20),
        FilledButton(
          onPressed: loading ? null : onLogin,
          child: const Text('Войти по УИН и УАН'),
        ),
        const SizedBox(height: 20),
        _LoginHint(
          'УАН остаётся приватным: в общих списках он маскируется, а полный номер доступен только владельцу в профиле и DID.',
        ),
      ],
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
            ? const Color(0xFF141414).withValues(alpha: 0.82)
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
