import { useEffect, useState } from "react";

const INFILLS = [
  { label: "Grid", value: "grid" },
  { label: "Honeycomb", value: "honey" },
  { label: "Finray", value: "finr" },
  { label: "Triangle", value: "tri" },
];

function App() {
  const [stepFile, setStepFile] = useState(null);
  const [meshSize, setMeshSize] = useState(1.0);
  const [outThickness, setOutThickness] = useState(0.87);
  const [infThickness, setInfThickness] = useState(0.45);

  const [rows, setRows] = useState([{ infill: "grid", density: 20 }]);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);
  const [previousJobs, setPreviousJobs] = useState([]);

  useEffect(() => {
    loadPreviousJobs();
  }, []);

  async function loadPreviousJobs() {
    const response = await fetch("/jobs");
    const data = await response.json();
    setPreviousJobs(data.jobs || []);
  }

  function addRow() {
    setRows([...rows, { infill: "grid", density: 20 }]);
  }

  function updateRow(index, key, value) {
    const newRows = [...rows];
    newRows[index][key] = value;
    setRows(newRows);
  }

  function removeRow(index) {
    if (rows.length === 1) return;
    setRows(rows.filter((_, i) => i !== index));
  }

  function buildSimSpace() {
    const infills = {
      grid: [],
      honey: [],
      finr: [],
      tri: [],
    };

    rows.forEach((row) => {
      infills[row.infill].push(Number(row.density));
    });

    return {
      infills,
      mesh_size: Number(meshSize),
      out_thickness: Number(outThickness),
      inf_thickness: Number(infThickness),
    };
  }

  function getStepUrl(jobName, designName) {
    const stepName = designName.replace("-", "") + ".step";
    return `/jobs/${jobName}/infills/${stepName}`;
  }

  async function submitJob(event) {
    event.preventDefault();

    if (!stepFile) {
      setStatus("Please upload a STEP file first.");
      return;
    }

    const formData = new FormData();
    formData.append("step_file", stepFile);
    formData.append("sim_space", JSON.stringify(buildSimSpace()));

    setStatus("Running simulation...");
    setResult(null);

    try {
      const response = await fetch("/run", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log(data);
      if (!response.ok || data.status !== "complete") {
        setStatus("Simulation failed.");
        setResult(data);
        return;
      }

      setStatus("Simulation complete.");
      setResult(data);
      loadPreviousJobs();
    } catch (error) {
      setStatus("Could not connect to backend.");
      setResult({ error: error.message });
    }
  }

  function RankingTable({ jobName, metrics }) {
    if (!metrics) {
      return <p>No saved metrics for this job.</p>;
    }

    return (
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Design</th>
            <th>Pseudo CGS</th>
            <th>Displacement</th>
            <th>Stress</th>
            <th>STEP</th>
          </tr>
        </thead>

        <tbody>
          {metrics.map((row, index) => (
            <tr key={`${jobName}-${index}`}>
              <td>#{index + 1}</td>
              <td>{row[0]}</td>
              <td>{Number(row[1]).toFixed(4)}</td>
              <td>{Number(row[2]).toFixed(4)}</td>
              <td>{Number(row[3]).toFixed(4)}</td>
              <td>
                <a href={getStepUrl(jobName, row[0])} target="_blank">
                  View STEP
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }

  return (
    <main className="page">
      <section className="hero">
        <p className="tag">Infill FEA Tool</p>
        <h1>Batch simulation setup</h1>
        <p>
          Upload one STEP file, test multiple infill-density combinations, and
          view current or previous job rankings.
        </p>
      </section>

      <form className="panel" onSubmit={submitJob}>
        <section className="card">
          <h2>Base Part</h2>

          <label className="uploadBox">
            <input
              type="file"
              accept=".step,.stp"
              onChange={(e) => setStepFile(e.target.files[0])}
            />
            <span>{stepFile ? stepFile.name : "Choose base_part.step"}</span>
          </label>
        </section>

        <section className="card">
          <div className="cardHeader">
            <h2>Design Space</h2>
            <button type="button" className="secondaryBtn" onClick={addRow}>
              + Add Entry
            </button>
          </div>

          <table>
            <thead>
              <tr>
                <th>Infill</th>
                <th>Density</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  <td>
                    <select
                      value={row.infill}
                      onChange={(e) =>
                        updateRow(index, "infill", e.target.value)
                      }
                    >
                      {INFILLS.map((infill) => (
                        <option key={infill.value} value={infill.value}>
                          {infill.label}
                        </option>
                      ))}
                    </select>
                  </td>

                  <td>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.01"
                      value={row.density}
                      onChange={(e) =>
                        updateRow(index, "density", e.target.value)
                      }
                    />
                  </td>

                  <td>
                    <button
                      type="button"
                      className="deleteBtn"
                      onClick={() => removeRow(index)}
                      disabled={rows.length === 1}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="card">
          <h2>Global Simulation Settings</h2>

          <div className="settingsGrid">
            <label>
              Mesh Size
              <input
                type="number"
                step="0.01"
                value={meshSize}
                onChange={(e) => setMeshSize(e.target.value)}
              />
            </label>

            <label>
              Outline Thickness
              <input
                type="number"
                step="0.01"
                value={outThickness}
                onChange={(e) => setOutThickness(e.target.value)}
              />
            </label>

            <label>
              Infill Thickness
              <input
                type="number"
                step="0.01"
                value={infThickness}
                onChange={(e) => setInfThickness(e.target.value)}
              />
            </label>
          </div>
        </section>

        <section className="card submitCard">
          <button type="submit" className="primaryBtn">
            Run Job
          </button>

          {status && <p className="status">{status}</p>}
        </section>
      </form>

      {result?.metrics && (
        <section className="resultsCard">
          <h2>Current Job Ranking</h2>
          <RankingTable jobName={result.job} metrics={result.metrics} />
        </section>
      )}

      <section className="resultsCard">
        <div className="cardHeader">
          <h2>Previous Jobs</h2>
          <button
            type="button"
            className="secondaryBtn"
            onClick={loadPreviousJobs}
          >
            Refresh
          </button>
        </div>

        {previousJobs.length === 0 ? (
          <p>No previous jobs found.</p>
        ) : (
          previousJobs.map((job) => (
            <details key={job.job} className="jobDetails">
              <summary>{job.job}</summary>
              <RankingTable jobName={job.job} metrics={job.metrics} />
            </details>
          ))
        )}
      </section>
    </main>
  );
}

export default App;
