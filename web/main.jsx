import React from "react";
import { createRoot } from "react-dom/client";
import { Auth0Provider } from "@auth0/auth0-react";
import App from "./App.jsx";
import "./styles.css";

const configuration = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN,
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
  audience: import.meta.env.VITE_AUTH0_AUDIENCE,
};

function MissingConfiguration() {
  return (
    <main className="setup-screen">
      <div className="setup-panel">
        <div className="brand-mark">Z</div>
        <p className="eyebrow">ZimSignal / local setup</p>
        <h1>Connect your sign-in</h1>
        <p>
          Add the public Auth0 SPA settings to the project-root <code>.env</code>,
          then restart <code>npm run dev</code>.
        </p>
        <pre>{`VITE_AUTH0_DOMAIN=your-tenant.us.auth0.com
VITE_AUTH0_CLIENT_ID=your-spa-client-id
VITE_AUTH0_AUDIENCE=https://zimsignal-api`}</pre>
        <p className="setup-note">
          Use the SPA application’s Domain and Client ID. Never put its client
          secret in frontend variables.
        </p>
      </div>
    </main>
  );
}

const root = createRoot(document.getElementById("root"));

if (!configuration.domain || !configuration.clientId || !configuration.audience) {
  root.render(<MissingConfiguration />);
} else {
  root.render(
    <React.StrictMode>
      <Auth0Provider
        domain={configuration.domain}
        clientId={configuration.clientId}
        authorizationParams={{
          redirect_uri: window.location.origin,
          audience: configuration.audience,
        }}
        cacheLocation="memory"
      >
        <App />
      </Auth0Provider>
    </React.StrictMode>,
  );
}