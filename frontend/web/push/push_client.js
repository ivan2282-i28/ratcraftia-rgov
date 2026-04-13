(function () {
  // Keep the worker at the web root so Flutter serves it at the same URL
  // we register here and the worker can own the whole app scope.
  const workerUrl = new URL("push_service_worker.js", document.baseURI);
  const workerScope = new URL("./", workerUrl);
  const appUrl = new URL("../", workerScope).toString();
  const iconUrl = new URL("../icons/Icon-192.png", workerScope).toString();
  const badgeUrl = new URL("../icons/Icon-maskable-192.png", workerScope).toString();

  function isSupported() {
    return (
      "serviceWorker" in navigator &&
      "PushManager" in window &&
      "Notification" in window
    );
  }

  function base64UrlToUint8Array(base64Value) {
    const padding = "=".repeat((4 - (base64Value.length % 4)) % 4);
    const base64 = (base64Value + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = window.atob(base64);
    const output = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; i += 1) {
      output[i] = rawData.charCodeAt(i);
    }
    return output;
  }

  function statusMessage(supported, permission, subscribed) {
    if (!supported) {
      return "Текущий браузер не поддерживает web push.";
    }
    if (permission === "denied") {
      return "Разрешение на уведомления отклонено в настройках браузера.";
    }
    if (subscribed) {
      return "Уведомления включены и готовы к доставке.";
    }
    return "Уведомления выключены. Их можно активировать прямо из профиля.";
  }

  async function getRegistration() {
    if (!isSupported()) {
      return null;
    }
    return navigator.serviceWorker.register(workerUrl.toString(), {
      scope: workerScope.pathname,
    });
  }

  async function buildStatus(message) {
    if (!isSupported()) {
      return JSON.stringify({
        supported: false,
        permission: "default",
        subscribed: false,
        message: message || statusMessage(false, "default", false),
      });
    }

    const registration = await getRegistration();
    const subscription = registration
      ? await registration.pushManager.getSubscription()
      : null;
    const permission = Notification.permission || "default";

    return JSON.stringify({
      supported: true,
      permission,
      subscribed: Boolean(subscription),
      message:
        message || statusMessage(true, permission, Boolean(subscription)),
    });
  }

  async function pushToServer(subscription, apiBaseUrl, token) {
    const response = await fetch(
      `${apiBaseUrl}/notifications/subscriptions`,
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          subscription: subscription.toJSON(),
          user_agent: navigator.userAgent,
        }),
      },
    );

    if (!response.ok) {
      throw new Error("Не удалось зарегистрировать push-подписку на сервере.");
    }
  }

  async function removeFromServer(subscription, apiBaseUrl, token) {
    const response = await fetch(
      `${apiBaseUrl}/notifications/subscriptions/unregister`,
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ endpoint: subscription.endpoint }),
      },
    );

    if (!response.ok) {
      throw new Error("Не удалось отключить push-подписку на сервере.");
    }
  }

  async function ensureSubscribed(publicKey, apiBaseUrl, token, askPermission) {
    if (!isSupported()) {
      return buildStatus();
    }

    let permission = Notification.permission || "default";
    if (permission === "default" && askPermission) {
      permission = await Notification.requestPermission();
    }

    if (permission !== "granted") {
      return buildStatus(statusMessage(true, permission, false));
    }

    const registration = await getRegistration();
    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: base64UrlToUint8Array(publicKey),
      });
    }

    await pushToServer(subscription, apiBaseUrl, token);
    return buildStatus();
  }

  window.rgovPush = {
    async getStatus() {
      return buildStatus();
    },

    async sync(publicKey, apiBaseUrl, token) {
      return ensureSubscribed(publicKey, apiBaseUrl, token, false);
    },

    async enable(publicKey, apiBaseUrl, token) {
      return ensureSubscribed(publicKey, apiBaseUrl, token, true);
    },

    async disable(apiBaseUrl, token) {
      if (!isSupported()) {
        return buildStatus();
      }

      const registration = await getRegistration();
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        try {
          await removeFromServer(subscription, apiBaseUrl, token);
        } finally {
          await subscription.unsubscribe();
        }
      }

      return buildStatus("Push-уведомления отключены.");
    },

    async preview(title, body) {
      if (!isSupported()) {
        throw new Error("Текущий браузер не поддерживает уведомления.");
      }

      if ((Notification.permission || "default") !== "granted") {
        throw new Error("Сначала разрешите уведомления в браузере.");
      }

      const registration = await getRegistration();
      await registration.showNotification(title, {
        body,
        icon: iconUrl,
        badge: badgeUrl,
        tag: "rgov-preview",
        data: { url: appUrl },
      });
    },
  };
})();
