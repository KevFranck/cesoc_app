import { useEffect, useMemo, useState } from "react";
import {
  createWorkstation,
  getAdminClients,
  getAdminOverview,
  getAdminWorkstations,
  getDailyReports,
  grantClientPages,
  resetClientPassword,
  updateWorkstation,
} from "./api";

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

const navItems = [
  { id: "dashboard", label: "Dashboard", description: "Analyses et activite du jour" },
  { id: "clients", label: "Clients", description: "Liste et gestion des comptes" },
  { id: "workstations", label: "Postes", description: "Ajout et gestion des postes" },
  { id: "reports", label: "Rapports", description: "Historique journalier" },
];

const defaultPage = "dashboard";

function getInitialPage() {
  const params = new URLSearchParams(window.location.search);
  const page = params.get("page");
  if (page && navItems.some((item) => item.id === page)) {
    return page;
  }
  return defaultPage;
}

function formatDateTime(value) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString("fr-CA");
}

function formatDateForCsv(value) {
  if (!value) {
    return "";
  }
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-");
    return `${day}/${month}/${year}`;
  }
  return value;
}

function formatMetric(value) {
  const numericValue = Number(value ?? 0);
  if (Number.isNaN(numericValue)) {
    return "0";
  }
  return new Intl.NumberFormat("fr-CA").format(numericValue);
}

function downloadCsv(filename, rows) {
  const csvContent = rows.map((row) => row.map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(";")).join("\n");
  const blob = new Blob([`\ufeff${csvContent}`], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function StatCard({ label, value, accent, hint }) {
  return (
    <article className={`stat-card stat-${accent}`}>
      <span>{label}</span>
      <strong>{formatMetric(value)}</strong>
      {hint ? <small>{hint}</small> : null}
    </article>
  );
}

function Panel({ title, subtitle, actions, children }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3>{title}</h3>
          {subtitle ? <p className="panel-subtitle">{subtitle}</p> : null}
        </div>
        {actions ? <div className="panel-actions">{actions}</div> : null}
      </div>
      {children}
    </section>
  );
}

function DataTable({ columns, rows, renderRow, emptyMessage }) {
  return (
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
  );
}

function Modal({ title, children, onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button type="button" className="secondary-button table-button" onClick={onClose}>
            Fermer
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

function Sidebar({ activePage, onSelectPage }) {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <p className="eyebrow">CESOC Admin</p>
        <h1>Console de supervision</h1>
        <p>
          Une interface separee pour suivre les postes, les clients et les rapports sans surcharger une seule page.
        </p>
      </div>

      <nav className="nav-list">
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`nav-item ${activePage === item.id ? "nav-item-active" : ""}`}
            onClick={() => onSelectPage(item.id)}
          >
            <span>{item.label}</span>
            <small>{item.description}</small>
          </button>
        ))}
      </nav>
    </aside>
  );
}

