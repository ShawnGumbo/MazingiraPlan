const ACCESS_TOKEN_KEY = 'access_token';
const USER_ROLE_KEY = 'user_role';
const USERNAME_KEY = 'username';

const decodeBase64Url = (value) => {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/');
  const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4);
  return atob(padded);
};

const parseTokenPayload = (token) => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const decoded = decodeBase64Url(parts[1]);
    return JSON.parse(decoded);
  } catch {
    return null;
  }
};

const isTokenActive = (token) => {
  const payload = parseTokenPayload(token);

  if (!payload) {
    return false;
  }

  if (!payload.exp) {
    return true;
  }

  return payload.exp * 1000 > Date.now();
};

export const persistSession = (accessToken, fallbackUsername = '') => {
  const payload = parseTokenPayload(accessToken) || {};
  const username = payload.username || fallbackUsername || '';
  const role = payload.role || 'USER';

  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(USERNAME_KEY, username);
  localStorage.setItem(USER_ROLE_KEY, role);

  return { username, role };
};

export const getAuthSession = () => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY) || '';
  const username = localStorage.getItem(USERNAME_KEY) || '';
  const role = localStorage.getItem(USER_ROLE_KEY) || 'USER';
  const isAuthenticated = Boolean(token) && isTokenActive(token);

  if (!isAuthenticated && token) {
    clearSession();
  }

  return {
    token,
    username: isAuthenticated ? username : '',
    role: isAuthenticated ? role : 'USER',
    isAuthenticated,
  };
};

export const clearSession = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
  localStorage.removeItem(USER_ROLE_KEY);
};