import 'dart:convert';

import 'package:http/http.dart' as http;

typedef JsonMap = Map<String, dynamic>;

const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000/api',
);

class ApiClient {
  String? token;

  Future<JsonMap> login(String identifier, String secret) async {
    final response = await _request(
      'POST',
      '/auth/login',
      body: {'identifier': identifier, 'secret': secret},
      requiresAuth: false,
    );
    return response as JsonMap;
  }

  Future<JsonMap> requestExternalAuthApplication({
    required String name,
    required String description,
    required String homepageUrl,
    required String contactEmail,
    required String redirectUri,
  }) async {
    final response = await _request(
      'POST',
      '/oauth/apps/request',
      body: {
        'name': name,
        'description': description,
        'homepage_url': homepageUrl,
        'contact_email': contactEmail,
        'redirect_uri': redirectUri,
      },
      requiresAuth: false,
    );
    return response as JsonMap;
  }

  Future<JsonMap> loginWithPassword(String identifier, String password) async {
    final response = await _request(
      'POST',
      '/auth/login/password',
      body: {'identifier': identifier, 'password': password},
      requiresAuth: false,
    );
    return response as JsonMap;
  }

  Future<JsonMap> loginWithRgov(String login, String password) async {
    final response = await _request(
      'POST',
      '/auth/login/rgov',
      body: {'login': login, 'password': password},
      requiresAuth: false,
    );
    return response as JsonMap;
  }

  Future<JsonMap> me() async => (await _request('GET', '/auth/me')) as JsonMap;

  Future<JsonMap> didToken() async =>
      (await _request('GET', '/did/me/token')) as JsonMap;

  Future<JsonMap> getPushConfig() async =>
      (await _request('GET', '/notifications/config')) as JsonMap;

  Future<List<JsonMap>> getInbox() async =>
      _jsonList(await _request('GET', '/mail/messages?box=inbox'));

  Future<List<JsonMap>> getSent() async =>
      _jsonList(await _request('GET', '/mail/messages?box=sent'));

  Future<void> sendMail({
    required String to,
    required String subject,
    required String text,
  }) async {
    await _request(
      'POST',
      '/mail/messages',
      body: {'to': to, 'subject': subject, 'text': text},
    );
  }

  Future<List<JsonMap>> getNews() async =>
      _jsonList(await _request('GET', '/news'));

  Future<void> postNews({required String title, required String body}) async {
    await _request('POST', '/news', body: {'title': title, 'body': body});
  }

  Future<void> deleteNews(int newsId) async {
    await _request('DELETE', '/news/$newsId');
  }

  Future<List<JsonMap>> getLaws() async =>
      _jsonList(await _request('GET', '/laws'));

  Future<List<JsonMap>> getBills() async =>
      _jsonList(await _request('GET', '/parliament/bills'));

  Future<JsonMap> getParliamentSummary() async =>
      (await _request('GET', '/parliament/summary')) as JsonMap;

  Future<List<JsonMap>> getParliamentElections() async =>
      _jsonList(await _request('GET', '/parliament/elections'));

  Future<void> nominateParliamentCandidate(
    int electionId, {
    String partyName = '',
  }) async {
    await _request(
      'POST',
      '/parliament/elections/$electionId/candidates',
      body: {'party_name': partyName},
    );
  }

  Future<void> signParliamentCandidate(int electionId, int candidateId) async {
    await _request(
      'POST',
      '/parliament/elections/$electionId/candidates/$candidateId/sign',
    );
  }

  Future<void> voteParliamentCandidate(
    int electionId,
    int candidateId,
    String vote,
  ) async {
    await _request(
      'POST',
      '/parliament/elections/$electionId/candidates/$candidateId/vote',
      body: {'vote': vote},
    );
  }

  Future<void> createBill({
    required String title,
    required String summary,
    required String proposedText,
    int? lawId,
  }) async {
    await _request(
      'POST',
      '/parliament/bills',
      body: {
        'title': title,
        'summary': summary,
        'proposed_text': proposedText,
        'law_id': lawId,
        'target_level': 'law',
      },
    );
  }

  Future<void> voteBill(int billId, String vote) async {
    await _request(
      'POST',
      '/parliament/bills/$billId/vote',
      body: {'vote': vote},
    );
  }

  Future<void> publishBill(int billId) async {
    await _request('POST', '/parliament/bills/$billId/publish');
  }

  Future<List<JsonMap>> getReferenda() async =>
      _jsonList(await _request('GET', '/referenda'));

  Future<void> createReferendum({
    required String title,
    required String description,
    required String proposedText,
    required String targetLevel,
    required String matterType,
    String? subjectIdentifier,
    int? lawId,
  }) async {
    await _request(
      'POST',
      '/referenda',
      body: {
        'title': title,
        'description': description,
        'proposed_text': proposedText,
        'law_id': lawId,
        'target_level': targetLevel,
        'matter_type': matterType,
        'subject_identifier': subjectIdentifier,
        'closes_in_days': 4,
      },
    );
  }

  Future<void> signReferendum(int referendumId) async {
    await _request('POST', '/referenda/$referendumId/sign');
  }

  Future<void> voteReferendum(int referendumId, String vote) async {
    await _request(
      'POST',
      '/referenda/$referendumId/vote',
      body: {'vote': vote},
    );
  }

  Future<void> publishReferendum(int referendumId) async {
    await _request('POST', '/referenda/$referendumId/publish');
  }