function DashboardPage({ overview, loading, onRefresh }) {
  const safeReport = { ...emptyOverview.report, ...(overview?.report ?? {}) };
  const activeSessions = overview?.active_sessions ?? [];
  const recentSessions = overview?.recent_sessions ?? [];
  const recentPrintJobs = overview?.recent_print_jobs ?? [];

  return (
    <div className="page-grid">
      <div className="stats-grid">
        <StatCard label="Connexions du jour" value={safeReport.total_connections} accent="green" hint="Sessions ouvertes aujourd'hui" />
        <StatCard label="Sessions actives" value={safeReport.active_sessions} accent="blue" hint="Postes actuellement utilises" />
        <StatCard label="Minutes utilisees" value={safeReport.total_minutes_used} accent="gold" hint="Temps cumule du jour" />
        <StatCard label="Pages imprimees" value={safeReport.total_pages_printed} accent="pink" hint="Pages autorisees aujourd'hui" />
      </div>

      <div className="stats-grid compact-grid">
        <StatCard label="Impressions bloquees" value={safeReport.blocked_print_jobs} accent="pink" hint="Quota atteint" />
        <StatCard label="Travaux d'impression" value={safeReport.total_print_jobs} accent="blue" hint="Tous statuts confondus" />
        <StatCard label="Date analysee" value={safeReport.date || "-"} accent="green" hint="Base du rapport" />
      </div>

      <Panel title="Synthese du jour" subtitle="Lecture rapide des indicateurs principaux">
        <div className="overview-strip">
          <div className="overview-item">
            <span className="overview-label">Connexions</span>
            <strong>{formatMetric(safeReport.total_connections)}</strong>
          </div>
          <div className="overview-item">
            <span className="overview-label">Minutes</span>
            <strong>{formatMetric(safeReport.total_minutes_used)}</strong>
          </div>
          <div className="overview-item">
            <span className="overview-label">Pages</span>
            <strong>{formatMetric(safeReport.total_pages_printed)}</strong>
          </div>
          <div className="overview-item">
            <span className="overview-label">Impressions bloquees</span>
            <strong>{formatMetric(safeReport.blocked_print_jobs)}</strong>
          </div>
        </div>
      </Panel>

      <div className="two-column-grid">
        <Panel
          title="Sessions actives"
          subtitle="Vue immediate des postes occupes"
          actions={
            <button className="primary-button" onClick={onRefresh} disabled={loading}>
              {loading ? "Actualisation..." : "Actualiser"}
            </button>
          }
        >
          <DataTable
            columns={["Email", "Utilisateur", "Poste", "Debut"]}
            rows={activeSessions}
            emptyMessage="Aucune session active."
            renderRow={(sessionRow) => (
              <tr key={`active-${sessionRow.id}`}>
                <td>{sessionRow.user.email}</td>
                <td>{sessionRow.user.first_name} {sessionRow.user.last_name}</td>
                <td>{sessionRow.workstation.name}</td>
                <td>{formatDateTime(sessionRow.started_at)}</td>
              </tr>
            )}
          />
        </Panel>

        <Panel title="Sessions recentes" subtitle="Dernieres sessions fermees ou en cours">
          <DataTable
            columns={["Email", "Utilisateur", "Statut", "Poste", "Duree"]}
            rows={recentSessions}
            emptyMessage="Aucune session recente."
            renderRow={(sessionRow) => (
              <tr key={`recent-${sessionRow.id}`}>
                <td>{sessionRow.user.email}</td>
                <td>{sessionRow.user.first_name} {sessionRow.user.last_name}</td>
                <td><span className={`status-chip status-${sessionRow.status}`}>{sessionRow.status}</span></td>
                <td>{sessionRow.workstation.name}</td>
                <td>{sessionRow.duration_minutes} min</td>
              </tr>
            )}
          />
        </Panel>
      </div>

      <Panel title="Impressions recentes" subtitle="Historique des derniers travaux detectes">
        <DataTable
          columns={["Email", "Utilisateur", "Pages", "Statut", "Poste", "Horodatage"]}
          rows={recentPrintJobs}
          emptyMessage="Aucune impression recente."
          renderRow={(job) => (
            <tr key={`print-${job.id}`}>
              <td>{job.user.email}</td>
              <td>{job.user.first_name} {job.user.last_name}</td>
              <td>{job.pages}</td>
              <td><span className={`status-chip status-${job.status}`}>{job.status}</span></td>
              <td>{job.workstation.name}</td>
              <td>{formatDateTime(job.printed_at)}</td>
            </tr>
          )}
        />
      </Panel>
    </div>
  );
}

