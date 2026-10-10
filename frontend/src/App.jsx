import { useEffect, useMemo, useState } from "react";
import "./App.css";
const WATERLOOP_API =
  "https://lokcenk6zbx2jb2hupqcgzp5vy0eyagu.lambda-url.eu-north-1.on.aws/";

const INITIAL_DEMANDS = [
  {
    id: "toilet",
    name: "Toilet flushing",
    category: "SANITATION",
    icon: "↗",
    demand: 80000,
    priority: 3,
    description: "Non-potable demand across facility restrooms",
    color: "blue",
  },
  {
    id: "landscape",
    name: "Landscaping",
    category: "GREEN SPACES",
    icon: "❋",
    demand: 100000,
    priority: 2,
    description: "Irrigation for lawns and landscaped areas",
    color: "green",
  },
  {
    id: "vehicle",
    name: "Vehicle washing",
    category: "OPERATIONS",
    icon: "◉",
    demand: 70000,
    priority: 1,
    description: "Exterior washing for facility vehicles",
    color: "orange",
  },
];

const INITIAL_QUALITY = {
  turbidity: "1.4",
  ph: "7.2",
};

const formatLitres = (value) =>
  `${new Intl.NumberFormat("en-IN").format(Math.round(value))} L`;

const formatCompact = (value) => {
  if (value >= 100000) {
    return `${(value / 100000).toFixed(value % 100000 === 0 ? 0 : 1)} lakh`;
  }
  return new Intl.NumberFormat("en-IN").format(Math.round(value));
};

function assessQuality(quality) {
  const turbidity = Number(quality.turbidity);
  const ph = Number(quality.ph);

  if (
    quality.turbidity.trim() === "" ||
    quality.ph.trim() === "" ||
    !Number.isFinite(turbidity) ||
    !Number.isFinite(ph)
  ) {
    return {
      status: "INSUFFICIENT DATA",
      message: "Enter valid turbidity and pH measurements.",
      eligible: false,
    };
  }

  if (turbidity < 0 || ph < 0 || ph > 14) {
    return {
      status: "INVALID INPUT",
      message: "Enter physically valid measurement values.",
      eligible: false,
    };
  }

  if (turbidity >= 2 || ph < 6.5 || ph > 8.5) {
    return {
      status: "NOT COMPATIBLE",
      message:
        "At least one configured toilet-flushing quality check is not met.",
      eligible: false,
    };
  }

  return {
    status: "CONDITIONAL",
    message:
      "Two prototype checks pass. Other applicable quality parameters and treatment requirements still need verification.",
    eligible: true,
  };
}

function allocateWater(supply, demands, qualityEligible) {
  let remaining = supply;

  return [...demands]
    .sort((a, b) => b.priority - a.priority)
    .map((item) => {
      if (!qualityEligible) {
        return {
          ...item,
          allocated: 0,
          status: "HELD",
        };
      }

      const allocated = Math.min(item.demand, remaining);
      remaining -= allocated;

      let status = "UNALLOCATED";
      if (allocated === item.demand) status = "FULL";
      else if (allocated > 0) status = "PARTIAL";

      return { ...item, allocated, status };
    })
    .sort(
      (a, b) =>
        INITIAL_DEMANDS.findIndex((item) => item.id === a.id) -
        INITIAL_DEMANDS.findIndex((item) => item.id === b.id)
    );
}

function StatCard({ label, value, note, icon }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        <span className="stat-icon">{icon}</span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-note">{note}</div>
    </article>
  );
}

function App() {
  const [supply, setSupply] = useState(500000);
  const [costPer1000, setCostPer1000] = useState(50);
  const [quality, setQuality] = useState(INITIAL_QUALITY);
  const [awsResult, setAwsResult] = useState(null);
  const [awsLoading, setAwsLoading] = useState(false);
  const [awsError, setAwsError] = useState("");

  useEffect(() => {
  const controller = new AbortController();

  async function fetchAllocation() {
    setAwsLoading(true);
    setAwsError("");

    try {
      const response = await fetch(WATERLOOP_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          available_litres: supply,
          freshwater_cost_per_1000_litres: costPer1000,
          demands: INITIAL_DEMANDS.map((item) => ({
            name: item.name,
            demand_litres: item.demand,
            priority: item.priority,
          })),
        }),
        signal: controller.signal,
      });

      const result = await response.json();

      if (!response.ok || result.success === false) {
        throw new Error(result.error || "AWS allocation request failed.");
      }

      setAwsResult(result);
    } catch (error) {
      if (error.name !== "AbortError") {
        setAwsError(error.message || "Unable to reach AWS.");
      }
    } finally {
      if (!controller.signal.aborted) {
        setAwsLoading(false);
      }
    }
  }

  fetchAllocation();

  return () => controller.abort();
}, [supply, costPer1000]);


  const qualityAssessment = useMemo(
    () => assessQuality(quality),
    [quality]
  );

