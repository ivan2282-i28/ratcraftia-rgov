self.addEventListener("push", (event) => {
  const appUrl = new URL("../", self.registration.scope).toString();
  const iconUrl = new URL("../icons/Icon-192.png", self.registration.scope).toString();
  const badgeUrl = new URL(
    "../icons/Icon-maskable-192.png",
    self.registration.scope,
  ).toString();

  let payload = {};
  if (event.data) {
    try {
      payload = event.data.json();
    } catch (_) {
      payload = { body: event.data.text() };
    }
  }

  const title = payload.title || "RGOV";
  const options = {
    body: payload.body || "В Ratcraftia появилось новое событие.",
    icon: payload.icon || iconUrl,
    badge: payload.badge || badgeUrl,
    tag: payload.tag || "rgov-update",
    data: { url: payload.url || appUrl },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl =
    (event.notification.data && event.notification.data.url) ||
    new URL("../", self.registration.scope).toString();

  event.waitUntil(
    (async () => {
      const windows = await clients.matchAll({
        type: "window",
        includeUncontrolled: true,
      });

      for (const client of windows) {
        try {
          if ("navigate" in client) {
            await client.navigate(targetUrl);
          }
        } catch (_) {}

        if ("focus" in client) {
          await client.focus();
          return;
        }
      }

      await clients.openWindow(targetUrl);
    })(),
  );
});
