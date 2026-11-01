import { useEffect, useRef, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { ArrowUp, LogOut, MessageSquareText, Sprout } from "lucide-react";

const suggestions = [
  "What should I watch in the maize market?",
  "Summarize this season's agriculture outlook.",
  "What information is available for my region?",
];

function App() {
  const {
    error: authError,
    getAccessTokenSilently,
    isAuthenticated,
    isLoading,
    loginWithRedirect,
    logout,
    user,
  } = useAuth0();
  const [organisationId, setOrganisationId] = useState("org-demo");
  const [threadId] = useState(() => crypto.randomUUID());
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState([]);
  const [pending, setPending] = useState(false);
  const [requestError, setRequestError] = useState("");
  const messageList = useRef(null);
  const audience = import.meta.env.VITE_AUTH0_AUDIENCE;

  useEffect(() => {
    messageList.current?.scrollTo({
      top: messageList.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, pending]);

  async function sendMessage(event) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || pending) return;

    setDraft("");
    setRequestError("");
    setMessages((current) => [...current, { role: "user", content: message }]);
    setPending(true);

    try {
      const token = await getAccessTokenSilently({
        authorizationParams: { audience },
      });
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          "X-Organisation-ID": organisationId,
        },
        body: JSON.stringify({ message, thread_id: threadId }),
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || `Request failed (${response.status})`);
      }

      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.response },
      ]);
    } catch (error) {
      setRequestError(error.message || "Could not reach ZimSignal.");
    } finally {
      setPending(false);
    }
  }

  if (isLoading) {
    return (
      <main className="loading-screen" aria-live="polite">
        <span className="loading-dot" /> Checking your session
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="login-screen">
        <section className="login-copy">
          <div className="brand-lockup">
            <div className="brand-mark"><Sprout size={21} /></div>
            <span>ZimSignal</span>
          </div>
          <div className="login-message">
            <p className="eyebrow">FIELD INTELLIGENCE / ZIMBABWE</p>
            <h1>Make the next decision with better signals.</h1>
            <p className="login-description">
              Ask about markets, agriculture, and local conditions. Your
              conversations are tied to your authenticated account.
            </p>
            <button
              className="primary-button login-button"
              onClick={() => loginWithRedirect()}
            >
              Sign in to ZimSignal <ArrowUp className="button-arrow" size={17} />
            </button>
            {authError && <p className="error-message">{authError.message}</p>}
          </div>
          <p className="login-footer">Evidence first. Decisions remain yours.</p>
        </section>
        <aside className="login-aside" aria-hidden="true">
          <div className="field-lines" />
          <div className="aside-caption">
            <span>01 / RESEARCH DESK</span>
            <span>Harare · Zimbabwe</span>
          </div>
          <div className="aside-orbit orbit-one" />
          <div className="aside-orbit orbit-two" />
          <div className="signal-stamp"><Sprout size={32} /></div>
        </aside>
      </main>
    );
  }

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark"><Sprout size={20} /></div>
          <span>ZimSignal</span>
        </div>
        <div className="sidebar-label">WORKSPACE</div>
        <div className="nav-item active" aria-current="page">
          <MessageSquareText size={17} /> Intelligence chat
        </div>
        <div className="sidebar-bottom">
          <div className="profile-row">
            <div className="avatar">{(user?.name || user?.email || "U")[0].toUpperCase()}</div>
            <div className="profile-copy">
              <strong>{user?.name || "Signed-in user"}</strong>
              <span>{user?.email}</span>
            </div>
          </div>
          <button
            className="quiet-button signout-button"
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          >
            <LogOut size={16} /> Sign out
          </button>
        </div>
      </aside>

      <section className="chat-workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">ZIMBABWE / INTELLIGENCE DESK</p>
            <h1>Field intelligence</h1>
          </div>
          <label className="organisation-field">
            <span>Organisation</span>
            <input
              value={organisationId}
              onChange={(event) => setOrganisationId(event.target.value)}
              aria-label="Organisation ID"
              spellCheck="false"
            />
          </label>
        </header>

        <div className="conversation" ref={messageList} aria-live="polite">
          {messages.length === 0 ? (
            <div className="welcome-block">
              <div className="welcome-icon"><Sprout size={23} /></div>
              <p className="eyebrow">YOUR RESEARCH DESK</p>
              <h2>What would you like to understand?</h2>
              <p className="welcome-description">
                Ask a question. ZimSignal will check available evidence and
                report when the information is limited.
              </p>
              <div className="suggestions">
                {suggestions.map((suggestion) => (
                  <button
                    className="suggestion"
                    key={suggestion}
                    onClick={() => setDraft(suggestion)}
                  >
                    {suggestion}<ArrowUp size={15} />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="message-list">
              {messages.map((message, index) => (
                <article className={`message ${message.role}`} key={`${index}-${message.role}`}>
                  {message.role === "assistant" && (
                    <div className="message-mark"><Sprout size={16} /></div>
                  )}
                  <div className="message-content">
                    <span className="message-label">
                      {message.role === "assistant" ? "ZIMSIGNAL" : "YOU"}
                    </span>
                    <p>{message.content}</p>
                  </div>
                </article>
              ))}
              {pending && (
                <div className="message assistant" aria-label="ZimSignal is responding">
                  <div className="message-mark"><Sprout size={16} /></div>
                  <div className="typing-indicator"><i /><i /><i /></div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="composer-wrap">
          {requestError && <p className="request-error" role="alert">{requestError}</p>}
          <form className="composer" onSubmit={sendMessage}>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              placeholder="Ask about a market, crop, or local signal..."
              aria-label="Your message"
              rows={2}
            />
            <button
              className="send-button"
              type="submit"
              disabled={!draft.trim() || pending || !organisationId.trim()}
              aria-label="Send message"
              title="Send message"
            >
              <ArrowUp size={19} />
            </button>
          </form>
          <p className="composer-note">Answers depend on available evidence. Verify consequential decisions.</p>
        </div>
      </section>
    </main>
  );
}

export default App;