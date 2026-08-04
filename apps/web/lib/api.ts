export type User = {
  id: string;
  email: string;
  username: string;
  is_verified: boolean;
};

export type Organization = {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  role: string;
};

export type TokenBundle = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type AuthenticatedUser = TokenBundle & {
  user: User;
};

export type RegisterResponse = AuthenticatedUser & {
  organization_id: string;
};

export type LoginResponse = AuthenticatedUser;

export type RefreshResponse = TokenBundle;

export type LogoutResponse = {
  message: string;
};

export type RegisterPayload = {
  email: string;
  username: string;
  password: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RefreshPayload = {
  refresh_token: string;
};

export type LogoutPayload = {
  refresh_token: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(
  path: string,
  init?: RequestInit,
  token?: string,
): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      typeof payload?.detail === "string" ? payload.detail : "Request failed";
    throw new Error(message);
  }

  return payload as T;
}

export async function registerUser(
  payload: RegisterPayload,
): Promise<RegisterResponse> {
  return request<RegisterResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function loginUser(payload: LoginPayload): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function refreshSession(
  payload: RefreshPayload,
): Promise<RefreshResponse> {
  return request<RefreshResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function logoutSession(
  payload: LogoutPayload,
): Promise<LogoutResponse> {
  return request<LogoutResponse>("/auth/logout", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getCurrentUser(token: string): Promise<User> {
  return request<User>("/auth/me", undefined, token);
}

export async function getOrganization(
  token: string,
  organizationId: string,
): Promise<Organization> {
  return request<Organization>(
    `/auth/organizations/${organizationId}`,
    undefined,
    token,
  );
}
