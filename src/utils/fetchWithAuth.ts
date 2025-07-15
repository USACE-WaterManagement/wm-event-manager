const fetchWithAuth = async (
  input: RequestInfo | URL,
  options: RequestInit = {},
  token?: string
): Promise<Response> => {
  const headers = new Headers(options.headers);

  // Add Authorization header
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
  };

  return fetch(input, fetchOptions);
};

export default fetchWithAuth;
