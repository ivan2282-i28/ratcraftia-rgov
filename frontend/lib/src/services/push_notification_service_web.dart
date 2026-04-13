import 'dart:convert';
import 'dart:js_interop';

import 'api_client.dart';

@JS('window.rgovPush')
external _PushBridge? get _pushBridge;

extension type _PushBridge(JSObject _) implements JSObject {
  external JSPromise<JSString> getStatus();
  external JSPromise<JSString> sync(
    JSString publicKey,
    JSString apiBaseUrl,
    JSString token,
  );
  external JSPromise<JSString> enable(
    JSString publicKey,
    JSString apiBaseUrl,
    JSString token,
  );
  external JSPromise<JSString> disable(JSString apiBaseUrl, JSString token);
  external JSPromise<JSAny?> preview(JSString title, JSString body);
}

class PushNotificationStatus {
  const PushNotificationStatus({
    required this.supported,
    required this.permission,
    required this.subscribed,
    required this.message,
  });

  const PushNotificationStatus.initial()
    : supported = false,
      permission = 'default',
      subscribed = false,
      message = 'Push-уведомления пока не настроены.';

  final bool supported;
  final String permission;
  final bool subscribed;
  final String message;

  bool get enabled => supported && permission == 'granted' && subscribed;

  factory PushNotificationStatus.fromJsonString(String value) {
    final payload = jsonDecode(value);
    if (payload is! Map<String, dynamic>) {
      return const PushNotificationStatus.initial();
    }

    return PushNotificationStatus(
      supported: payload['supported'] == true,
      permission: payload['permission']?.toString() ?? 'default',
      subscribed: payload['subscribed'] == true,
      message: payload['message']?.toString() ?? 'Push-уведомления обновлены.',
    );
  }
}

class PushNotificationService {
  Future<PushNotificationStatus> getStatus() async {
    final bridge = _pushBridge;
    if (bridge == null) {
      return const PushNotificationStatus.initial();
    }
    final result = await bridge.getStatus().toDart;
    return PushNotificationStatus.fromJsonString(result.toDart);
  }

  Future<PushNotificationStatus> sync({
    required String publicKey,
    required String token,
  }) async {
    final bridge = _pushBridge;
    if (bridge == null) {
      return const PushNotificationStatus.initial();
    }
    final result = await bridge
        .sync(publicKey.toJS, apiBaseUrl.toJS, token.toJS)
        .toDart;
    return PushNotificationStatus.fromJsonString(result.toDart);
  }

  Future<PushNotificationStatus> enable({
    required String publicKey,
    required String token,
  }) async {
    final bridge = _pushBridge;
    if (bridge == null) {
      return const PushNotificationStatus.initial();
    }
    final result = await bridge
        .enable(publicKey.toJS, apiBaseUrl.toJS, token.toJS)
        .toDart;
    return PushNotificationStatus.fromJsonString(result.toDart);
  }

  Future<PushNotificationStatus> disable({required String token}) async {
    final bridge = _pushBridge;
    if (bridge == null) {
      return const PushNotificationStatus.initial();
    }
    final result = await bridge.disable(apiBaseUrl.toJS, token.toJS).toDart;
    return PushNotificationStatus.fromJsonString(result.toDart);
  }

  Future<void> preview() async {
    final bridge = _pushBridge;
    if (bridge == null) {
      return;
    }
    await bridge
        .preview(
          'RGOV'.toJS,
          'Тестовое уведомление Ratcraftia успешно доставлено.'.toJS,
        )
        .toDart;
  }
}
