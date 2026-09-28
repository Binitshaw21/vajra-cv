import { useRef, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Check,
  CheckCircle2,
  ChevronRight,
  CloudFog,
  Cpu,
  Database,
  Download,
  FileCheck2,
  FileUp,
  KeyRound,
  LayoutDashboard,
  LoaderCircle,
  LockKeyhole,
  LogOut,
  Menu,
  Moon,
  Network,
  ScanSearch,
  ShieldCheck,
  ShieldEllipsis,
  Siren,
  Sun,
  WifiOff,
  X,
} from "lucide-react";
import { apiFetch, setApiKey } from "./api";
import SpectralSVDChart from "./components/SpectralSVDChart";
import SelfHealingTTA from "./components/SelfHealingTTA";
import MerkleDAGExplorer from "./components/MerkleDAGExplorer";
import ZKMLVerifier from "./components/ZKMLVerifier";

type TabId = 1 | 2 | 3 | 4 | 5 | 6;
const tabs: {
  id: TabId;
  label: string;
  eyebrow: string;
  icon: typeof LayoutDashboard;
}[] = [
  {
    id: 1,
    label: "Command overview",
    eyebrow: "Mission control",
    icon: LayoutDashboard,
  },
  {
    id: 2,
    label: "Poison scrubber",
    eyebrow: "Tier 01 / data integrity",
    icon: ShieldEllipsis,
  },
  {
    id: 3,
    label: "Trojan hunter",
    eyebrow: "Tier 02 / model integrity",
    icon: ScanSearch,
  },
  {
    id: 4,
    label: "ECC monitor",
    eyebrow: "Tier 03 / hardware integrity",
    icon: Cpu,
  },
  {
    id: 5,
    label: "Self-healing",
    eyebrow: "Tier 04 / environment shift",
    icon: CloudFog,
  },
  {
    id: 6,
    label: "Audit ledger",
    eyebrow: "Tier 05 / proof & provenance",
    icon: LockKeyhole,
  },
];
const tabMeta = (activeTab: TabId) =>
  tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

