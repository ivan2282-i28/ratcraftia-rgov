import 'dart:async';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/ui.dart';
import '../services/api_client.dart';
import '../services/push_notification_service.dart';
import 'login_screen.dart';
import 'portal_pages.dart';

class PortalScreen extends StatefulWidget {
  const PortalScreen({
    super.key,
    required this.themeMode,
    required this.onThemeModeChanged,
  });

  final ThemeMode themeMode;
  final ValueChanged<ThemeMode> onThemeModeChanged;

  @override
  State<PortalScreen> createState() => _PortalScreenState();
}

class _PortalScreenState extends State<PortalScreen> {
  final ApiClient _api = ApiClient();
  final PushNotificationService _pushNotifications = PushNotificationService();

  final _passwordIdentifierController = TextEditingController();
  final _passwordSecretController = TextEditingController();
  final _uanIdentifierController = TextEditingController();
  final _uanSecretController = TextEditingController();
  final _mailToController = TextEditingController();
  final _mailSubjectController = TextEditingController();
  final _mailTextController = TextEditingController();
  final _billTitleController = TextEditingController();
  final _billSummaryController = TextEditingController();
  final _billTextController = TextEditingController();
  final _billLawIdController = TextEditingController();
  final _referendumTitleController = TextEditingController();
  final _referendumDescriptionController = TextEditingController();
  final _referendumTextController = TextEditingController();
  final _referendumLawIdController = TextEditingController();
  final _newsTitleController = TextEditingController();
  final _newsBodyController = TextEditingController();
  final _loginChangeController = TextEditingController();
  final _orgNameController = TextEditingController();
  final _orgSlugController = TextEditingController();
  final _orgDescriptionController = TextEditingController();
  final _userUinController = TextEditingController();
  final _userUanController = TextEditingController();
  final _userLoginController = TextEditingController();
  final _userPasswordController = TextEditingController();
  final _userFirstNameController = TextEditingController();
  final _userLastNameController = TextEditingController();
  final _userPatronymicController = TextEditingController();
  final _userPermissionsController = TextEditingController();
  final _userPositionController = TextEditingController();
  final _assignedPermissionsController = TextEditingController();
  final _personnelPositionController = TextEditingController();
  final _userEditUinController = TextEditingController();
  final _userEditUanController = TextEditingController();
  final _userEditFirstNameController = TextEditingController();
  final _userEditLastNameController = TextEditingController();
  final _userEditPatronymicController = TextEditingController();
  final _transferAmountController = TextEditingController();
  final _transferReasonController = TextEditingController();
  final _mintAmountController = TextEditingController();
  final _mintReasonController = TextEditingController();

  bool _restoring = true;
  bool _loading = false;
  PortalSection _selectedSection = PortalSection.overview;

  JsonMap? _profile;
  JsonMap? _did;
  List<JsonMap> _inbox = [];
  List<JsonMap> _sent = [];
  List<JsonMap> _news = [];
  List<JsonMap> _laws = [];
  List<JsonMap> _bills = [];
  List<JsonMap> _referenda = [];
  List<JsonMap> _users = [];
  List<JsonMap> _organizations = [];
  List<JsonMap> _directory = [];
  List<JsonMap> _transactions = [];
  List<JsonMap> _ledger = [];
  List<JsonMap> _adminLogs = [];
  PushNotificationStatus _pushStatus = const PushNotificationStatus.initial();

  String _referendumTargetLevel = 'constitution';
  int? _selectedUserId;
  int? _selectedTransferRecipientId;
  String? _selectedOrganizationSlug;

  @override
  void initState() {
    super.initState();
    _selectedSection = PortalSection.fromFragment(Uri.base.fragment);
    _restoreSession();
  }

