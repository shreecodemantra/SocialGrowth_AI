import { apiClient } from "./client";
import type { User } from "../types";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function registerUser(email: string, password: string, fullName?: string): Promise<User> {
  const { data } = await apiClient.post<User>("/auth/register", {
    email,
    password,
    full_name: fullName || undefined,
  });
  return data;
}

export async function login(email: string, password: string): Promise<TokenPair> {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  const { data } = await apiClient.post<TokenPair>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>("/users/me");
  return data;
}