function ClientsPage({ clients, onResetPassword, onOpenGrantModal, busyUserId }) {
  const [clientSearch, setClientSearch] = useState("");

  const filteredClients = useMemo(() => {
    return clients.filter((client) => {
      const haystack = `${client.email} ${client.first_name} ${client.last_name}`.toLowerCase();
      return haystack.includes(clientSearch.toLowerCase());
    });
  }, [clients, clientSearch]);

  return (
    <div className="page-grid">
      <Panel
        title="Clients"
        subtitle="Recherche, historique rapide et gestion des mots de passe"
        actions={
          <input
            className="table-filter"
            value={clientSearch}
            onChange={(event) => setClientSearch(event.target.value)}
            placeholder="Rechercher par email ou nom"
          />
        }
      >
        <DataTable
          columns={["Email", "Nom", "Sessions", "Pages", "Bonus jour", "Active", "Derniere session", "Poste", "Actions"]}
          rows={filteredClients}
          emptyMessage="Aucun client trouve."
          renderRow={(client) => (
            <tr key={`client-${client.id}`}>
              <td>{client.email}</td>
              <td>{client.first_name} {client.last_name}</td>
              <td>{client.total_sessions}</td>
              <td>{client.total_pages_printed}</td>
              <td>{client.bonus_pages_today}</td>
              <td>
                <span className={`status-chip ${client.has_active_session ? "status-active" : "status-closed"}`}>
                  {client.has_active_session ? "Oui" : "Non"}
                </span>
              </td>
              <td>{formatDateTime(client.last_session_started_at)}</td>
              <td>{client.last_workstation_name || "-"}</td>
              <td className="actions-cell">
                <button
                  type="button"
                  className="secondary-button table-button"
                  onClick={() => onOpenGrantModal(client)}
                  disabled={busyUserId === client.id}
                >
                  {busyUserId === client.id ? "Traitement..." : "Ajouter des pages"}
                </button>
                <button
                  type="button"
                  className="secondary-button table-button"
                  onClick={() => onResetPassword(client.id)}
                  disabled={busyUserId === client.id}
                >
                  {busyUserId === client.id ? "Traitement..." : "Reset a cesoc"}
                </button>
              </td>
            </tr>
          )}
        />
      </Panel>
    </div>
  );
}

function WorkstationsPage({ workstations, onCreateWorkstation, onToggleWorkstation, busyWorkstationId }) {
  const [name, setName] = useState("");
  const [location, setLocation] = useState("Accueil");

  function handleSubmit(event) {
    event.preventDefault();
    onCreateWorkstation({ name, location, is_active: true });
    setName("");
    setLocation("Accueil");
  }

  return (
    <div className="page-grid">
      <Panel title="Ajouter un poste" subtitle="Chaque ordinateur client pourra ensuite etre lie a un poste fixe">
        <form className="inline-form" onSubmit={handleSubmit}>
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Ex: POSTE-04" required />
          <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Ex: Accueil" required />
          <button className="primary-button" type="submit">Ajouter le poste</button>
        </form>
      </Panel>

      <Panel title="Postes" subtitle="Activation et desactivation des postes disponibles">
        <DataTable
          columns={["Nom", "Emplacement", "Etat", "Action"]}
          rows={workstations}
          emptyMessage="Aucun poste configure."
          renderRow={(workstation) => (
            <tr key={`workstation-${workstation.id}`}>
              <td>{workstation.name}</td>
              <td>{workstation.location}</td>
              <td>
                <span className={`status-chip ${workstation.is_active ? "status-active" : "status-blocked"}`}>
                  {workstation.is_active ? "Actif" : "Inactif"}
                </span>
              </td>
              <td>
                <button
                  type="button"
                  className="secondary-button table-button"
                  onClick={() => onToggleWorkstation(workstation)}
                  disabled={busyWorkstationId === workstation.id}
                >
                  {busyWorkstationId === workstation.id
                    ? "Mise a jour..."
                    : workstation.is_active ? "Desactiver" : "Activer"}
                </button>
              </td>
            </tr>
          )}
        />
      </Panel>
    </div>
  );
}