function StatCard({
  label,
  value,
  detail,
  tone = "blue",
  icon: Icon,
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "blue" | "red" | "green" | "amber";
  icon: typeof Activity;
}) {
  return (
    <article className={`stat-card stat-${tone}`}>
      <div className="stat-card-top">
        <span>{label}</span>
        <Icon size={17} />
      </div>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

function Overview({ onNavigate }: { onNavigate: (tab: TabId) => void }) {
  return (
    <div className="view-stack">
      <section className="mission-banner">
        <div className="mission-signal">
          <span className="pulse-dot" />
          <span>Assurance pipeline nominal</span>
        </div>
        <div className="mission-copy">
          <h2>Edge inference is protected.</h2>
          <p>
            Five independent defense tiers are watching the active model on Node
            04.
          </p>
        </div>
        <div className="mission-score">
          <span>Readiness</span>
          <strong>98.7%</strong>
          <small>+2.4% this cycle</small>
        </div>
      </section>
      <div className="stats-grid">
        <StatCard
          label="Total inferences"
          value="14,203"
          detail="Last 24 hours  ·  +8.2%"
          tone="blue"
          icon={Activity}
        />
        <StatCard
          label="Threats quarantined"
          value="312"
          detail="3 awaiting analyst review"
          tone="red"
          icon={Siren}
        />
        <StatCard
          label="Proofs generated"
          value="14,203"
          detail="100% validation rate"
          tone="green"
          icon={FileCheck2}
        />
        <StatCard
          label="Mean response"
          value="0.08 ms"
          detail="ECC recovery latency"
          tone="amber"
          icon={Cpu}
        />
      </div>
      <div className="section-heading">
        <div>
          <span className="kicker">Defense posture</span>
          <h2>Five layers. One trusted decision.</h2>
        </div>
        <span className="live-label">
          <span className="live-dot" /> Live telemetry
        </span>
      </div>
      <section className="layer-grid">
        {tabs.slice(1).map((tab, index) => {
          const Icon = tab.icon;
          const states = [
            "3 anomalies",
            "Nominal",
            "1 intercept",
            "Ready",
            "Verified",
          ];
          return (
            <button
              className="layer-card"
              key={tab.id}
              onClick={() => onNavigate(tab.id)}
            >
              <div className="layer-number">0{index + 1}</div>
              <Icon size={20} />
              <span className="layer-name">{tab.label}</span>
              <span
                className={`layer-state state-${index === 0 || index === 2 ? "alert" : "ok"}`}
              >
                {states[index]}
              </span>
              <ChevronRight size={16} className="layer-arrow" />
            </button>
          );
        })}
      </section>
      <section className="lower-grid">
        <div className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <span className="kicker">Recent activity</span>
              <h3>Assurance event stream</h3>
            </div>
            <button className="text-button" onClick={() => onNavigate(6)}>
              View ledger <ArrowUpRight size={14} />
            </button>
          </div>
          <div className="event-list">
            <div className="event-item">
              <span className="event-icon red">
                <AlertTriangle size={15} />
              </span>
              <div>
                <strong>Poisoned cluster quarantined</strong>
                <small>Module 1 · sample IDs 85, 88, 92</small>
              </div>
              <time>2m ago</time>
            </div>
            <div className="event-item">
              <span className="event-icon green">
                <Check size={15} />
              </span>
              <div>
                <strong>Inference commitment recorded</strong>
                <small>Module 3 · local ledger</small>
              </div>
              <time>6m ago</time>
            </div>
            <div className="event-item">
              <span className="event-icon amber">
                <ShieldCheck size={15} />
              </span>
              <div>
                <strong>Memory integrity ready</strong>
                <small>ECC guardian awaiting calibration</small>
              </div>
              <time>11m ago</time>
            </div>
          </div>
        </div>
        <div className="panel node-panel">
          <div className="panel-heading">
            <div>
              <span className="kicker">Node health</span>
              <h3>Operational envelope</h3>
            </div>
            <Network size={18} />
          </div>
          <div className="health-row">
            <span>
              <span className="mini-dot green-dot" /> Compute enclave
            </span>
            <strong>Healthy</strong>
          </div>
          <div className="health-row">
            <span>
              <span className="mini-dot green-dot" /> Local ledger
            </span>
            <strong>Synced</strong>
          </div>
          <div className="health-row">
            <span>
              <span className="mini-dot amber-dot" /> Sensor feed
            </span>
            <strong>Degraded</strong>
          </div>
          <div className="health-bar">
            <span style={{ width: "82%" }} />
          </div>
          <small>82% of available edge capacity</small>
        </div>
      </section>
    </div>
  );
}

interface TrojanReport {
  filename: string;
  size_bytes: number;
  sha256: string;
  verdict: string;
  l1_norms: number[];
  anomaly_indices: number[];
  suspected_trojan_classes: number[];
}

function TrojanHunter() {
  const fileInput = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [report, setReport] = useState<TrojanReport | null>(null);
  const [error, setError] = useState("");
  const [scanning, setScanning] = useState(false);

  const chooseFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setReport(null);
    setError("");
    if (file && !/\.(pth|pt|onnx)$/i.test(file.name)) {
      setSelectedFile(null);
      setError("Choose a PyTorch model (.pth or .pt) or ONNX artifact.");
      return;
    }
    setSelectedFile(file);
  };

  const scanModel = async () => {
    if (!selectedFile) return;
    setScanning(true);
    setError("");
    setReport(null);
    try {
      const formData = new FormData();
      formData.append("model", selectedFile);
      const response = await apiFetch("/api/module2/trojan-scan", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok)
        throw new Error(data.detail ?? "The model scan failed.");
      setReport(data);
    } catch (scanError) {
      setError(
        scanError instanceof Error
          ? scanError.message
          : "The model scan failed.",
      );
    } finally {
      setScanning(false);
    }
  };

  return (
    <section className="panel trojan-panel">
      <input
        ref={fileInput}
        className="visually-hidden"
        type="file"
        accept=".pth,.pt,.onnx"
        onChange={chooseFile}
      />
      {!selectedFile && !report && (
        <div className="empty-tool">
          <div className="empty-orb">
            <ScanSearch size={30} />
          </div>
          <h3>Semantic scan ready</h3>
          <p>
            Choose a signed model artifact to sweep for dormant triggers and
            backdoors.
          </p>
          <button
            className="primary-button"
            onClick={() => fileInput.current?.click()}
          >
            <FileUp size={15} /> Select model artifact
          </button>
        </div>
      )}
      {selectedFile && !report && (
        <div className="selected-model">
          <div className="file-icon">
            <FileCheck2 size={22} />
          </div>
          <div>
            <span className="kicker">Artifact selected</span>
            <h3>{selectedFile.name}</h3>
            <p>
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB · Ready for
              local analysis
            </p>
          </div>
          <button
            className="primary-button"
            disabled={scanning}
            onClick={scanModel}
          >
            {scanning ? (
              <>
                <LoaderCircle size={15} className="spin" /> Scanning...
              </>
            ) : (
              <>
                Run Trojan scan <ArrowUpRight size={15} />
              </>
            )}
          </button>
        </div>
      )}
      {report && (
        <div className="trojan-report">
          <div className="report-top">
            <div>
              <span className="kicker">Scan complete</span>
              <h3>{report.filename}</h3>
            </div>
            <span
              className={`badge ${report.verdict === "CERTIFIED_CLEAN" ? "badge-green" : "badge-red"}`}
            >
              <CheckCircle2 size={13} /> {report.verdict.replace("_", " ")}
            </span>
          </div>
          <div className="report-grid">
            <div>
              <span>Artifact SHA-256</span>
              <code>{report.sha256.slice(0, 24)}...</code>
            </div>
            <div>
              <span>Classes audited</span>
              <strong>{report.l1_norms.length}</strong>
            </div>
            <div>
              <span>Suspected classes</span>
              <strong
                className={
                  report.suspected_trojan_classes.length ? "danger-text" : ""
                }
              >
                {report.suspected_trojan_classes.length
                  ? report.suspected_trojan_classes.join(", ")
                  : "None"}
              </strong>
            </div>
          </div>
          <button
            className="secondary-button"
            onClick={() => {
              setReport(null);
              setSelectedFile(null);
            }}
          >
            Scan another artifact
          </button>
        </div>
      )}
      {error && (
        <div className="inline-error">
          <AlertTriangle size={16} /> {error}
        </div>
      )}
    </section>
  );
}

function ToolView({ activeTab }: { activeTab: TabId }) {
  if (activeTab === 2)
    return (
      <div className="tool-view">
        <div className="tool-intro">
          <span className="kicker">Tier 01 / data integrity</span>
          <h2>Poison scrubber</h2>
          <p>
            Detect covariance-matching attacks before they reach the inference
            pipeline.
          </p>
        </div>
        <div className="tool-grid">
          <SpectralSVDChart />
          <div className="panel log-panel">
            <div className="panel-heading">
              <div>
                <span className="kicker">Topological analysis</span>
                <h3>TDA quarantine log</h3>
              </div>
              <Database size={18} />
            </div>
            <div className="terminal-log">
              <p>
                <i>09:41:02</i> graph initialized
              </p>
              <p>
                <i>09:41:03</i> MST median edge: 2.14
              </p>
              <p className="log-alert">
                <i>09:41:04</i> anomalous component detected
              </p>
              <p className="log-alert">
                <i>09:41:04</i> 3 indices flagged for quarantine
              </p>
              <p className="log-ok">
                <i>09:41:05</i> clean set sealed for inference
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  if (activeTab === 4)
    return (
      <div className="tool-view">
        <div className="tool-intro">
          <span className="kicker">Tier 03 / hardware integrity</span>
          <h2>Weight-ECC monitor</h2>
          <p>
            Confidential memory protection against physical fault injection.
          </p>
        </div>
        <section className="panel ecc-panel">
          <div className="panel-heading">
            <div>
              <span className="kicker">Memory enclave / live</span>
              <h3>Fault intercept report</h3>
            </div>
            <span className="badge badge-red">
              <Siren size={13} /> Critical hijack prevented
            </span>
          </div>
          <div className="ecc-alert">
            <AlertTriangle size={20} />
            <div>
              <strong>Memory fault intercepted</strong>
              <span>
                Layer <code>2.weight</code> · Bit 30 · IEEE-754 exponent MSB
              </span>
            </div>
          </div>
          <div className="value-grid">
            <div>
              <span>Expected value</span>
              <strong>
                0x3D4CCCCD <em>(0.0500)</em>
              </strong>
            </div>
            <div>
              <span>Fault-injected RAM</span>
              <strong className="danger-text">
                0x7D4CCCCD <em>(1.70e+38)</em>
              </strong>
            </div>
          </div>
          <div className="success-line">
            <CheckCircle2 size={17} /> Hot-patch buffer restored memory in
            0.08ms
          </div>
        </section>
      </div>
    );
  if (activeTab === 5)
    return (
      <div className="tool-view">
        <div className="tool-intro">
          <span className="kicker">Tier 04 / environment shift</span>
          <h2>Self-healing inference</h2>
          <p>
            Adapt to fog, sandstorms, and sensor drift without retraining or
            network egress.
          </p>
        </div>
        <SelfHealingTTA />
      </div>
    );
  if (activeTab === 6)
    return (
      <div className="tool-view">
        <div className="tool-intro">
          <span className="kicker">Tier 05 / proof & provenance</span>
          <h2>Audit ledger</h2>
          <p>
            Verify every inference with a private proof and tamper-evident
            chain.
          </p>
        </div>
        <div className="tool-grid">
          <ZKMLVerifier />
          <MerkleDAGExplorer />
        </div>
      </div>
    );
  return (
    <div className="tool-view">
      <div className="tool-intro">
        <span className="kicker">Tier 02 / model integrity</span>
        <h2>Trojan hunter</h2>
        <p>Scan model behavior for dormant triggers and semantic backdoors.</p>
      </div>
      <TrojanHunter />
    </div>
  );
}

function ThemeToggle({
  nightMode,
  onToggle,
}: {
  nightMode: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      className="icon-button theme-toggle"
      title={nightMode ? "Switch to day mode" : "Switch to night mode"}
      aria-label={nightMode ? "Switch to day mode" : "Switch to night mode"}
      onClick={onToggle}
    >
      {nightMode ? <Sun size={17} /> : <Moon size={17} />}
    </button>
  );
}

function LandingScreen({
  onContinue,
  nightMode,
  onToggleTheme,
}: {
  onContinue: () => void;
  nightMode: boolean;
  onToggleTheme: () => void;
}) {
  return (
    <div className={`landing-shell ${nightMode ? "theme-night" : ""}`}>
      <header className="landing-nav">
        <div className="landing-brand">
          <div className="login-mark">
            <ShieldCheck size={22} />
          </div>
          <strong>
            VAJRA<span>-CV</span>
          </strong>
        </div>
        <div className="landing-actions">
          <ThemeToggle nightMode={nightMode} onToggle={onToggleTheme} />
          <button className="landing-login" onClick={onContinue}>
            Sign in <ArrowUpRight size={15} />
          </button>
        </div>
      </header>
      <main className="landing-main">
        <div className="landing-copy">
          <span className="kicker">Enterprise AI assurance</span>
          <h1>Trust every model before it reaches production.</h1>
          <p>
            One control plane for model integrity, data poisoning, provenance,
            drift, and air-gapped inference assurance.
          </p>
          <button className="landing-cta" onClick={onContinue}>
            Enter the assurance console <ArrowUpRight size={17} />
          </button>
          <div className="landing-proof">
            <span>
              <CheckCircle2 size={15} /> Signed artifacts
            </span>
            <span>
              <CheckCircle2 size={15} /> Air-gapped ready
            </span>
            <span>
              <CheckCircle2 size={15} /> Role-controlled
            </span>
          </div>
        </div>
        <div className="landing-visual">
          <div className="visual-top">
            <span className="pulse-dot" /> ASSURANCE CONTROL PLANE{" "}
            <span>NODE 04</span>
          </div>
          <div className="visual-score">
            <span>Deployment confidence</span>
            <strong>98.7%</strong>
            <small>All critical checks within policy</small>
          </div>
          <div className="visual-lines">
            <div>
              <span>Model integrity</span>
              <b>Verified</b>
            </div>
            <div>
              <span>Provenance chain</span>
              <b>Intact</b>
            </div>
            <div>
              <span>Environment drift</span>
              <b className="visual-warn">Monitored</b>
            </div>
          </div>
        </div>
      </main>
      <section className="landing-how-it-works" aria-label="How the assurance platform works">
        <div><span className="kicker">Simple control loop</span><h2>From artifact to trusted decision.</h2></div>
        <div className="landing-steps">
          <div><strong>01</strong><span>Upload</span><p>Send features, models, frames, or ledger inputs to the local assurance node.</p></div>
          <div><strong>02</strong><span>Analyze</span><p>Run integrity, poisoning, drift, provenance, and behavior checks.</p></div>
          <div><strong>03</strong><span>Decide</span><p>Review a clear SAFE, FLAGGED, CLEAN, or COMPROMISED result.</p></div>
        </div>
      </section>
    </div>
  );
}

function LoginScreen({
  onLogin,
  nightMode,
  onToggleTheme,
}: {
  onLogin: (profile: { name: string; role: string }) => void;
  nightMode: boolean;
  onToggleTheme: () => void;
}) {
  const [email, setEmail] = useState("admin@vajra.local");
  const [password, setPassword] = useState("");
  const [apiKey, setApiKeyValue] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanEmail || !password.trim() || !apiKey.trim()) {
      setError("Email, password, and API key are required.");
      return;
    }

    const profiles: Record<string, { name: string; role: string }> = {
      "admin@vajra.local": { name: "Ariana Chen", role: "Admin" },
      "operator@vajra.local": { name: "Marco Silva", role: "Operator" },
      "auditor@vajra.local": { name: "Priya Nair", role: "Auditor" },
    };

    const profile = profiles[cleanEmail] ?? {
      name: "Enterprise User",
      role: "Operator",
    };
    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setError("");
    setApiKey(apiKey);
    onLogin(profile);
  };

  return (
    <div className={`login-shell ${nightMode ? "theme-night" : ""}`}>
      <div className="login-panel">
        <div className="login-theme-toggle">
          <ThemeToggle nightMode={nightMode} onToggle={onToggleTheme} />
        </div>
        <div className="login-brand">
          <div className="login-mark">
            <ShieldCheck size={22} />
          </div>
          <div>
            <strong>VAJRA-CV</strong>
            <small>Enterprise trust platform</small>
          </div>
        </div>

        <div className="login-header">
          <span className="login-kicker">Secure access</span>
          <h1>Sign in to the assurance console</h1>
          <p>
            Protecting model integrity, provenance, and edge inference with
            zero-trust controls.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="name@company.com"
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
            />
          </label>

          <label>
            <span>API key</span>
            <input
              type="password"
              value={apiKey}
              onChange={(event) => setApiKeyValue(event.target.value)}
              placeholder="Provided by your platform administrator"
            />
          </label>

          {error && (
            <div className="login-error">
              <AlertTriangle size={15} /> {error}
            </div>
          )}

          <button className="login-button" type="submit">
            <KeyRound size={17} /> Sign in
          </button>
        </form>

        <div className="login-footer">
          <div className="login-meta">
            <span className="mini-dot green-dot" /> MDM verified
          </div>
          <div className="login-meta">
            <span className="mini-dot amber-dot" /> SSO-ready
          </div>
          <div className="login-meta">
            <span className="mini-dot green-dot" /> MFA enforced
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>(1);
  const [mobileNav, setMobileNav] = useState(false);
  const [stage, setStage] = useState<"landing" | "login" | "dashboard">(
    "landing",
  );
  const [nightMode, setNightMode] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sessionUser, setSessionUser] = useState<{
    name: string;
    role: string;
  } | null>(null);
  const meta = tabMeta(activeTab);

  if (stage === "landing")
    return (
      <LandingScreen
        onContinue={() => setStage("login")}
        nightMode={nightMode}
        onToggleTheme={() => setNightMode((value) => !value)}
      />
    );
  if (stage === "login" || !sessionUser)
    return (
      <LoginScreen
        onLogin={(profile) => {
          setSessionUser(profile);
          setStage("dashboard");
        }}
        nightMode={nightMode}
        onToggleTheme={() => setNightMode((value) => !value)}
      />
    );

  const downloadReport = () => {
    const blob = new Blob(
      [
        JSON.stringify(
          {
            product: "VAJRA-CV",
            exported_at: new Date().toISOString(),
            active_view: meta.label,
            operator: sessionUser.name,
          },
          null,
          2,
        ),
      ],
      { type: "application/json" },
    );
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "vajra-assurance-report.json";
    anchor.click();
    URL.revokeObjectURL(url);
  };
  const productNav = [
    { label: "Overview", tab: 1 as TabId },
    { label: "Models", tab: 3 as TabId },
    { label: "Integrity", tab: 2 as TabId },
    { label: "Deployments", tab: 5 as TabId },
    { label: "Reports", tab: 6 as TabId },
  ];
  return (
    <div className={`app-shell ${nightMode ? "theme-night" : ""}`}>
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""} ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={22} />
          </div>
          <div>
            <strong>
              VAJRA<span>-CV</span>
            </strong>
            <small>Edge assurance console</small>
          </div>
          <button className="close-nav" onClick={() => setMobileNav(false)}>
            <X size={18} />
          </button>
        </div>
        <div className="node-chip">
          <span className="pulse-dot" />
          <div>
            <strong>NODE 04 / ACTIVE</strong>
            <small>Air-gapped enclave</small>
          </div>
        </div>
        <nav>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                className={
                  activeTab === tab.id ? "nav-item active" : "nav-item"
                }
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setMobileNav(false);
                }}
              >
                <Icon size={18} />
                <span>{tab.label}</span>
                {activeTab === tab.id && (
                  <ChevronRight size={15} className="nav-arrow" />
                )}
              </button>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <div className="airgap-status">
            <WifiOff size={17} />
            <div>
              <strong>Zero network egress</strong>
              <small>Secure offline mode</small>
            </div>
            <span className="mini-dot green-dot" />
          </div>
          <small className="build-label">VAJRA-CV v1.4.2 · build 8421</small>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <button className="menu-button" title="Toggle navigation" aria-label="Toggle navigation" onClick={() => { setSidebarCollapsed((value) => !value); setMobileNav(true); }}>
            <Menu size={21} />
          </button>
          <div className="breadcrumb">
            <span>VAJRA-CV</span>
            <ChevronRight size={14} />
            <strong>{meta.label}</strong>
          </div>
          <nav className="product-nav" aria-label="Product navigation">
            {productNav.map((item) => (
              <button
                className={`product-nav-item ${activeTab === item.tab ? "active" : ""}`}
                key={item.label}
                onClick={() => setActiveTab(item.tab)}
              >
                {item.label}
              </button>
            ))}
          </nav>
          <div className="topbar-actions">
            <span className="secure-pill">
              <span className="mini-dot green-dot" /> Secure session
            </span>
            <button
              className="icon-button"
              title={nightMode ? "Switch to day mode" : "Switch to night mode"}
              aria-label={
                nightMode ? "Switch to day mode" : "Switch to night mode"
              }
              onClick={() => setNightMode((value) => !value)}
            >
              {nightMode ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <button
              className="icon-button"
              title="Download report"
              onClick={downloadReport}
            >
              <Download size={17} />
            </button>
            <div className="profile-wrap">
              <button className="user-chip" title="Open user profile" aria-label="Open user profile" onClick={() => setProfileOpen((value) => !value)}>
                <span>{sessionUser.name.split(" ").map((part) => part[0]).slice(0, 2).join("")}</span>
              </button>
              {profileOpen && <div className="profile-menu"><strong>{sessionUser.name}</strong><span>{sessionUser.role}</span><small>Authenticated session</small><button onClick={() => { setProfileOpen(false); setSessionUser(null); setStage("landing"); }}><LogOut size={14} /> Sign out</button></div>}
            </div>
            <button
              className="icon-button logout-button"
              title="Sign out"
              onClick={() => {
                setSessionUser(null);
                setStage("landing");
              }}
            >
              <LogOut size={16} />
            </button>
          </div>
        </header>
        <div className="content-wrap">
          <div className="product-hero">
            <div className="product-hero-text">
              <span className="kicker">AI trust platform</span>
              <h2>Protect every model release with measurable assurance.</h2>
              <p>
                VAJRA-CV helps security teams verify integrity, provenance,
                drift, and backdoor risk before deployment.
              </p>
            </div>
            <div className="product-hero-stats">
              <div>
                <strong>99.98%</strong>
                <span>Proof validation</span>
              </div>
              <div>
                <strong>312</strong>
                <span>Threats blocked</span>
              </div>
              <div>
                <strong>4.3x</strong>
                <span>Faster review</span>
              </div>
            </div>
          </div>
          <div className="page-heading">
            <div>
              <span className="kicker">{meta.eyebrow}</span>
              <h1>{activeTab === 1 ? "Command overview" : meta.label}</h1>
            </div>
            <div className="heading-meta">
              <span className="session-badge">
                <span className="mini-dot green-dot" /> {sessionUser.role}
              </span>
              <code>{sessionUser.name}</code>
            </div>
          </div>
          {activeTab === 1 ? (
            <Overview onNavigate={setActiveTab} />
          ) : (
            <ToolView activeTab={activeTab} />
          )}
        </div>
      </main>
    </div>
  );
}