  @override
  void dispose() {
    final controllers = [
      _passwordIdentifierController,
      _passwordSecretController,
      _uanIdentifierController,
      _uanSecretController,
      _mailToController,
      _mailSubjectController,
      _mailTextController,
      _billTitleController,
      _billSummaryController,
      _billTextController,
      _billLawIdController,
      _referendumTitleController,
      _referendumDescriptionController,
      _referendumTextController,
      _referendumLawIdController,
      _newsTitleController,
      _newsBodyController,
      _loginChangeController,
      _orgNameController,
      _orgSlugController,
      _orgDescriptionController,
      _userUinController,
      _userUanController,
      _userLoginController,
      _userPasswordController,
      _userFirstNameController,
      _userLastNameController,
      _userPatronymicController,
      _userPermissionsController,
      _userPositionController,
      _assignedPermissionsController,
      _personnelPositionController,
      _userEditUinController,
      _userEditUanController,
      _userEditFirstNameController,
      _userEditLastNameController,
      _userEditPatronymicController,
      _transferAmountController,
      _transferReasonController,
      _mintAmountController,
      _mintReasonController,
    ];

    for (final controller in controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  List<String> _permissionsFor(JsonMap? profile) {
    final raw = profile?['permissions'] as List<dynamic>? ?? const [];
    return raw.map((item) => item.toString()).toList();
  }

  bool _hasPermission(String permission, {JsonMap? profile}) {
    final permissions = _permissionsFor(profile ?? _profile);
    return permissions.contains('*') || permissions.contains(permission);
  }

  List<String> _parsePermissions(String raw) {
    final values =
        raw
            .split(',')
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .map((item) => item.toLowerCase())
            .toSet()
            .toList()
          ..sort();
    if (values.contains('*')) {
      return const ['*'];
    }
    return values;
  }

  String _permissionsTextForUser(int? userId, [List<JsonMap>? users]) {
    if (userId == null) {
      return '';
    }
    final source = users ?? _users;
    for (final user in source) {
      if (user['id'] == userId) {
        final permissions = (user['permissions'] as List<dynamic>? ?? const [])
            .map((item) => item.toString())
            .toList();
        return permissions.join(', ');
      }
    }
    return '';
  }

  void _syncAssignedPermissionsInput([int? userId, List<JsonMap>? users]) {
    final text = _permissionsTextForUser(userId ?? _selectedUserId, users);
    if (_assignedPermissionsController.text == text) {
      return;
    }
    _assignedPermissionsController.value = TextEditingValue(
      text: text,
      selection: TextSelection.collapsed(offset: text.length),
    );
  }

  JsonMap? _userById(int? userId, [List<JsonMap>? users]) {
    if (userId == null) {
      return null;
    }
    final source = users ?? _users;
    for (final user in source) {
      if (user['id'] == userId) {
        return user;
      }
    }
    return null;
  }

  void _syncSelectedUserEditor([int? userId, List<JsonMap>? users]) {
    final selected = _userById(userId ?? _selectedUserId, users);
    final values = [
      (
        controller: _userEditUinController,
        value: selected?['uin']?.toString() ?? '',
      ),
      (
        controller: _userEditUanController,
        value: selected?['uan']?.toString() ?? '',
      ),
      (
        controller: _userEditFirstNameController,
        value: selected?['first_name']?.toString() ?? '',
      ),
      (
        controller: _userEditLastNameController,
        value: selected?['last_name']?.toString() ?? '',
      ),
      (
        controller: _userEditPatronymicController,
        value: selected?['patronymic']?.toString() ?? '',
      ),
    ];
    for (final item in values) {
      if (item.controller.text == item.value) {
        continue;
      }
      item.controller.value = TextEditingValue(
        text: item.value,
        selection: TextSelection.collapsed(offset: item.value.length),
      );
    }
  }

  bool get _canCreateBills => _hasPermission('bills.manage');
  bool get _canCreateReferenda => _hasPermission('referenda.manage');
  bool get _canPostNews => _hasPermission('news.manage');
  bool get _canCreateOrganizations =>
      _hasPermission('admin.organizations.create');
  bool get _canManagePersonnel => _hasPermission('admin.personnel.manage');
  bool get _canCreateUsers => _hasPermission('admin.users.create');
  bool get _canUpdateUsers => _hasPermission('admin.users.update');
  bool get _canManagePermissions =>
      _hasPermission('admin.users.permissions.write');
  bool get _canReadUsers => _hasPermission('admin.users.read');
  bool get _canReadOrganizations => _hasPermission('admin.organizations.read');
  bool get _canReadAdminLogs => _hasPermission('admin.logs.read');
  bool get _canMintRatubles => _hasPermission('ratubles.mint');
  bool get _canOpenAdmin =>
      _canReadAdminLogs ||
      _canMintRatubles ||
      _canCreateOrganizations ||
      _canManagePersonnel ||
      _canCreateUsers ||
      _canUpdateUsers ||
      _canManagePermissions ||
      _canReadUsers ||
      _canReadOrganizations;

  Future<void> _restoreSession() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('rgov_token');
    if (token == null || token.isEmpty) {
      final status = await _pushNotifications.getStatus();
      if (!mounted) {
        return;
      }
      setState(() {
        _pushStatus = status;
        _restoring = false;
      });
      return;
    }

    _api.token = token;
    try {
      await _refreshPortal();
    } catch (_) {
      await prefs.remove('rgov_token');
      _api.token = null;
    }

    if (!mounted) {
      return;
    }
    setState(() => _restoring = false);
  }

  Future<void> _persistToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('rgov_token', token);
  }

