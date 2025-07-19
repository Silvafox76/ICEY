    try {
      setError(null);
      setLoading(true);
      const response = await apiClient.login(username, password);
      console.log("Login API response:", response);
      if (response.access_token) {
        apiClient.setToken(response.access_token);
        const userData = await apiClient.getCurrentUser();
        console.log("User data after login:", userData);
        setUser(userData);
      }
      return response;
    } catch (error) {
      setError(error.message);
      console.error("Login error:", error);
      throw error;
    } finally {
      setLoading(false);
      console.log("Loading set to false after login");
    }