self.addEventListener("push", (event) => {
  const fallbackUrl = self.registration.scope;
  let payload = {};

  if (event.data) {
    try {
      payload = event.data.json();
    } catch {
      payload = { body: event.data.text() };
    }
  }

  const title = payload.title || "RGOV";
  const options = {
    body: payload.body || "В Ratcraftia произошло новое событие.",
    icon: payload.icon || "/favicon.svg",
    badge: payload.badge || "/favicon.svg",
    tag: payload.tag || "rgov-update",
    data: { url: payload.url || fallbackUrl },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl =
    (event.notification.data && event.notification.data.url) ||
    self.registration.scope;

  event.waitUntil(
    (async () => {
      const windows = await clients.matchAll({
        type: "window",
        includeUncontrolled: true,
      });

      for (const client of windows) {
        if ("focus" in client) {
          try {
            if ("navigate" in client) {
              await client.navigate(targetUrl);
            }
          } catch {}

          await client.focus();
          return;
        }
      }

      await clients.openWindow(targetUrl);
    })(),
  );
});
