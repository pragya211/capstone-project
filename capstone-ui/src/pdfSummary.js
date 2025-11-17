import React, { useState } from "react";
import apiClient from "./apiClient";

function PDFSummary() {
  const [file, setFile] = useState(null);
  const [sections, setSections] = useState(null);
  const [summaries, setSummaries] = useState(null);
  const [loadingExtract, setLoadingExtract] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);

  // File select
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setSections(null);
    setSummaries(null);
  };

  // Extract sections
  const handleExtract = async () => {
    if (!file) return alert("Select a PDF first");
    setLoadingExtract(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await apiClient.post("/headings_route", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setSections(res.data.sections);
    } catch (err) {
      console.error("Extraction error:", err);
    }
    setLoadingExtract(false);
  };

  // Summarize sections
  const handleSummarize = async () => {
    if (!sections) return alert("Extract sections first");
    setLoadingSummary(true);

    try {
      const res = await apiClient.post("/summarize", sections);
      setSummaries(res.data.summaries);
    } catch (err) {
      console.error("Summarization error:", err);
    }
    setLoadingSummary(false);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>AI Research Paper Summarizer</h2>

      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button onClick={handleExtract} disabled={loadingExtract}>
        {loadingExtract ? "Extracting..." : "Extract Sections"}
      </button>

      {sections && (
        <div style={{ marginTop: "20px" }}>
          <h3>Extracted Sections</h3>
          <p><strong>Abstract:</strong> {sections.abstract}</p>
          <p><strong>Introduction:</strong> {sections.introduction}</p>
          <p><strong>Main Body:</strong> {sections.main_body}</p>

          <button onClick={handleSummarize} disabled={loadingSummary}>
            {loadingSummary ? "Summarizing..." : "Summarize"}
          </button>
        </div>
      )}

      {summaries && (
        <div style={{ marginTop: "20px" }}>
          <h3>Summaries</h3>
          <p><strong>Abstract:</strong> {summaries.abstract}</p>
          <p><strong>Introduction:</strong> {summaries.introduction}</p>
          <p><strong>Main Body:</strong> {summaries.main_body}</p>
        </div>
      )}
    </div>
  );
}

export default PDFSummary;
