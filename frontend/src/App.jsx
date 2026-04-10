import { useEffect, useState } from "react";

import { api, tokenStorage } from "./api";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";

function getInitialTheme() {
  const savedTheme = window.localStorage.getItem("sales-crm-theme");
  if (savedTheme === "light" || savedTheme === "dark") {
    return savedTheme;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const [token, setToken] = useState(tokenStorage.get());
  const [user, setUser] = useState(null);
  const [bootstrapping, setBootstrapping] = useState(Boolean(token));
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("sales-crm-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (!token) {
      setUser(null);
      setBootstrapping(false);
      return;
    }

    const loadUser = async () => {
      try {
        const { data } = await api.get("/me/");
        setUser(data);
      } catch (error) {
        tokenStorage.clear();
        setToken(null);
        setUser(null);
      } finally {
        setBootstrapping(false);
      }
    };

    loadUser();
  }, [token]);

  const handleLogin = (accessToken, loggedInUser) => {
    tokenStorage.set(accessToken);
    setToken(accessToken);
    setUser(loggedInUser);
  };

  const handleLogout = () => {
    tokenStorage.clear();
    setToken(null);
    setUser(null);
  };

  const handleToggleTheme = () => {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  };

  if (bootstrapping) {
    return (
      <div className="app-shell">
        <div className="panel loading-shell">
          <div className="skeleton-line skeleton-title" />
          <div className="skeleton-line" />
          <div className="skeleton-line skeleton-short" />
        </div>
      </div>
    );
  }

  if (!token || !user) {
    return <LoginPage onLogin={handleLogin} theme={theme} onToggleTheme={handleToggleTheme} />;
  }

  return <DashboardPage user={user} onLogout={handleLogout} theme={theme} onToggleTheme={handleToggleTheme} />;
}

export default App;
