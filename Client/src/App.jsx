import React, { useState } from "react";
import './App.css'

const App = () => {
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setloading] = useState(false)
  const [searchText, setSearchText] = useState("");

  const handleFileChange = (e) => {
    setPdfFile(e.target.files[0]);
  };

  const handleSearchChange = (e) => {
    setSearchText(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!pdfFile || !searchText) {
      alert("Please upload a PDF file and enter a search term.");
      return;
    }
    setloading(true)
    const formData = new FormData();
    formData.append("pdf", pdfFile);
    formData.append("search_text", searchText);
    const fileName = pdfFile.name.slice(0, -4)
    try {
      const response = await fetch("http://127.0.0.1:5000/highlight", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Error in fetching highlighted PDF.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${fileName}_highlighted.pdf`;
      link.click();
      window.URL.revokeObjectURL(url); // Clean up
    } catch (error) {
      alert("An error occurred while downloading the file.");
      console.error("Error:", error);
    } finally {
      setloading(false)
    }
  };

  return (
    <div>
      <h1>PDF Text Highlighter</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <textarea type="text" placeholder="Enter text to highlight" value={searchText} onChange={handleSearchChange} />
        <button type="submit">Highlight & Download</button>
      </form>
      {
        loading && <div className="loaderContainer">
          <div className="loader"></div>

        </div>
      }


    </div>
  );
};

export default App;

