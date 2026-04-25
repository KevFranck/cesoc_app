const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Erreur API ${response.status}: ${detail}`);
  }

  return response.json();
}

export async function listWorkstations() {
  return request("/catalog/workstations");
}

export async function loginAdmin(externalId, workstationName) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      external_id: externalId,
      workstation_name: workstationName,
    }),
  });
}

export async function getAdminOverview() {
  return request("/admin/overview");
}

export async function closeSession(sessionId) {
  return request(`/sessions/${sessionId}/close`, {
    method: "POST",
  });
}

export { apiBaseUrl };
