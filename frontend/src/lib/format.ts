const dateTimeFormatter = new Intl.DateTimeFormat("ru-RU", {
  dateStyle: "medium",
  timeStyle: "short",
});

const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  dateStyle: "long",
});

export function formatDateTime(value?: string | null) {
  if (!value) {
    return "Не указано";
  }
  try {
    return dateTimeFormatter.format(new Date(value));
  } catch {
    return value;
  }
}

export function formatDate(value?: string | null) {
  if (!value) {
    return "Не указано";
  }
  try {
    return dateFormatter.format(new Date(value));
  } catch {
    return value;
  }
}

export function formatNumber(value?: number | null) {
  return new Intl.NumberFormat("ru-RU").format(value ?? 0);
}

export function shortToken(value: string, length = 18) {
  if (value.length <= length * 2) {
    return value;
  }
  return `${value.slice(0, length)}…${value.slice(-length)}`;
}

export function initials(fullName: string) {
  return fullName
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

export function sentenceCase(value: string) {
  if (!value) {
    return "";
  }
  return value.charAt(0).toUpperCase() + value.slice(1).replaceAll("_", " ");
}