const allocations = useMemo(() => {
  // Never display an allocation when the prototype quality gate fails.
  if (!qualityAssessment.eligible) {
    return INITIAL_DEMANDS.map((item) => ({
      ...item,
      allocated: 0,
      status: "HELD",
    }));
  }

  const awsAllocations = awsResult?.allocations;

  if (Array.isArray(awsAllocations)) {
    return INITIAL_DEMANDS.map((item) => {
      const result = awsAllocations.find(
        (allocation) => allocation.name === item.name
      );

      return {
        ...item,
        allocated: result?.allocated_litres ?? 0,
        status: result?.status ?? "UNALLOCATED",
      };
    });
  }

  return allocateWater(
    supply,
    INITIAL_DEMANDS,
    qualityAssessment.eligible
  );
}, [awsResult, supply, qualityAssessment.eligible]);

  const totalDemand = INITIAL_DEMANDS.reduce(
    (total, item) => total + item.demand,
    0
  );

  const totalAllocated = allocations.reduce(
    (total, item) => total + item.allocated,
    0
  );

  const remainingSupply = supply - totalAllocated;
  const estimatedSavings = (totalAllocated / 1000) * costPer1000;
  const allocationPercent =
    supply > 0 ? Math.min(100, (totalAllocated / supply) * 100) : 0;

  const changeQuality = (field, value) => {
    setQuality((previous) => ({ ...previous, [field]: value }));
  };

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" aria-label="WATERLOOP home">
          <span className="brand-mark">W</span>
          <span>
            <strong>waterloop</strong>
            <small>RESOURCE INTELLIGENCE</small>
          </span>
        </a>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="navigation" aria-label="Main navigation">
          <a className="nav-item active" href="#overview">
            <span>◫</span> Decision overview
          </a>
          <a className="nav-item" href="#quality">
            <span>◇</span> Quality checks
          </a>
          <a className="nav-item" href="#allocation">
            <span>⇄</span> Allocation plan
          </a>
          <a className="nav-item" href="#impact">
            <span>↗</span> Impact estimate
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="demo-tag">
            <span className="live-dot" />
            PROTOTYPE MODE
          </div>
          <p>Decision support for a more circular water future.</p>
          <div className="sidebar-footer">BUILT FOR ENVIRONMENTAL HACKS</div>
        </div>
      </aside>

      <section className="main-content" id="overview">
        <header className="topbar">
          <div className="breadcrumbs">
            Workspace <span>/</span> Water planning
          </div>
          <div className="topbar-right">
            <span className="demo-badge">DEMO SCENARIO</span>
            <div className="avatar">EO</div>
            <span className="workspace-name">EarthOps</span>
          </div>
        </header>

        <div className="page-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-line" />
                WATER REUSE DECISION ENGINE
              </div>
              <h1>Make every litre count.</h1>
              <p className="page-subtitle">
                Turn available treated water into an explainable allocation
                plan for non-potable uses.
              </p>
            </div>
            <div className="location-pill">
              <span>⌖</span>
              Metro Industrial Park
              <span className="location-demo">DEMO</span>
            </div>
          </section>

          <div className="notice">
            <span className="notice-icon">ⓘ</span>
            <p>
              <strong>Representative scenario.</strong> Supply, demand and
              financial figures are illustrative—not live facility data.
            </p>
          </div>

          <div
  role="status"
  style={{
    margin: "12px 0",
    padding: "10px 14px",
    borderRadius: "10px",
    background: awsError
      ? "#fff1f0"
      : awsLoading
        ? "#fff8e6"
        : "#eaf8ef",
    color: awsError
      ? "#a61b1b"
      : awsLoading
        ? "#795500"
        : "#176b38",
    fontSize: "13px",
  }}
>
  {awsError
    ? `AWS connection issue: ${awsError}`
    : awsLoading
      ? "Connecting to the WATERLOOP AWS planner…"
      : awsResult
        ? "AWS planner connected · Allocation returned by Lambda"
        : "Preparing AWS planner…"}