  Future<void> _clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('rgov_token');
  }

  Future<void> _runBusy(Future<void> Function() action) async {
    setState(() => _loading = true);
    try {
      await action();
    } on ApiException catch (error) {
      _showSnack(error.message, isError: true);
    } catch (error) {
      _showSnack('Не удалось выполнить операцию: $error', isError: true);
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  void _showSnack(String message, {bool isError = false}) {
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: isError ? brick : moss),
    );
  }

  Future<void> _loginWithPassword() async {
    await _runBusy(() async {
      final response = await _api.loginWithPassword(
        _passwordIdentifierController.text.trim(),
        _passwordSecretController.text,
      );
      final token = response['access_token'].toString();
      _api.token = token;
      await _persistToken(token);
      await _refreshPortal(seedProfile: response['profile'] as JsonMap);
      _showSnack('Сессия открыта.');
    });
  }

  Future<void> _loginWithUan() async {
    await _runBusy(() async {
      final response = await _api.loginWithUan(
        _uanIdentifierController.text.trim(),
        _uanSecretController.text.trim(),
      );
      final token = response['access_token'].toString();
      _api.token = token;
      await _persistToken(token);
      await _refreshPortal(seedProfile: response['profile'] as JsonMap);
      _showSnack('Сессия открыта.');
    });
  }

  Future<void> _logout() async {
    await _runBusy(() async {
      final token = _api.token;
      if (token != null && token.isNotEmpty) {
        try {
          await _disablePushNotifications(silent: true);
        } catch (_) {}
      }

      _api.token = null;
      await _clearToken();

      if (!mounted) {
        return;
      }
      setState(() {
        _profile = null;
        _did = null;
        _inbox = [];
        _sent = [];
        _news = [];
        _laws = [];
        _bills = [];
        _referenda = [];
        _users = [];
        _organizations = [];
        _directory = [];
        _transactions = [];
        _ledger = [];
        _adminLogs = [];
        _selectedSection = PortalSection.overview;
        _selectedUserId = null;
        _selectedTransferRecipientId = null;
        _selectedOrganizationSlug = null;
        _pushStatus = const PushNotificationStatus.initial();
      });
      _assignedPermissionsController.clear();
      _userPermissionsController.clear();
      _syncSelectedUserEditor(null, const <JsonMap>[]);
    });
  }

  Future<void> _refreshPortal({JsonMap? seedProfile}) async {
    final profile = seedProfile ?? await _api.me();
    final futures = <Future<dynamic>>[
      _api.didToken(),
      _api.getInbox(),
      _api.getSent(),
      _api.getNews(),
      _api.getLaws(),
      _api.getBills(),
      _api.getReferenda(),
      _api.getRatublesDirectory(),
      _api.getRatublesTransactions(),
      _hasPermission('admin.users.read', profile: profile)
          ? _api.getUsers()
          : Future.value(<JsonMap>[]),
      _hasPermission('admin.organizations.read', profile: profile)
          ? _api.getOrganizations()
          : Future.value(<JsonMap>[]),
      _hasPermission('admin.logs.read', profile: profile)
          ? _api.getRatublesLedger()
          : Future.value(<JsonMap>[]),
      _hasPermission('admin.logs.read', profile: profile)
          ? _api.getAdminLogs()
          : Future.value(<JsonMap>[]),
    ];

    final results = await Future.wait(futures);
    final directory = results[7] as List<JsonMap>;
    final transactions = results[8] as List<JsonMap>;
    final users = results[9] as List<JsonMap>;
    final organizations = results[10] as List<JsonMap>;
    final ledger = results[11] as List<JsonMap>;
    final adminLogs = results[12] as List<JsonMap>;
    final selectedUserId = _resolveSelectedUserId(users);
    final selectedOrganizationSlug = _resolveSelectedOrganizationSlug(
      organizations,
    );
    final selectedTransferRecipientId = _resolveSelectedTransferRecipientId(
      directory,
      profile,
    );

    if (!mounted) {
      return;
    }

    setState(() {
      _profile = profile;
      _did = results[0] as JsonMap;
      _inbox = results[1] as List<JsonMap>;
      _sent = results[2] as List<JsonMap>;
      _news = results[3] as List<JsonMap>;
      _laws = results[4] as List<JsonMap>;
      _bills = results[5] as List<JsonMap>;
      _referenda = results[6] as List<JsonMap>;
      _directory = directory;
      _transactions = transactions;
      _users = users;
      _organizations = organizations;
      _ledger = ledger;
      _adminLogs = adminLogs;
      _selectedUserId = selectedUserId;
      _selectedTransferRecipientId = selectedTransferRecipientId;
      _selectedOrganizationSlug = selectedOrganizationSlug;
    });
    _syncAssignedPermissionsInput(selectedUserId, users);
    _syncSelectedUserEditor(selectedUserId, users);

    unawaited(_syncPushNotificationsSilently());
  }

  Future<void> _sendMail() async {
    await _runBusy(() async {
      await _api.sendMail(
        to: _mailToController.text.trim(),
        subject: _mailSubjectController.text.trim(),
        text: _mailTextController.text.trim(),
      );
      _mailToController.clear();
      _mailSubjectController.clear();
      _mailTextController.clear();
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Письмо отправлено.');
    });
  }

  Future<void> _createBill() async {
    await _runBusy(() async {
      await _api.createBill(
        title: _billTitleController.text.trim(),
        summary: _billSummaryController.text.trim(),
        proposedText: _billTextController.text.trim(),
        lawId: maybeInt(_billLawIdController.text),
      );
      _billTitleController.clear();
      _billSummaryController.clear();
      _billTextController.clear();
      _billLawIdController.clear();
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Законопроект создан.');
    });
  }

  Future<void> _voteBill(int billId, String vote) async {
    await _runBusy(() async {
      await _api.voteBill(billId, vote);
      await _refreshPortal(seedProfile: _profile);
    });
  }

  Future<void> _publishBill(int billId) async {
    await _runBusy(() async {
      await _api.publishBill(billId);
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Закон опубликован.');
    });
  }

  Future<void> _createReferendum() async {
    await _runBusy(() async {
      await _api.createReferendum(
        title: _referendumTitleController.text.trim(),
        description: _referendumDescriptionController.text.trim(),
        proposedText: _referendumTextController.text.trim(),
        targetLevel: _referendumTargetLevel,
        lawId: maybeInt(_referendumLawIdController.text),
      );
      _referendumTitleController.clear();
      _referendumDescriptionController.clear();
      _referendumTextController.clear();
      _referendumLawIdController.clear();
      setState(() => _referendumTargetLevel = 'constitution');
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Референдум создан.');
    });
  }

  Future<void> _voteReferendum(int referendumId, String vote) async {
    await _runBusy(() async {
      await _api.voteReferendum(referendumId, vote);
      await _refreshPortal(seedProfile: _profile);
    });
  }

  Future<void> _publishReferendum(int referendumId) async {
    await _runBusy(() async {
      await _api.publishReferendum(referendumId);
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Итог референдума опубликован.');
    });
  }

  Future<void> _postNews() async {
    await _runBusy(() async {
      await _api.postNews(
        title: _newsTitleController.text.trim(),
        body: _newsBodyController.text.trim(),
      );
      _newsTitleController.clear();
      _newsBodyController.clear();
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Новость опубликована.');
    });
  }

  Future<void> _deleteNews(int newsId) async {
    await _runBusy(() async {
      await _api.deleteNews(newsId);
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Новость удалена.');
    });
  }

  Future<void> _changeLogin() async {
    await _runBusy(() async {
      final profile = await _api.changeLogin(
        _loginChangeController.text.trim(),
      );
      _loginChangeController.clear();
      await _refreshPortal(seedProfile: profile);
      _showSnack('Логин обновлён.');
    });
  }

  Future<void> _createOrganization() async {
    await _runBusy(() async {
      await _api.createOrganization(
        name: _orgNameController.text.trim(),
        slug: _orgSlugController.text.trim(),
        description: _orgDescriptionController.text.trim(),
      );
      _orgNameController.clear();
      _orgSlugController.clear();
      _orgDescriptionController.clear();
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Организация создана.');
    });
  }

  Future<void> _createUser() async {
    await _runBusy(() async {
      await _api.createUser(
        uin: _userUinController.text.trim(),
        uan: _userUanController.text.trim(),
        login: _userLoginController.text.trim(),
        password: _userPasswordController.text,
        firstName: _userFirstNameController.text.trim(),
        lastName: _userLastNameController.text.trim(),
        patronymic: _userPatronymicController.text.trim(),
        permissions: _parsePermissions(_userPermissionsController.text),
        positionTitle: _userPositionController.text.trim(),
      );
      for (final controller in [
        _userUinController,
        _userUanController,
        _userLoginController,
        _userPasswordController,
        _userFirstNameController,
        _userLastNameController,
        _userPatronymicController,
        _userPermissionsController,
        _userPositionController,
      ]) {
        controller.clear();
      }
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Пользователь создан.');
    });
  }

  Future<void> _updateSelectedUser() async {
    final userId = _selectedUserId;
    if (userId == null) {
      _showSnack('Выберите пользователя.', isError: true);
      return;
    }

    await _runBusy(() async {
      await _api.updateUser(
        userId: userId,
        uin: _userEditUinController.text.trim(),
        uan: _userEditUanController.text.trim(),
        firstName: _userEditFirstNameController.text.trim(),
        lastName: _userEditLastNameController.text.trim(),
        patronymic: _userEditPatronymicController.text.trim(),
      );
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Данные пользователя обновлены.');
    });
  }

  Future<void> _hireSelectedUser() async {
    final userId = _selectedUserId;
    final orgSlug = _selectedOrganizationSlug;
    if (userId == null || orgSlug == null || orgSlug.isEmpty) {
      _showSnack('Выберите пользователя и организацию.', isError: true);
      return;
    }

    await _runBusy(() async {
      await _api.hireUser(
        userId: userId,
        orgSlug: orgSlug,
        positionTitle: _personnelPositionController.text.trim(),
      );
      _personnelPositionController.clear();
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Назначение выполнено.');
    });
  }

  Future<void> _fireSelectedUser() async {
    final userId = _selectedUserId;
    if (userId == null) {
      _showSnack('Выберите пользователя.', isError: true);
      return;
    }

    await _runBusy(() async {
      await _api.fireUser(userId);
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Пользователь переведён в гражданский статус.');
    });
  }

  Future<void> _changePermissionsForSelectedUser() async {
    final userId = _selectedUserId;
    if (userId == null) {
      _showSnack('Выберите пользователя.', isError: true);
      return;
    }

    await _runBusy(() async {
      await _api.changeUserPermissions(
        userId,
        _parsePermissions(_assignedPermissionsController.text),
      );
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Права доступа обновлены.');
    });
  }

  Future<void> _sendRatubles() async {
    final recipientId = _selectedTransferRecipientId;
    if (recipientId == null) {
      _showSnack('Выберите получателя.', isError: true);
      return;
    }

    final amount = maybeInt(_transferAmountController.text);
    if (amount == null || amount <= 0) {
      _showSnack('Введите корректную сумму.', isError: true);
      return;
    }

    await _runBusy(() async {
      await _api.transferRatubles(
        recipientId: recipientId,
        amount: amount,
        reason: _transferReasonController.text.trim(),
      );
      _transferAmountController.clear();
      _transferReasonController.clear();
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Перевод выполнен.');
    });
  }

  Future<void> _mintRatubles() async {
    final recipientId = _selectedUserId;
    if (recipientId == null) {
      _showSnack('Выберите пользователя для начисления.', isError: true);
      return;
    }

    final amount = maybeInt(_mintAmountController.text);
    if (amount == null || amount <= 0) {
      _showSnack('Введите корректную сумму.', isError: true);
      return;
    }

    await _runBusy(() async {
      await _api.mintRatubles(
        recipientId: recipientId,
        amount: amount,
        reason: _mintReasonController.text.trim(),
      );
      _mintAmountController.clear();
      _mintReasonController.clear();
      await _refreshPortal(seedProfile: _profile);
      _showSnack('Начисление выполнено.');
    });
  }

  Future<void> _syncPushNotificationsSilently() async {
    final token = _api.token;
    if (token == null || token.isEmpty) {
      return;
    }

    try {
      final config = await _api.getPushConfig();
      final publicKey = config['public_vapid_key']?.toString() ?? '';
      if (publicKey.isEmpty) {
        return;
      }
      final status = await _pushNotifications.sync(
        publicKey: publicKey,
        token: token,
      );
      if (!mounted) {
        return;
      }
      setState(() => _pushStatus = status);
    } catch (_) {
      final status = await _pushNotifications.getStatus();
      if (!mounted) {
        return;
      }
      setState(() => _pushStatus = status);
    }
  }

  Future<void> _enablePushNotifications() async {
    await _runBusy(() async {
      final token = _api.token;
      if (token == null || token.isEmpty) {
        throw const ApiException('Сначала нужно войти в аккаунт.');
      }

      final config = await _api.getPushConfig();
      final publicKey = config['public_vapid_key']?.toString() ?? '';
      if (publicKey.isEmpty) {
        throw const ApiException('Публичный push-ключ не настроен.');
      }

      final status = await _pushNotifications.enable(
        publicKey: publicKey,
        token: token,
      );
      if (!mounted) {
        return;
      }
      setState(() => _pushStatus = status);
      _showSnack(status.message, isError: !status.enabled);
    });
  }

  Future<void> _disablePushNotifications({bool silent = false}) async {
    final token = _api.token;
    if (token == null || token.isEmpty) {
      return;
    }

    Future<void> action() async {
      final status = await _pushNotifications.disable(token: token);
      if (!mounted) {
        return;
      }
      setState(() => _pushStatus = status);
      if (!silent) {
        _showSnack('Push-уведомления отключены.');
      }
    }

    if (silent) {
      await action();
      return;
    }
    await _runBusy(action);
  }

  Future<void> _previewPushNotification() async {
    await _runBusy(() async {
      await _pushNotifications.preview();
      _showSnack('Тестовое уведомление отправлено в браузер.');
    });
  }

  int? _resolveSelectedUserId(List<JsonMap> users) {
    final ids = users.map((item) => item['id']).toSet();
    if (ids.contains(_selectedUserId)) {
      return _selectedUserId;
    }
    return users.isEmpty ? null : users.first['id'] as int;
  }

  String? _resolveSelectedOrganizationSlug(List<JsonMap> organizations) {
    final slugs = organizations.map((item) => item['slug']).toSet();
    if (slugs.contains(_selectedOrganizationSlug)) {
      return _selectedOrganizationSlug;
    }
    return organizations.isEmpty ? null : organizations.first['slug'] as String;
  }

  int? _resolveSelectedTransferRecipientId(
    List<JsonMap> directory,
    JsonMap profile,
  ) {
    final currentUserId = profile['id'];
    final recipientIds = directory
        .where((item) => item['id'] != currentUserId)
        .map((item) => item['id'])
        .toSet();
    if (recipientIds.contains(_selectedTransferRecipientId)) {
      return _selectedTransferRecipientId;
    }
    for (final item in directory) {
      if (item['id'] != currentUserId) {
        return item['id'] as int;
      }
    }
    return null;
  }

  void _selectSection(PortalSection section, [BuildContext? context]) {
    setState(() => _selectedSection = section);
    if (context != null) {
      Navigator.of(context).pop();
    }
  }

  void _toggleThemeMode() {
    final nextMode = widget.themeMode == ThemeMode.dark
        ? ThemeMode.light
        : ThemeMode.dark;
    widget.onThemeModeChanged(nextMode);
  }

  @override
  Widget build(BuildContext context) {
    if (_restoring) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_profile == null) {
      return LoginScreen(
        loading: _loading,
        passwordIdentifierController: _passwordIdentifierController,
        passwordSecretController: _passwordSecretController,
        uanIdentifierController: _uanIdentifierController,
        uanSecretController: _uanSecretController,
        onPasswordLogin: _loginWithPassword,
        onUanLogin: _loginWithUan,
        darkMode: widget.themeMode == ThemeMode.dark,
        onToggleTheme: _toggleThemeMode,
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final wide = constraints.maxWidth >= 1080;
        final page = _buildPage();

        return Scaffold(
          appBar: AppBar(
            leading: wide
                ? null
                : Builder(
                    builder: (context) => IconButton(
                      onPressed: () => Scaffold.of(context).openDrawer(),
                      icon: const Icon(Icons.menu_rounded),
                    ),
                  ),
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'RGOV',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
                Text(
                  _profile?['permissions_label']?.toString() ?? 'Пользователь',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
            actions: [
              IconButton(
                onPressed: _toggleThemeMode,
                tooltip: widget.themeMode == ThemeMode.dark
                    ? 'Светлая тема'
                    : 'Чёрная тема',
                icon: Icon(
                  widget.themeMode == ThemeMode.dark
                      ? Icons.light_mode_rounded
                      : Icons.dark_mode_rounded,
                ),
              ),
              IconButton(
                onPressed: _loading
                    ? null
                    : () =>
                          _runBusy(() => _refreshPortal(seedProfile: _profile)),
                tooltip: 'Обновить данные',
                icon: const Icon(Icons.refresh_rounded),
              ),
              if (wide)
                TextButton.icon(
                  onPressed: _loading ? null : _logout,
                  icon: const Icon(Icons.logout_rounded),
                  label: const Text('Выход'),
                )
              else
                IconButton(
                  onPressed: _loading ? null : _logout,
                  tooltip: 'Выход',
                  icon: const Icon(Icons.logout_rounded),
                ),
              const SizedBox(width: 8),
            ],
          ),
          drawer: wide ? null : _buildDrawer(context),
          body: Container(
            decoration: BoxDecoration(gradient: appBackgroundGradient(context)),
            child: Row(
              children: [
                if (wide) _buildNavigationRail(),
                Expanded(child: page),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildNavigationRail() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 8, 20),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(28),
        child: NavigationRail(
          backgroundColor: appRailColor(context),
          indicatorColor: appSoftFillColor(context),
          selectedIndex: _selectedSection.index,
          labelType: NavigationRailLabelType.all,
          onDestinationSelected: (index) {
            _selectSection(PortalSection.values[index]);
          },
          leading: Padding(
            padding: const EdgeInsets.only(top: 18),
            child: CircleAvatar(
              radius: 28,
              backgroundColor: copper,
              foregroundColor: Colors.white,
              child: Text(
                initialsFromName(_profile?['full_name']?.toString() ?? ''),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          destinations: PortalSection.values
              .map(
                (section) => NavigationRailDestination(
                  icon: Icon(section.icon),
                  label: Text(section.label),
                ),
              )
              .toList(),
        ),
      ),
    );
  }

  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: appInsetColor(context),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 24,
                    backgroundColor: copper,
                    foregroundColor: Colors.white,
                    child: Text(
                      initialsFromName(
                        _profile?['full_name']?.toString() ?? '',
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _profile?['full_name']?.toString() ?? '',
                          style: TextStyle(
                            color: appTextColor(context),
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${_profile?['permissions_label']} · Ratubles ${_profile?['ratubles'] ?? 0}',
                          style: TextStyle(
                            color: appMutedTextColor(context, 0.72),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            for (final section in PortalSection.values)
              ListTile(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                selected: section == _selectedSection,
                selectedTileColor: appSoftFillColor(context),
                leading: Icon(section.icon),
                title: Text(section.label),
                onTap: () => _selectSection(section, context),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildPage() {
    return switch (_selectedSection) {
      PortalSection.overview => OverviewPage(
        loading: _loading,
        busy: _loading,
        profile: _profile,
        did: _did,
        inbox: _inbox,
        news: _news,
        laws: _laws,
        bills: _bills,
        referenda: _referenda,
        loginChangeController: _loginChangeController,
        onChangeLogin: _changeLogin,
        pushStatus: _pushStatus,
        onEnablePush: _enablePushNotifications,
        onDisablePush: () => _disablePushNotifications(),
        onPreviewPush: _previewPushNotification,
      ),
      PortalSection.ratubles => RatublesPage(
        loading: _loading,
        busy: _loading,
        profile: _profile,
        users: _users,
        directory: _directory,
        transactions: _transactions,
        selectedRecipientId: _selectedTransferRecipientId,
        transferAmountController: _transferAmountController,
        transferReasonController: _transferReasonController,
        onSelectedRecipientChanged: (value) {
          setState(() => _selectedTransferRecipientId = value);
        },
        onSendTransfer: _sendRatubles,
      ),
      PortalSection.mail => MailPage(
        loading: _loading,
        busy: _loading,
        mailToController: _mailToController,
        mailSubjectController: _mailSubjectController,
        mailTextController: _mailTextController,
        inbox: _inbox,
        sent: _sent,
        onSendMail: _sendMail,
      ),
      PortalSection.laws => LawsPage(loading: _loading, laws: _laws),
      PortalSection.referenda => ReferendaPage(
        loading: _loading,
        busy: _loading,
        canCreateReferenda: _canCreateReferenda,
        referendumTitleController: _referendumTitleController,
        referendumDescriptionController: _referendumDescriptionController,
        referendumTextController: _referendumTextController,
        referendumLawIdController: _referendumLawIdController,
        referendumTargetLevel: _referendumTargetLevel,
        onTargetLevelChanged: (value) {
          if (value != null) {
            setState(() => _referendumTargetLevel = value);
          }
        },
        onCreateReferendum: _createReferendum,
        referenda: _referenda,
        onVoteReferendum: _voteReferendum,
        onPublishReferendum: _publishReferendum,
      ),
      PortalSection.parliament => ParliamentPage(
        loading: _loading,
        busy: _loading,
        canCreateBills: _canCreateBills,
        billTitleController: _billTitleController,
        billSummaryController: _billSummaryController,
        billTextController: _billTextController,
        billLawIdController: _billLawIdController,
        onCreateBill: _createBill,
        bills: _bills,
        onVoteBill: _voteBill,
        onPublishBill: _publishBill,
      ),
      PortalSection.news => NewsPage(
        loading: _loading,
        busy: _loading,
        canPostNews: _canPostNews,
        newsTitleController: _newsTitleController,
        newsBodyController: _newsBodyController,
        news: _news,
        onPostNews: _postNews,
        onDeleteNews: _deleteNews,
      ),
      PortalSection.admin => AdminPage(
        loading: _loading,
        busy: _loading,
        canOpenAdmin: _canOpenAdmin,
        canCreateOrganizations: _canCreateOrganizations,
        canManagePersonnel: _canManagePersonnel,
        canCreateUsers: _canCreateUsers,
        canUpdateUsers: _canUpdateUsers,
        canManagePermissions: _canManagePermissions,
        canMintRatubles: _canMintRatubles,
        canReadAdminLogs: _canReadAdminLogs,
        users: _users,
        organizations: _organizations,
        ledger: _ledger,
        adminLogs: _adminLogs,
        selectedUserId: _selectedUserId,
        selectedOrganizationSlug: _selectedOrganizationSlug,
        orgNameController: _orgNameController,
        orgSlugController: _orgSlugController,
        orgDescriptionController: _orgDescriptionController,
        userUinController: _userUinController,
        userUanController: _userUanController,
        userLoginController: _userLoginController,
        userPasswordController: _userPasswordController,
        userFirstNameController: _userFirstNameController,
        userLastNameController: _userLastNameController,
        userPatronymicController: _userPatronymicController,
        userPermissionsController: _userPermissionsController,
        userPositionController: _userPositionController,
        assignedPermissionsController: _assignedPermissionsController,
        personnelPositionController: _personnelPositionController,
        userEditUinController: _userEditUinController,
        userEditUanController: _userEditUanController,
        userEditFirstNameController: _userEditFirstNameController,
        userEditLastNameController: _userEditLastNameController,
        userEditPatronymicController: _userEditPatronymicController,
        mintAmountController: _mintAmountController,
        mintReasonController: _mintReasonController,
        onSelectedUserChanged: (value) {
          setState(() => _selectedUserId = value);
          _syncAssignedPermissionsInput(value);
          _syncSelectedUserEditor(value);
        },
        onSelectedOrganizationChanged: (value) {
          setState(() => _selectedOrganizationSlug = value);
        },
        onCreateOrganization: _createOrganization,
        onHireSelectedUser: _hireSelectedUser,
        onFireSelectedUser: _fireSelectedUser,
        onChangePermissionsForSelectedUser: _changePermissionsForSelectedUser,
        onCreateUser: _createUser,
        onUpdateSelectedUser: _updateSelectedUser,
        onMintRatubles: _mintRatubles,
      ),
    };
  }
}

enum PortalSection {
  overview('Обзор', Icons.dashboard_rounded),
  ratubles('Ratubles', Icons.savings_rounded),
  mail('GovMail', Icons.mail_rounded),
  laws('Законы', Icons.balance_rounded),
  referenda('Референдумы', Icons.how_to_vote_rounded),
  parliament('Парламент', Icons.account_balance_rounded),
  news('Новости', Icons.newspaper_rounded),
  admin('Управление', Icons.admin_panel_settings_rounded);

  const PortalSection(this.label, this.icon);

  final String label;
  final IconData icon;

  static PortalSection fromFragment(String fragment) {
    for (final section in values) {
      if (section.name == fragment) {
        return section;
      }
    }
    return PortalSection.overview;
  }
}