function ReportsPage({ reports, reportDays, onChangeReportDays }) {
  const exportRows = [
    ["Date", "Connexions", "Sessions actives", "Minutes utilisees", "Travaux d'impression", "Pages imprimees", "Impressions bloquees"],
    ...reports.map((dailyReport) => [
      formatDateForCsv(dailyReport.date),
      dailyReport.total_connections,
      dailyReport.active_sessions,
      dailyReport.total_minutes_used,
      dailyReport.total_print_jobs,
      dailyReport.total_pages_printed,
      dailyReport.blocked_print_jobs,
    ]),
  ];

  return (
    <div className="page-grid">
      <Panel
        title="Rapports journaliers"
        subtitle="Serie recente pour la reddition de comptes"
        actions={
          <div className="panel-actions">
            <select className="table-filter period-filter" value={reportDays} onChange={(event) => onChangeReportDays(Number(event.target.value))}>
              <option value={7}>7 jours</option>
              <option value={14}>14 jours</option>
              <option value={30}>30 jours</option>
              <option value={90}>90 jours</option>
            </select>
            <button
              type="button"
              className="secondary-button"
              onClick={() => downloadCsv(`cesoc-rapports-${reportDays}-jours.csv`, exportRows)}
            >
              Exporter en CSV
            </button>
          </div>
        }
      >
        <DataTable
          columns={["Date", "Connexions", "Actives", "Minutes", "Travaux", "Pages", "Impressions bloquees"]}
          rows={reports}
          emptyMessage="Aucun rapport recent."
          renderRow={(dailyReport) => (
            <tr key={`report-${dailyReport.date}`}>
              <td>{formatDateForCsv(dailyReport.date)}</td>
              <td>{formatMetric(dailyReport.total_connections)}</td>
              <td>{formatMetric(dailyReport.active_sessions)}</td>
              <td>{formatMetric(dailyReport.total_minutes_used)}</td>
              <td>{formatMetric(dailyReport.total_print_jobs)}</td>
              <td>{formatMetric(dailyReport.total_pages_printed)}</td>
              <td>{formatMetric(dailyReport.blocked_print_jobs)}</td>
            </tr>
          )}
        />
      </Panel>
    </div>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState(getInitialPage);
  const [dashboardError, setDashboardError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [reportDays, setReportDays] = useState(7);
  const [busyUserId, setBusyUserId] = useState(null);
  const [busyWorkstationId, setBusyWorkstationId] = useState(null);
  const [grantModalClient, setGrantModalClient] = useState(null);
  const [grantPagesValue, setGrantPagesValue] = useState("5");
  const [grantReasonValue, setGrantReasonValue] = useState("Besoin exceptionnel");
  const [overview, setOverview] = useState(emptyOverview);
  const [clients, setClients] = useState([]);
  const [reports, setReports] = useState([]);
  const [workstations, setWorkstations] = useState([]);

  async function loadOverview(days = reportDays) {
    const safeDays = Number.isInteger(days) ? days : reportDays;
    setLoadingDashboard(true);
    setDashboardError("");

    try {
      const [overviewPayload, clientsPayload, reportsPayload, workstationsPayload] = await Promise.all([
        getAdminOverview(),
        getAdminClients(),
        getDailyReports(safeDays),
        getAdminWorkstations(),
      ]);
      setOverview({
        ...emptyOverview,
        ...(overviewPayload ?? {}),
        report: {
          ...emptyOverview.report,
          ...((overviewPayload ?? {}).report ?? {}),
        },
      });
      setClients(clientsPayload ?? []);
      setReports(reportsPayload ?? []);
      setWorkstations(workstationsPayload ?? []);
    } catch (error) {
      setDashboardError(error.message);
    } finally {
      setLoadingDashboard(false);
    }
  }

  async function handleResetPassword(userId) {
    setDashboardError("");
    setSuccessMessage("");
    setBusyUserId(userId);
    try {
      const payload = await resetClientPassword(userId);
      setSuccessMessage(payload.message);
      await loadOverview();
    } catch (error) {
      setDashboardError(error.message);
    } finally {
      setBusyUserId(null);
    }
  }

  function openGrantModal(client) {
    setGrantModalClient(client);
    setGrantPagesValue("5");
    setGrantReasonValue("Besoin exceptionnel");
  }

  async function handleGrantPagesSubmit(event) {
    event.preventDefault();
    if (!grantModalClient) {
      return;
    }
    const pages = Number.parseInt(grantPagesValue, 10);
    if (Number.isNaN(pages) || pages <= 0) {
      setDashboardError("Veuillez saisir un nombre de pages valide.");
      return;
    }

    setDashboardError("");
    setSuccessMessage("");
    setBusyUserId(grantModalClient.id);
    try {
      const payload = await grantClientPages(grantModalClient.id, pages, grantReasonValue);
      setSuccessMessage(`${payload.message} Quota du jour: ${payload.total_quota_today} pages.`);
      setGrantModalClient(null);
      await loadOverview();
    } catch (error) {
      setDashboardError(error.message);
    } finally {
      setBusyUserId(null);
    }
  }

  async function handleCreateWorkstation(payload) {
    setDashboardError("");
    setSuccessMessage("");
    try {
      const result = await createWorkstation(payload);
      setSuccessMessage(`Poste ${result.name} ajoute.`);
      await loadOverview();
    } catch (error) {
      setDashboardError(error.message);
    }
  }

  async function handleToggleWorkstation(workstation) {
    setDashboardError("");
    setSuccessMessage("");
    setBusyWorkstationId(workstation.id);
    try {
      const result = await updateWorkstation(workstation.id, { is_active: !workstation.is_active });
      setSuccessMessage(`Poste ${result.name} mis a jour.`);
      await loadOverview();
    } catch (error) {
      setDashboardError(error.message);
    } finally {
      setBusyWorkstationId(null);
    }
  }

  useEffect(() => {
    loadOverview(reportDays);
  }, [reportDays]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    params.set("page", activePage);
    const nextUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, "", nextUrl);
  }, [activePage]);

  return (
    <div className="admin-shell">
      <Sidebar activePage={activePage} onSelectPage={setActivePage} />

      <main className="content-shell">
        <header className="content-header">
          <div>
            <p className="eyebrow">CESOC Administration</p>
            <h2>{navItems.find((item) => item.id === activePage)?.label}</h2>
            <p className="section-copy">
              {navItems.find((item) => item.id === activePage)?.description}
            </p>
          </div>
          <button className="primary-button" onClick={() => loadOverview()} disabled={loadingDashboard}>
            {loadingDashboard ? "Actualisation..." : "Actualiser les donnees"}
          </button>
        </header>

        {dashboardError ? <div className="banner error-banner">{dashboardError}</div> : null}
        {successMessage ? <div className="banner success-banner">{successMessage}</div> : null}

        {activePage === "dashboard" ? (
          <DashboardPage overview={overview} loading={loadingDashboard} onRefresh={() => loadOverview()} />
        ) : null}
        {activePage === "clients" ? (
          <ClientsPage
            clients={clients}
            onResetPassword={handleResetPassword}
            onOpenGrantModal={openGrantModal}
            busyUserId={busyUserId}
          />
        ) : null}
        {activePage === "workstations" ? (
          <WorkstationsPage
            workstations={workstations}
            onCreateWorkstation={handleCreateWorkstation}
            onToggleWorkstation={handleToggleWorkstation}
            busyWorkstationId={busyWorkstationId}
          />
        ) : null}
        {activePage === "reports" ? (
          <ReportsPage reports={reports} reportDays={reportDays} onChangeReportDays={setReportDays} />
        ) : null}
      </main>

        {grantModalClient ? (
        <Modal title={`Ajouter des pages a ${grantModalClient.email}`} onClose={() => setGrantModalClient(null)}>
          <form className="modal-form" onSubmit={handleGrantPagesSubmit}>
            <p className="modal-copy">
              Ce bonus s'ajoute uniquement au quota de la journee en cours. Utilise-le pour les besoins exceptionnels.
            </p>
            <label>
              Nombre de pages
              <input
                type="number"
                min="1"
                value={grantPagesValue}
                onChange={(event) => setGrantPagesValue(event.target.value)}
                placeholder="Ex: 5"
                required
              />
            </label>
            <label>
              Raison
              <input
                value={grantReasonValue}
                onChange={(event) => setGrantReasonValue(event.target.value)}
                placeholder="Ex: Besoin exceptionnel"
                required
              />
            </label>
            <div className="grant-preview">
              <span>Client concerne</span>
              <strong>{grantModalClient.first_name} {grantModalClient.last_name}</strong>
              <small>{grantModalClient.email}</small>
            </div>
            <div className="modal-actions">
              <button type="button" className="secondary-button" onClick={() => setGrantModalClient(null)}>
                Annuler
              </button>
              <button type="submit" className="primary-button" disabled={busyUserId === grantModalClient.id}>
                {busyUserId === grantModalClient.id ? "Ajout..." : "Ajouter les pages"}
              </button>
            </div>
          </form>
        </Modal>
      ) : null}
    </div>
  );
}