</div>

          <section className="stats-grid" aria-label="Water summary">
            <StatCard
              label="TREATED WATER AVAILABLE"
              value={formatCompact(supply)}
              note="Litres per day"
              icon="≈"
            />
            <StatCard
              label="REUSE ALLOCATED"
              value={formatCompact(totalAllocated)}
              note={`${totalDemand > 0 ? Math.round((totalAllocated / totalDemand) * 100) : 0}% of listed demand`}
              icon="↗"
            />
            <StatCard
              label="SUPPLY UNALLOCATED"
              value={formatCompact(remainingSupply)}
              note="Remaining in this scenario"
              icon="◌"
            />
            <StatCard
              label="ESTIMATED GROSS SAVINGS"
              value={`₹${new Intl.NumberFormat("en-IN", {
                maximumFractionDigits: 0,
              }).format(estimatedSavings)}`}
              note="Per day · illustrative assumption"
              icon="₹"
            />
          </section>

          <section className="planner-grid">
            <article className="panel supply-panel">
              <div className="panel-heading">
                <div>
                  <div className="section-kicker">01 / AVAILABLE RESOURCE</div>
                  <h2>Water supply</h2>
                </div>
                <span className="heading-icon water-icon">≈</span>
              </div>

              <p className="panel-description">
                How much treated wastewater is available today?
              </p>

              <div className="supply-number">
                <strong>{formatLitres(supply)}</strong>
                <span>/ day</span>
              </div>

              <input
                className="range-input"
                type="range"
                min="0"
                max="600000"
                step="10000"
                value={supply}
                onChange={(event) => setSupply(Number(event.target.value))}
                aria-label="Available treated water in litres per day"
              />

              <div className="range-labels">
                <span>0 L</span>
                <span>600,000 L</span>
              </div>

              <div className="scenario-buttons">
                <button
                  className={supply === 500000 ? "scenario-active" : ""}
                  onClick={() => setSupply(500000)}
                >
                  Normal supply
                </button>
                <button
                  className={supply === 150000 ? "scenario-active" : ""}
                  onClick={() => setSupply(150000)}
                >
                  Shortage scenario
                </button>
              </div>

              <div className="supply-footnote">
                <span className="footnote-icon">↻</span>
                Allocation recalculates as you adjust supply.
              </div>
            </article>

            <article className="panel quality-panel" id="quality">
              <div className="panel-heading">
                <div>
                  <div className="section-kicker">02 / QUALITY GATE</div>
                  <h2>Check compatibility</h2>
                </div>
                <span className="heading-icon quality-icon">◇</span>
              </div>

              <p className="panel-description">
                Prototype checks for the toilet-flushing use case.
              </p>

              <div className="quality-fields">
                <label>
                  <span>Turbidity</span>
                  <span className="field-unit">NTU</span>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={quality.turbidity}
                    onChange={(event) =>
                      changeQuality("turbidity", event.target.value)
                    }
                  />
                  <small>Configured check: &lt; 2 NTU</small>
                </label>

                <label>
                  <span>pH</span>
                  <span className="field-unit">pH scale</span>
                  <input
                    type="number"
                    min="0"
                    max="14"
                    step="0.1"
                    value={quality.ph}
                    onChange={(event) =>
                      changeQuality("ph", event.target.value)
                    }
                  />
                  <small>Configured range: 6.5–8.5</small>
                </label>
              </div>

              <div
                className={`quality-result ${
                  qualityAssessment.eligible ? "result-conditional" : "result-held"
                }`}
              >
                <span className="result-symbol">
                  {qualityAssessment.eligible ? "!" : "×"}
                </span>
                <div>
                  <strong>{qualityAssessment.status}</strong>
                  <p>{qualityAssessment.message}</p>
                </div>
              </div>

              <p className="quality-disclaimer">
                This prototype checks only two parameters. It does not certify
                water safety or replace applicable standards, treatment
                verification, or expert approval.
              </p>
            </article>
          </section>

          <section className="panel allocation-panel" id="allocation">
            <div className="allocation-heading">
              <div>
                <div className="section-kicker">03 / RECOMMENDED DISTRIBUTION</div>
                <h2>Allocation plan</h2>
                <p className="panel-description">
                  A priority-ordered allocation of the available supply.
                </p>
              </div>
              <div className="demand-summary">
                <span>TOTAL LISTED DEMAND</span>
                <strong>{formatLitres(totalDemand)}</strong>
              </div>
            </div>

            <div className="allocation-meter">
              <div
                className="allocation-meter-fill"
                style={{ width: `${allocationPercent}%` }}
              />
            </div>
            <div className="meter-caption">
              <span>{formatLitres(totalAllocated)} allocated</span>
              <span>{formatLitres(supply)} available</span>
            </div>

            <div className="allocation-table-wrap">
              <table className="allocation-table">
                <thead>
                  <tr>
                    <th>NON-POTABLE USE</th>
                    <th>DAILY DEMAND</th>
                    <th>ALLOCATION</th>
                    <th>FULFILMENT</th>
                    <th>STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {allocations.map((item) => {
                    const percent =
                      item.demand > 0
                        ? (item.allocated / item.demand) * 100
                        : 0;

                    return (
                      <tr key={item.id}>
                        <td>
                          <div className="use-name">
                            <span className={`use-icon ${item.color}`}>
                              {item.icon}
                            </span>
                            <span>
                              <strong>{item.name}</strong>
                              <small>{item.category}</small>
                            </span>
                          </div>
                        </td>
                        <td>{formatLitres(item.demand)}</td>
                        <td>
                          <strong>{formatLitres(item.allocated)}</strong>
                        </td>
                        <td>
                          <div className="fulfilment">
                            <div className="fulfilment-track">
                              <div
                                className="fulfilment-fill"
                                style={{ width: `${percent}%` }}
                              />
                            </div>
                            <span>{Math.round(percent)}%</span>
                          </div>
                        </td>
                        <td>
                          <span
                            className={`status-badge status-${item.status.toLowerCase()}`}
                          >
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="allocation-note">
              <span>ⓘ</span>
              <p>
                <strong>Decision logic:</strong> eligible uses are considered
                in configured priority order. This prototype does not yet
                optimize distance, conveyance costs, or treatment costs.
              </p>
            </div>
          </section>

          <section className="impact-grid" id="impact">
            <article className="panel impact-panel">
              <div className="section-kicker">04 / RESOURCE IMPACT</div>
              <h2>What could this plan change?</h2>
              <p className="panel-description">
                Illustrative estimates based on the current allocation.
              </p>

              <div className="impact-metrics">
                <div>
                  <span className="impact-icon">↘</span>
                  <span>
                    <small>Potential freshwater displacement</small>
                    <strong>{formatLitres(totalAllocated)} / day</strong>
                  </span>
                </div>
                <div>
                  <span className="impact-icon money-icon">₹</span>
                  <span>
                    <small>Assumed freshwater cost / 1,000 L</small>
                    <strong>₹{costPer1000}</strong>
                  </span>
                </div>
              </div>

              <label className="cost-control">
                <span>Adjust illustrative freshwater cost</span>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={costPer1000}
                  onChange={(event) =>
                    setCostPer1000(Number(event.target.value))
                  }
                  aria-label="Illustrative freshwater cost per 1000 litres"
                />
                <span>₹10 <span>₹100</span></span>
              </label>
            </article>

            <article className="impact-callout">
              <div className="callout-orbit orbit-one" />
              <div className="callout-orbit orbit-two" />
              <div className="callout-content">
                <span className="callout-label">ESTIMATED GROSS SAVINGS</span>
                <div className="callout-value">
                  ₹{new Intl.NumberFormat("en-IN", {
                    maximumFractionDigits: 0,
                  }).format(estimatedSavings)}
                  <span>/ day</span>
                </div>
                <p>
                  Based on allocated reuse × assumed freshwater price.
                </p>
                <div className="callout-divider" />
                <div className="callout-total">
                  <span>Illustrative 30-day equivalent</span>
                  <strong>
                    ₹{new Intl.NumberFormat("en-IN", {
                      maximumFractionDigits: 0,
                    }).format(estimatedSavings * 30)}
                  </strong>
                </div>
                <small className="callout-disclaimer">
                  Gross estimate only. Treatment, pumping, conveyance, and
                  actual tariffs are not included.
                </small>
              </div>
            </article>
          </section>

          <footer className="page-footer">
            <span>
              <span className="footer-mark">W</span> WATERLOOP
            </span>
            <span>Decision support, not a water-safety certification.</span>
            <span>EARTHOPS · ENVIRONMENTAL HACKS 2026</span>
          </footer>
        </div>
      </section>
    </main>
  );
}

export default App;