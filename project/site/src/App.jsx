import { useState } from "react";

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

  async function submitJob(event) {
    event.preventDefault();

    if (!stepFile) {
      setStatus("Please upload a STEP file first.");
      return;
    }

    const simSpace = buildSimSpace();

    const formData = new FormData();
    formData.append("step_file", stepFile);
    formData.append("sim_space", JSON.stringify(simSpace));

    setStatus("Submitting job...");
    setResult(null);

    try {
      const response = await fetch("/run", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        setStatus("Backend returned an error.");
        setResult(data);
        return;
      }

      setStatus("Job submitted successfully.");
      setResult(data);
    } catch (error) {
      setStatus("Could not connect to backend.");
      setResult({ error: error.message });
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <p className="tag">Infill FEA Tool</p>
        <h1>Batch simulation setup</h1>
        <p>
          Upload one base STEP file, choose multiple infill-density combos, then
          submit the full design space to your Flask simulation route.
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
                      step="1"
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
            Submit Job
          </button>

          {status && <p className="status">{status}</p>}

          <div className="preview">
            <h3>Payload Preview</h3>
            <pre>{JSON.stringify(buildSimSpace(), null, 2)}</pre>
          </div>

          {result && (
            <div className="preview">
              <h3>Backend Response</h3>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </section>
      </form>
    </main>
  );
}

export default App;
