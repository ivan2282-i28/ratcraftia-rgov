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
      message = 'Push-уведомления недоступны в текущей сборке.';

  final bool supported;
  final String permission;
  final bool subscribed;
  final String message;

  bool get enabled => supported && permission == 'granted' && subscribed;
}

class PushNotificationService {
  Future<PushNotificationStatus> getStatus() async =>
      const PushNotificationStatus.initial();

  Future<PushNotificationStatus> sync({
    required String publicKey,
    required String token,
  }) async => const PushNotificationStatus.initial();

  Future<PushNotificationStatus> enable({
    required String publicKey,
    required String token,
  }) async => const PushNotificationStatus.initial();

  Future<PushNotificationStatus> disable({required String token}) async =>
      const PushNotificationStatus.initial();

  Future<void> preview() async {}
}
