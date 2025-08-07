const createMockAuthMethod = () => {
  let _isAuth = false;

  const mockAuthMethod = {
    async login() {
      _isAuth = true;
    },

    async logout() {
      _isAuth = false;
    },

    async isAuth() {
      return _isAuth;
    },
  };

  return mockAuthMethod;
};

export default createMockAuthMethod;