  Future<JsonMap> changeLogin(String login) async {
    final response = await _request(
      'POST',
      '/auth/change-login',
      body: {'new_login': login},
    );
    return response as JsonMap;
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _request(
      'POST',
      '/auth/change-password',
      body: {'current_password': currentPassword, 'new_password': newPassword},
    );
  }

  Future<List<JsonMap>> getExternalAuthApps() async =>
      _jsonList(await _request('GET', '/admin/external-auth-apps'));

  Future<JsonMap> approveExternalAuthApp(int appId) async {
    final response = await _request(
      'POST',
      '/admin/external-auth-apps/$appId/approve',
    );
    return response as JsonMap;
  }

  Future<JsonMap> deactivateExternalAuthApp(int appId) async {
    final response = await _request(
      'POST',
      '/admin/external-auth-apps/$appId/deactivate',
    );
    return response as JsonMap;
  }

  Future<List<JsonMap>> getUsers() async =>
      _jsonList(await _request('GET', '/admin/users'));

  Future<List<JsonMap>> getAdminLogs() async =>
      _jsonList(await _request('GET', '/admin/logs'));

  Future<List<JsonMap>> getOrganizations() async =>
      _jsonList(await _request('GET', '/admin/organizations'));

  Future<void> createOrganization({
    required String name,
    required String slug,
    required String description,
  }) async {
    await _request(
      'POST',
      '/admin/organizations',
      body: {
        'name': name,
        'slug': slug,
        'description': description,
        'kind': 'government',
      },
    );
  }

  Future<void> createUser({
    required String uin,
    required String uan,
    required String login,
    required String password,
    required String firstName,
    required String lastName,
    required String patronymic,
    required List<String> permissions,
    String? orgSlug,
    required String positionTitle,
  }) async {
    await _request(
      'POST',
      '/admin/users',
      body: {
        'uin': uin,
        'uan': uan,
        'login': login,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
        'patronymic': patronymic,
        'permissions': permissions,
        'org_slug': orgSlug,
        'position_title': positionTitle,
      },
    );
  }

  Future<void> updateUser({
    required int userId,
    required String uin,
    required String uan,
    required String firstName,
    required String lastName,
    required String patronymic,
  }) async {
    await _request(
      'PATCH',
      '/admin/users/$userId',
      body: {
        'uin': uin,
        'uan': uan,
        'first_name': firstName,
        'last_name': lastName,
        'patronymic': patronymic,
      },
    );
  }

  Future<void> hireUser({
    required int userId,
    required String orgSlug,
    required String positionTitle,
  }) async {
    await _request(
      'POST',
      '/admin/users/$userId/hire',
      body: {'org_slug': orgSlug, 'position_title': positionTitle},
    );
  }

  Future<void> fireUser(int userId) async {
    await _request('POST', '/admin/users/$userId/fire');
  }

  Future<void> changeUserPermissions(
    int userId,
    List<String> permissions,
  ) async {
    await _request(
      'POST',
      '/admin/users/$userId/permissions',
      body: {'permissions': permissions},
    );
  }

  Future<List<JsonMap>> getRatublesDirectory() async =>
      _jsonList(await _request('GET', '/ratubles/directory'));

  Future<List<JsonMap>> getRatublesTransactions() async =>
      _jsonList(await _request('GET', '/ratubles/transactions'));

  Future<List<JsonMap>> getRatublesLedger() async =>
      _jsonList(await _request('GET', '/ratubles/ledger'));

  Future<void> transferRatubles({
    required int recipientId,
    required String recipientKind,
    required int amount,
    required String reason,
  }) async {
    await _request(
      'POST',
      '/ratubles/transfer',
      body: {
        'recipient_id': recipientId,
        'recipient_kind': recipientKind,
        'amount': amount,
        'reason': reason,
      },
    );
  }

  Future<void> mintRatubles({
    required int recipientId,
    required String recipientKind,
    required int amount,
    required String reason,
  }) async {
    await _request(
      'POST',
      '/ratubles/mint',
      body: {
        'recipient_id': recipientId,
        'recipient_kind': recipientKind,
        'amount': amount,
        'reason': reason,
      },
    );
  }

  Future<dynamic> _request(
    String method,
    String path, {
    Object? body,
    bool requiresAuth = true,
  }) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (requiresAuth) {
      if (token == null || token!.isEmpty) {
        throw const ApiException('Сессия не активна.');
      }
      headers['Authorization'] = 'Bearer $token';
    }

    final uri = Uri.parse('$apiBaseUrl$path');
    late final http.Response response;

    switch (method) {
      case 'GET':
        response = await http.get(uri, headers: headers);
        break;
      case 'POST':
        response = await http.post(
          uri,
          headers: headers,
          body: jsonEncode(body ?? {}),
        );
        break;
      case 'PATCH':
        response = await http.patch(
          uri,
          headers: headers,
          body: jsonEncode(body ?? {}),
        );
        break;
      case 'DELETE':
        response = await http.delete(uri, headers: headers);
        break;
      default:
        throw ApiException('Неподдерживаемый метод: $method');
    }

    final decoded = response.body.isEmpty
        ? null
        : jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode >= 400) {
      final detail = decoded is Map && decoded['detail'] != null
          ? decoded['detail'].toString()
          : 'Ошибка ${response.statusCode}';
      throw ApiException(detail);
    }

    return decoded;
  }

  List<JsonMap> _jsonList(dynamic value) {
    if (value is! List) {
      return <JsonMap>[];
    }
    return value.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }
}

class ApiException implements Exception {
  const ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}
