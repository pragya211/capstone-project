import React, { useEffect, useRef, useState } from "react";
import PdfUploader from "./pdfUploader";
import AdvancedPdfProcessor from "./AdvancedPdfProcessor";
import ResearchAssessment from "./ResearchAssessment";
import { useAuth } from "./context/AuthContext";
import LoginForm from "./components/LoginForm";
import SignupForm from "./components/SignupForm";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("basic");
  const [authMode, setAuthMode] = useState("login");
  const { user, logout } = useAuth();
  const [isHeaderScrolled, setIsHeaderScrolled] = useState(false);
  const authSectionRef = useRef(null);
  const tabPanelsRef = useRef(null);

  // Shared state for both components
  const [sharedFile, setSharedFile] = useState(null);
  const [sharedSections, setSharedSections] = useState(null);
  const [sharedSummaries, setSharedSummaries] = useState(null);
  const [sharedEnhancedData, setSharedEnhancedData] = useState(null);
  const [sharedProcessingData, setSharedProcessingData] = useState(null);
  const [sharedAssessmentData, setSharedAssessmentData] = useState(null);
  const [sharedLoadingExtract, setSharedLoadingExtract] = useState(false);
  const [sharedLoadingSummary, setSharedLoadingSummary] = useState(false);
  const [sharedLoadingAdvanced, setSharedLoadingAdvanced] = useState(false);
  const [sharedLoadingAssessment, setSharedLoadingAssessment] = useState(false);

  const heroHighlights = [
    {
      icon: "⚡",
      title: "Instant Summaries",
      description: "Auto-extract sections and generate crisp AI summaries in seconds.",
      target: "basic",
      requiresAuth: false,
    },
    {
      icon: "🧠",
      title: "Deep PDF Insights",
      description: "Surface citations, figures, tables, and keywords with zero manual work.",
      target: "advanced",
      requiresAuth: true,
    },
    {
      icon: "🎯",
      title: "Research Readiness",
      description: "Assess completeness and uncover missing content before you publish.",
      target: "assessment",
      requiresAuth: true,
    },
  ];

  const heroMetrics = [
    { label: "Average summary time", value: "45s" },
    { label: "Citations extracted", value: "20+" },
    { label: "AI insights generated", value: "5 per paper" },
  ];

  useEffect(() => {
    if (!user && activeTab !== "basic") {
      setActiveTab("basic");
    }
  }, [user, activeTab]);

  useEffect(() => {
    const handleScroll = () => {
      setIsHeaderScrolled(window.scrollY > 16);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (ref) => {
    if (ref?.current) {
      ref.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const handleHighlightClick = (target) => {
    const requiresAuth = target === "advanced" || target === "assessment";
    if (requiresAuth && !user) {
      setAuthMode("login");
      scrollToSection(authSectionRef);
      return;
    }

    setActiveTab(target);
    const raf = typeof window !== "undefined" ? window.requestAnimationFrame : null;
    if (typeof raf === "function") {
      raf(() => scrollToSection(tabPanelsRef));
    } else {
      scrollToSection(tabPanelsRef);
    }
  };

  const renderAuthHeader = () => (
    <header className={`app-header ${isHeaderScrolled ? "is-scrolled" : ""}`}>
      <div className="brand">
        <div className="brand__badge">RC</div>
        <div className="brand__copy">
          <h1>Research Companion</h1>
          <p>Amplify your research workflow with guided AI assistance.</p>
        </div>
      </div>
      <div className="header-actions">
        {user ? (
          <div className="user-chip">
            <div className="user-chip__meta">
              <span className="user-chip__name">{user.full_name || user.email}</span>
              <span className="user-chip__status">Signed in</span>
            </div>
            <button className="ghost-button ghost-button--danger" onClick={logout}>
              Log Out
            </button>
          </div>
        ) : (
          <div className="auth-toggle">
            <button
              type="button"
              className={`auth-toggle__button ${authMode === "login" ? "is-active" : ""}`}
              onClick={() => {
                setAuthMode("login");
                scrollToSection(authSectionRef);
              }}
            >
              Log In
            </button>
            <button
              type="button"
              className={`auth-toggle__button auth-toggle__button--accent ${
                authMode === "signup" ? "is-active" : ""
              }`}
              onClick={() => {
                setAuthMode("signup");
                scrollToSection(authSectionRef);
              }}
            >
              Sign Up
            </button>
          </div>
        )}
      </div>
    </header>
  );

  const renderHero = () => (
    <section className={`app-hero ${user ? "app-hero--compact" : ""}`}>
      <div className="app-hero__inner">
        <div className="app-hero__copy">
          <span className="app-hero__eyebrow">AI-assisted literature review</span>
          <h2>
            Distill dense research papers
            <br />
            into actionable insights.
          </h2>
          <p>
            Upload PDFs, extract structure, generate summaries, and evaluate completeness — all within a single
            cohesive workspace.
          </p>
          {!user && (
            <div className="app-hero__cta">
              Create an account to unlock the advanced processor and research assessment dashboards.
            </div>
          )}
          <div className="metric-row">
            {heroMetrics.map((metric) => (
              <div key={metric.label} className="metric-pill">
                <span className="metric-pill__value">{metric.value}</span>
                <span className="metric-pill__label">{metric.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="app-hero__grid">
          {heroHighlights.map((highlight) => (
            <button
              key={highlight.title}
              type="button"
              className={`highlight-card ${
                highlight.requiresAuth && !user ? "highlight-card--locked" : ""
              }`}
              onClick={() => handleHighlightClick(highlight.target)}
            >
              <div className="highlight-card__icon">{highlight.icon}</div>
              <div className="highlight-card__content">
                <h3>{highlight.title}</h3>
                <p>{highlight.description}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );

  const renderAuthForms = () => {
    if (user) {
      return null;
    }

    return (
      <section ref={authSectionRef} className="auth-section">
        <div className="auth-section__panel">
          {authMode === "login" ? (
            <LoginForm />
          ) : (
            <SignupForm onSuccess={() => setAuthMode("login")} />
          )}
          <p className="auth-section__hint">
            {authMode === "login" ? (
              <>
                New to Research Companion?{" "}
                <button type="button" onClick={() => setAuthMode("signup")}>
                  Create an account
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button type="button" onClick={() => setAuthMode("login")}>
                  Log in instead
                </button>
              </>
            )}
          </p>
        </div>
        <div className="auth-section__highlights">
          <div className="auth-section__badge">Why teams choose us</div>
          <ul>
            <li>Glassmorphic workspace with focus-friendly layout.</li>
            <li>One-click AI summaries tuned for academic tone.</li>
            <li>Deep PDF parsing to capture citations, tables, and keywords.</li>
            <li>Assessment scores that flag missing or weak sections instantly.</li>
          </ul>
        </div>
      </section>
    );
  };

  const renderTabButton = (id, label, disabled = false) => {
    const isActive = activeTab === id;
    return (
      <button
        key={id}
        type="button"
        className={`tab-button ${isActive ? "is-active" : ""} ${disabled ? "is-disabled" : ""}`}
        onClick={() => {
          if (!disabled) {
            setActiveTab(id);
          }
        }}
        disabled={disabled}
      >
        {label}
      </button>
    );
  };

  return (
    <div className="app-shell">
      <div className="app-backdrop" />
      <div className="app-backdrop app-backdrop--accent" />
      {renderAuthHeader()}
      <main className="app-main">
        {renderHero()}
        {renderAuthForms()}
        <div className="tabs-nav">
          <div className="tab-bar">
            {renderTabButton("basic", "Basic Summarizer")}
            {renderTabButton("advanced", "Advanced Processor", !user)}
            {renderTabButton("assessment", "Research Assessment", !user)}
          </div>
        </div>
        <section ref={tabPanelsRef} className="tab-panels">
          {activeTab === "basic" && (
            <PdfUploader
              sharedFile={sharedFile}
              setSharedFile={setSharedFile}
              sharedSections={sharedSections}
              setSharedSections={setSharedSections}
              sharedSummaries={sharedSummaries}
              setSharedSummaries={setSharedSummaries}
              sharedEnhancedData={sharedEnhancedData}
              setSharedEnhancedData={setSharedEnhancedData}
              sharedLoadingExtract={sharedLoadingExtract}
              setSharedLoadingExtract={setSharedLoadingExtract}
              sharedLoadingSummary={sharedLoadingSummary}
              setSharedLoadingSummary={setSharedLoadingSummary}
            />
          )}
          {activeTab === "advanced" && (
            <AdvancedPdfProcessor
              sharedFile={sharedFile}
              setSharedFile={setSharedFile}
              sharedProcessingData={sharedProcessingData}
              setSharedProcessingData={setSharedProcessingData}
              sharedLoadingAdvanced={sharedLoadingAdvanced}
              setSharedLoadingAdvanced={setSharedLoadingAdvanced}
              sharedSummaries={sharedSummaries}
              setSharedSummaries={setSharedSummaries}
              sharedLoadingSummary={sharedLoadingSummary}
              setSharedLoadingSummary={setSharedLoadingSummary}
            />
          )}
          {activeTab === "assessment" && (
            <ResearchAssessment
              sharedFile={sharedFile}
              setSharedFile={setSharedFile}
              sharedAssessmentData={sharedAssessmentData}
              setSharedAssessmentData={setSharedAssessmentData}
              sharedLoadingAssessment={sharedLoadingAssessment}
              setSharedLoadingAssessment={setSharedLoadingAssessment}
            />
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
