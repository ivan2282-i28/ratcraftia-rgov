import type { PushStatus } from "../types";

type EnableParams = {
  publicKey: string;
  apiBaseUrl: string;
  token: string;
};

type DisableParams = {
  apiBaseUrl: string;
  token: string;
};

const workerUrl = "/push-service-worker.js";
const appUrl = window.location.origin;
const iconUrl = `${window.location.origin}/favicon.svg`;

function isSupported() {
  return (
    "serviceWorker" in navigator &&
    "PushManager" in window &&
    "Notification" in window
  );
}

function base64UrlToUint8Array(base64Value: string) {
  const padding = "=".repeat((4 - (base64Value.length % 4)) % 4);
  const base64 = (base64Value + padding).replaceAll("-", "+").replaceAll("_", "/");
  const rawData = window.atob(base64);
  const output = new Uint8Array(rawData.length);

  for (let index = 0; index < rawData.length; index += 1) {
    output[index] = rawData.charCodeAt(index);
  }

  return output;
}

function statusMessage(
  supported: boolean,
  permission: NotificationPermission | "default",
  subscribed: boolean,
) {
  if (!supported) {
    return "Текущий браузер не поддерживает web push.";
  }
  if (permission === "denied") {
    return "Доступ к уведомлениям отклонён в настройках браузера.";
  }
  if (subscribed) {
    return "Уведомления включены и готовы к доставке.";
  }
  return "Уведомления выключены. Их можно включить из профиля.";
}

async function getRegistration() {
  if (!isSupported()) {
    return null;
  }

  return navigator.serviceWorker.register(workerUrl, {
    scope: "/",
  });
}

async function buildStatus(message?: string): Promise<PushStatus> {
  if (!isSupported()) {
    return {
      supported: false,
      permission: "default",
      subscribed: false,
      message: message ?? statusMessage(false, "default", false),
    };
  }

  const registration = await getRegistration();
  const subscription = registration
    ? await registration.pushManager.getSubscription()
    : null;
  const permission = Notification.permission || "default";

  return {
    supported: true,
    permission,
    subscribed: Boolean(subscription),
    message:
      message ?? statusMessage(true, permission, Boolean(subscription)),
  };
}

async function pushToServer(
  subscription: PushSubscription,
  apiBaseUrl: string,
  token: string,
) {
  const response = await fetch(`${apiBaseUrl}/notifications/subscriptions`, {
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
  });

  if (!response.ok) {
    throw new Error("Не удалось зарегистрировать push-подписку.");
  }
}

async function removeFromServer(
  subscription: PushSubscription,
  apiBaseUrl: string,
  token: string,
) {
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
    throw new Error("Не удалось отключить push-подписку.");
  }
}

async function ensureSubscribed(
  params: EnableParams,
  askPermission: boolean,
): Promise<PushStatus> {
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
  if (!registration) {
    return buildStatus();
  }

  let subscription = await registration.pushManager.getSubscription();
  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: base64UrlToUint8Array(params.publicKey),
    });
  }

  await pushToServer(subscription, params.apiBaseUrl, params.token);
  return buildStatus();
}

export function getPushStatus() {
  return buildStatus();
}

export function syncPushSubscription(params: EnableParams) {
  return ensureSubscribed(params, false);
}

export function enablePush(params: EnableParams) {
  return ensureSubscribed(params, true);
}

export async function disablePush(params: DisableParams) {
  if (!isSupported()) {
    return buildStatus();
  }

  const registration = await getRegistration();
  const subscription = registration
    ? await registration.pushManager.getSubscription()
    : null;

  if (subscription) {
    try {
      await removeFromServer(subscription, params.apiBaseUrl, params.token);
    } finally {
      await subscription.unsubscribe();
    }
  }

  return buildStatus("Push-уведомления отключены.");
}

export async function previewPush() {
  if (!isSupported()) {
    throw new Error("Текущий браузер не поддерживает уведомления.");
  }

  if ((Notification.permission || "default") !== "granted") {
    throw new Error("Сначала разрешите уведомления в браузере.");
  }

  const registration = await getRegistration();
  if (!registration) {
    throw new Error("Service worker недоступен.");
  }

  await registration.showNotification("RGOV", {
    body: "Тестовое уведомление Ratcraftia успешно доставлено.",
    icon: iconUrl,
    badge: iconUrl,
    tag: "rgov-preview",
    data: { url: appUrl },
  });
}
