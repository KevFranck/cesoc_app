const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

function extractErrorMessage(payload, fallbackStatus) {
  if (!payload) {
    return `Erreur API ${fallbackStatus}`;
  }
  if (typeof payload === "string") {
    return payload;
  }
  if (typeof payload.detail === "string") {
    return payload.detail;
  }
  if (Array.isArray(payload.detail)) {
    return payload.detail.map((item) => item?.msg ?? String(item)).join(", ");
  }
  return `Erreur API ${fallbackStatus}`;
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let payload = null;
    try {
      payload = await response.json();
    } catch {
      payload = await response.text();
    }
    throw new Error(extractErrorMessage(payload, response.status));
  }

  return response.json();
}

export async function listWorkstations() {
  return request("/catalog/workstations");
}

export async function getAdminOverview() {
  return request("/admin/overview");
}

export async function getAdminClients() {
  return request("/admin/clients");
}

export async function resetClientPassword(userId) {
  return request(`/admin/clients/${userId}/reset-password`, {
    method: "POST",
  });
}

export async function grantClientPages(userId, pages, reason = "") {
  return request(`/admin/clients/${userId}/grant-pages`, {
    method: "POST",
    body: JSON.stringify({ pages, reason }),
  });
}

export async function getDailyReports(days = 7) {
  return request(`/admin/reports/daily?days=${days}`);
}

export async function getAdminWorkstations() {
  return request("/admin/workstations");
}

export async function createWorkstation(payload) {
  return request("/admin/workstations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateWorkstation(workstationId, payload) {
  return request(`/admin/workstations/${workstationId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
