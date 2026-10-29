import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  BarChart,
  Bar,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const num = (v) => Math.round(v).toLocaleString("en-GB");

function Card({ label, value, unit }) {
  return (
    <div className="card">
      <div className="label">{label}</div>
      <div className="value">
        {value} <span className="unit">{unit}</span>
      </div>
    </div>
  );
}

export default function App() {
  const [days, setDays] = useState([]);
  const [day, setDay] = useState("");
  const [cutoff, setCutoff] = useState(9);
  const [dayData, setDayData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [horizon, setHorizon] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/meta")
      .then((r) => r.json())
      .then((m) => {
        setDays(m.days);
        setDay(m.days[0]);
        setCutoff(m.default_cutoff);
      })
      .catch(() => setError("Could not load data"));
    fetch("/api/horizon")
      .then((r) => r.json())
      .then(setHorizon);
  }, []);

  useEffect(() => {
    fetch(`/api/metrics?cutoff=${cutoff}`)
      .then((r) => r.json())
      .then(setMetrics);
  }, [cutoff]);

  useEffect(() => {
    if (!day) return;
    fetch(`/api/day?date=${day}&cutoff=${cutoff}`)
      .then((r) => r.json())
      .then(setDayData);
  }, [day, cutoff]);

  if (error) return <main>{error}</main>;
  if (!metrics || !dayData) return <main>Loading...</main>;

  const s = metrics.summary;
  const chartRows = dayData.rows.map((r) => ({
    ...r,
    label: r.time.slice(11, 16),
    band: [r.safe_wind, r.high_wind],
  }));

  return (
    <div>
      <header>
        <h1>UK Wind Generation: Day-Ahead Forecast Portal</h1>
        <p>Elexon WINDFOR forecasts vs FUELHH actuals, delivery days 2-31 January 2026</p>
      </header>
      <main>
        <div className="controls">
          <label>
            Delivery day
            <select value={day} onChange={(e) => setDay(e.target.value)}>
              {days.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </label>
          <label>
            Decision cutoff (UTC, previous day)
            <select value={cutoff} onChange={(e) => setCutoff(Number(e.target.value))}>
              {[6, 7, 8, 9, 10, 11, 12].map((h) => (
                <option key={h} value={h}>{String(h).padStart(2, "0")}:00</option>
              ))}
            </select>
          </label>
        </div>

        <div className="insight">
          For decisions made at {String(cutoff).padStart(2, "0")}:00 the day before, the wind forecast was on
          average <b>{num(Math.abs(s.bias))} MW {s.bias > 0 ? "higher" : "lower"}</b> than what was actually generated.
          In 9 of 10 hours actual wind fell short of the forecast by no more than <b>{num(s.shortfall_p90)} MW</b>,
          so that is a sensible extra amount to plan for from thermal plants.
        </div>

        <div className="cards">
          <Card label="MAE" value={num(s.mae)} unit="MW" />
          <Card label="RMSE" value={num(s.rmse)} unit="MW" />
          <Card label="Bias (forecast - actual)" value={num(s.bias)} unit="MW" />
          <Card label="MAPE" value={s.mape} unit="%" />
          <Card label="MAE / mean actual" value={s.nmae} unit="%" />
          <Card label="P90 abs error" value={num(s.p90)} unit="MW" />
          <Card label="P95 abs error" value={num(s.p95)} unit="MW" />
        </div>

        <div className="panel">
          <h2>Forecast available at decision time vs actual, {dayData.day}</h2>
          <p className="note">
            Uses the latest forecast published before {dayData.cutoff.replace("T", " ").slice(0, 16)} UTC
            (published {dayData.publish_times.map((p) => p.replace("T", " ").slice(5, 16)).join(", ")}).
            Shaded band: likely range of actual wind (forecast adjusted by the 10th and 90th percentile of January errors).
          </p>
          <ResponsiveContainer width="100%" height={340}>
            <ComposedChart data={chartRows}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis tickFormatter={num} />
              <Tooltip formatter={(v) => (Array.isArray(v) ? v.map(num).join(" - ") : num(v))} />
              <Legend />
              <Area dataKey="band" name="Error band (MW)" fill="#9ec5e0" stroke="none" fillOpacity={0.5} />
              <Line dataKey="forecast" name="Forecast (MW)" stroke="#0b3d5c" strokeWidth={2} dot={false} />
              <Line dataKey="actual" name="Actual (MW)" stroke="#e67e22" strokeWidth={2} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="grid">
          <div className="panel">
            <h2>Mean absolute error by hour of day</h2>
            <p className="note">Averaged over all January delivery days.</p>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={metrics.by_hour}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis tickFormatter={num} />
                <Tooltip formatter={num} />
                <Bar dataKey="mae" name="MAE (MW)" fill="#0b3d5c" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="panel">
            <h2>Mean absolute error by forecast horizon</h2>
            <p className="note">Hours between publish time and target time, all published forecasts.</p>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={horizon}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis tickFormatter={num} />
                <Tooltip formatter={num} />
                <Bar dataKey="mae" name="MAE (MW)" fill="#e67e22" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <h2>Daily mean absolute error</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={metrics.by_day}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" tickFormatter={(d) => d.slice(8)} />
              <YAxis tickFormatter={num} />
              <Tooltip formatter={num} />
              <Bar dataKey="mae" name="MAE (MW)" fill="#2e86c1" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </main>
    </div>
  );
}
