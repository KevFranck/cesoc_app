import { useEffect, useState } from "react";
import { apiBaseUrl, closeSession, getAdminOverview, listWorkstations, loginAdmin } from "./api";

const emptyOverview = {
  report: {
    date: "",
    total_connections: 0,
    active_sessions: 0,
    total_minutes_used: 0,
    total_print_jobs: 0,
    total_pages_printed: 0,
    blocked_print_jobs: 0,
  },
  active_sessions: [],
  recent_sessions: [],
  recent_print_jobs: [],
};

function LoginScreen({ workstations, onLogin, loading, error }) {
  const [externalId, setExternalId] = useState("ADM-001");
  const [workstationName, setWorkstationName] = useState(workstations[0]?.name ?? "POSTE-01");

  useEffect(() => {
    if (!workstations.length) {
      return;
    }
    setWorkstationName((current) => current || workstations[0].name);
  }, [workstations]);

  function handleSubmit(event) {
    event.preventDefault();
    onLogin(externalId.trim(), workstationName);
  }

  return (
    <div className="login-shell">
      <section className="hero-card">
        <p className="eyebrow">CESOC Administration</p>
        <h1>Superviser les postes, les sessions et les impressions.</h1>
        <p className="hero-copy">
          Cette interface web est destinee aux comptes administrateurs et superviseurs. Elle
          centralise la frequentation, les sessions actives et les usages d&apos;impression.
        </p>
        <div className="hero-meta">
          <span>API cible : {apiBaseUrl}</span>
          <span>Compte demo : ADM-001</span>
        </div>
      </section>

      <section className="login-card">
        <h2>Connexion admin</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Identifiant
            <input
              value={externalId}
              onChange={(event) => setExternalId(event.target.value)}
              placeholder="ADM-001"
            />
          </label>

          <label>
            Poste
            <select
              value={workstationName}
              onChange={(event) => setWorkstationName(event.target.value)}
            >
              {workstations.map((workstation) => (
                <option key={workstation.id} value={workstation.name}>
                  {workstation.name}
                </option>
              ))}
            </select>
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Connexion..." : "Ouvrir le tableau de bord"}
          </button>
        </form>
        {error ? <p className="error-text">{error}</p> : null}
      </section>
    </div>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <article className={`stat-card stat-${accent}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function DataTable({ title, columns, rows, renderRow, emptyMessage }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h3>{title}</h3>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length ? (
              rows.map((row, index) => renderRow(row, index))
            ) : (
              <tr>
                <td colSpan={columns.length} className="empty-cell">
                  {emptyMessage}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Dashboard({ session, overview, onRefresh, onLogout, loading, error }) {
  const { report } = overview;

  return (
    <div className="dashboard-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Vue admin CESOC</p>
          <h1>{session.userName}</h1>
          <p className="hero-copy">
            Session admin ouverte sur {session.workstationName}. Derniere actualisation :
            {" "}
            {new Date().toLocaleTimeString("fr-CA")}
          </p>
        </div>
        <div className="topbar-actions">
          <button className="secondary-button" onClick={onRefresh} disabled={loading}>
            {loading ? "Actualisation..." : "Actualiser"}
          </button>
          <button className="danger-button" onClick={onLogout}>
            Fermer ma session
          </button>
        </div>
      </header>

      {error ? <div className="banner error-banner">{error}</div> : null}

      <section className="stats-grid">
        <StatCard label="Connexions du jour" value={report.total_connections} accent="gold" />
        <StatCard label="Sessions actives" value={report.active_sessions} accent="teal" />
        <StatCard label="Minutes utilisees" value={report.total_minutes_used} accent="sage" />
        <StatCard label="Pages imprimees" value={report.total_pages_printed} accent="coral" />
      </section>

      <section className="stats-grid compact-grid">
        <StatCard label="Impressions bloquees" value={report.blocked_print_jobs} accent="berry" />
        <StatCard label="Travaux d'impression" value={report.total_print_jobs} accent="slate" />
        <StatCard label="Date du rapport" value={report.date || "-"} accent="sand" />
      </section>

      <div className="panels-grid">
        <DataTable
          title="Sessions actives"
          columns={["Identifiant", "Utilisateur", "Poste", "Debut"]}
          rows={overview.active_sessions}
          emptyMessage="Aucune session active."
          renderRow={(sessionRow) => (
            <tr key={`active-${sessionRow.id}`}>
              <td>{sessionRow.user.external_id}</td>
              <td>{sessionRow.user.first_name} {sessionRow.user.last_name}</td>
              <td>{sessionRow.workstation.name}</td>
              <td>{new Date(sessionRow.started_at).toLocaleString("fr-CA")}</td>
            </tr>
          )}
        />

        <DataTable
          title="Sessions recentes"
          columns={["Identifiant", "Utilisateur", "Statut", "Poste", "Duree"]}
          rows={overview.recent_sessions}
          emptyMessage="Aucune session recente."
          renderRow={(sessionRow) => (
            <tr key={`recent-${sessionRow.id}`}>
              <td>{sessionRow.user.external_id}</td>
              <td>{sessionRow.user.first_name} {sessionRow.user.last_name}</td>
              <td>{sessionRow.status}</td>
              <td>{sessionRow.workstation.name}</td>
              <td>{sessionRow.duration_minutes} min</td>
            </tr>
          )}
        />
      </div>

      <DataTable
        title="Impressions recentes"
        columns={["Identifiant", "Utilisateur", "Pages", "Statut", "Poste", "Horodatage"]}
        rows={overview.recent_print_jobs}
        emptyMessage="Aucune impression recente."
        renderRow={(job) => (
          <tr key={`print-${job.id}`}>
            <td>{job.user.external_id}</td>
            <td>{job.user.first_name} {job.user.last_name}</td>
            <td>{job.pages}</td>
            <td>{job.status}</td>
            <td>{job.workstation.name}</td>
            <td>{new Date(job.printed_at).toLocaleString("fr-CA")}</td>
          </tr>
        )}
      />
    </div>
  );
}

export default function App() {
  const [workstations, setWorkstations] = useState([]);
  const [loginError, setLoginError] = useState("");
  const [dashboardError, setDashboardError] = useState("");
  const [loadingLogin, setLoadingLogin] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [overview, setOverview] = useState(emptyOverview);
  const [adminSession, setAdminSession] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function bootstrap() {
      try {
        const workstationData = await listWorkstations();
        if (isMounted) {
          setWorkstations(workstationData);
        }
      } catch (error) {
        if (isMounted) {
          setLoginError(error.message);
        }
      }
    }

    bootstrap();
    return () => {
      isMounted = false;
    };
  }, []);

  async function handleLogin(externalId, workstationName) {
    setLoadingLogin(true);
    setLoginError("");

    try {
      const payload = await loginAdmin(externalId, workstationName);
      if (payload.user.role !== "admin") {
        throw new Error("Ce compte n'a pas les droits administrateur.");
      }

      setAdminSession({
        sessionId: payload.session.id,
        userName: `${payload.user.first_name} ${payload.user.last_name}`,
        externalId: payload.user.external_id,
        workstationName: payload.session.workstation.name,
      });
    } catch (error) {
      setLoginError(error.message);
    } finally {
      setLoadingLogin(false);
    }
  }

  async function loadOverview() {
    setLoadingDashboard(true);
    setDashboardError("");

    try {
      const overviewPayload = await getAdminOverview();
      setOverview(overviewPayload);
    } catch (error) {
      setDashboardError(error.message);
    } finally {
      setLoadingDashboard(false);
    }
  }

  useEffect(() => {
    if (!adminSession) {
      return;
    }
    loadOverview();
  }, [adminSession]);

  async function handleLogout() {
    if (!adminSession) {
      return;
    }

    try {
      await closeSession(adminSession.sessionId);
    } catch (error) {
      setDashboardError(error.message);
    }

    setAdminSession(null);
    setOverview(emptyOverview);
  }

  if (!adminSession) {
    return (
      <LoginScreen
        workstations={workstations}
        onLogin={handleLogin}
        loading={loadingLogin}
        error={loginError}
      />
    );
  }

  return (
    <Dashboard
      session={adminSession}
      overview={overview}
      onRefresh={loadOverview}
      onLogout={handleLogout}
      loading={loadingDashboard}
      error={dashboardError}
    />
  );
}
