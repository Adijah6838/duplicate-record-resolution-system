import { useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [dups, setDups] = useState([]);
  const [quality, setQuality] = useState(null);
  const [msg, setMsg] = useState("");

  const loadQuality = async () => {
    const r = await axios.get(`${API}/quality`);
    setQuality(r.data);
  };

  const upload = async (e) => {
    const form = new FormData();
    form.append("file", e.target.files[0]);
    const r = await axios.post(`${API}/upload`, form);
    setMsg(`Imported ${r.data.imported}`);
    loadQuality();
  };

  const detect = async () => {
    const r = await axios.post(`${API}/detect?threshold=50`);
    setMsg(`Found ${r.data.candidates} candidates`);
    const d = await axios.get(`${API}/duplicates`);
    setDups(d.data);
  };

  const decide = async (id, action) => {
    await axios.post(`${API}/duplicates/${id}/decision?action=${action}`);
    setDups(dups.filter((d) => d.id !== id));
    loadQuality();
  };

  return (
    <div style={{ maxWidth: 900, margin: "20px auto", fontFamily: "sans-serif", padding: 20 }}>
      <h1>Duplicate Record Resolution</h1>
      {quality && <p>Total: {quality.total} | Active: {quality.active} | Merged: {quality.merged} | Missing Email: {quality.missing_email}</p>}
      <p>{msg}</p>
      <input type="file" accept=".csv" onChange={upload} />
      <button onClick={detect} style={{ marginLeft: 10 }}>Detect Duplicates</button>
      <button onClick={loadQuality} style={{ marginLeft: 10 }}>Refresh Quality</button>
      <hr />
      {dups.length === 0 && <p>No pending duplicates. Upload CSV then Detect.</p>}
      {dups.map((d) => (
        <div key={d.id} style={{ border: "1px solid #ccc", padding: 12, marginBottom: 12, borderRadius: 8 }}>
          <b>Score: {d.score}</b> — Name {d.breakdown.name} | Email {d.breakdown.email} | Phone {d.breakdown.phone} | Address {d.breakdown.address} | DOB {d.breakdown.dob}
          <div style={{ display: "flex", gap: 20, marginTop: 8 }}>
            <div><b>A:</b> {d.a.full_name}<br />{d.a.email}<br />{d.a.phone}<br />{d.a.address}</div>
            <div><b>B:</b> {d.b.full_name}<br />{d.b.email}<br />{d.b.phone}<br />{d.b.address}</div>
          </div>
          <button onClick={() => decide(d.id, "approve")} style={{ marginTop: 8, background: "green", color: "white" }}>Approve Merge (Keep A)</button>
          <button onClick={() => decide(d.id, "reject")} style={{ marginLeft: 8, marginTop: 8 }}>Reject - Not Duplicate</button>
        </div>
      ))}
    </div>
  );
}