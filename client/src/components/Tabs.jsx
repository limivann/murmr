import React, { useState } from "react";
import PodcastPlayer from "./Podcasts";
import axios from "axios";

export const Tabs = () => {
  const [activeTab, setActiveTab] = useState("Input");
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("English");
  const [mood, setMood] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");
  const [feelingValue, setFeelingValue] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const api = axios.create({
    baseURL: "http://localhost:8000",
  });

  const handleGenerate = async () => {
    console.log("Generating podcast...");
    try {
      setIsGenerating(true);
      const response = await api.post("/generate", {
        mood,
        user_prompt: feelingValue,
      });
      if (response.data.success) {
        setIsGenerating(false);
        // switch to podcast tab
        setActiveTab("Podcast");
        //
      }
      setIsGenerating(false);
    } catch (error) {
      console.error("Error generating podcast:", error);
    }
  };

  const handleUpload = async (e) => {
    console.log(e);
    const file = e.target.files[0];
    setFile(file);

    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    console.log("uploading file");

    try {
      const response = await api.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log(response.data);

      // const result = await response.json();
      // setUploadStatus(result.message);
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadStatus("Upload failed.");
    }
  };

  return (
    <div className="max-w-4xl min-w-[550px] mx-auto shadow-lg p-4">
      {/* Tab Navigation */}
      <div className="flex mb-4">
        {["Input", "Podcast"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 p-2 text-center rounded-md transition-colors duration-300 ${
              activeTab === tab
                ? "bg-blue-500 text-white font-bold"
                : "bg-gray-100 hover:bg-blue-100 text-gray-800"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "Input" && (
        <div className="p-2">
          {/* Custom File Input */}
          <div className="mb-4">
            <label className="block mb-2 text-left">1. Upload your data</label>
            <label className="flex items-center justify-center border-2 border-dashed border-gray-300 p-4 rounded-md cursor-pointer bg-gray-100 hover:bg-gray-50 transition-colors">
              {file ? (
                <span className="text-gray-700">{file.name}</span>
              ) : (
                <span className="text-gray-500">Click to select a file</span>
              )}
              <input
                type="file"
                onChange={(e) => handleUpload(e)}
                className="hidden"
              />
            </label>
          </div>

          {/* Textarea for feeling */}
          <div className="mb-4">
            <label className="block mb-2 text-left">
              2. How are you feeling today?
            </label>
            <textarea
              className="border p-2 rounded w-full"
              placeholder="Write here..."
              onChange={(e) => setFeelingValue(e.target.value)}
              value={feelingValue}
            />
          </div>

          {/* Mood and Language Selection */}
          <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex-1">
              <label className="block mb-2 text-left">3. Mood:</label>
              <div className="flex space-x-4">
                {["😞", "😐", "😊"].map((emoji) => (
                  <button
                    key={emoji}
                    onClick={() => setMood(emoji)}
                    className={`p-2 text-2xl transition-transform duration-200 rounded-full ${
                      mood === emoji
                        ? "border-2 border-blue-500 transform scale-110"
                        : "hover:scale-105"
                    }`}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex-1">
              <label className="block mb-2 text-left">4. Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="border p-2 rounded-xl w-full bg-gray-100"
              >
                <option value="English">English</option>
                <option value="Mandarin">Mandarin</option>
              </select>
            </div>
          </div>

          {/* Centered Inline Aesthetic Upload Button */}
          <div className="flex justify-center mt-6">
            <button
              className="w-30 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center gap-2 shadow-2xl hover:scale-105 transform transition-transform duration-300"
              onClick={handleGenerate}
            >
              {/* Upload Icon */}
              {!isGenerating && (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  className="w-6 h-6 fill-white"
                >
                  <path d="M5 17h14v2H5zm7-12l-5 5h3v4h4v-4h3z" />
                </svg>
              )}
              {/* Upload Text */}
              <span className="text-white font-bold uppercase tracking-wide">
                {isGenerating ? "Loading" : "Upload"}
              </span>
            </button>
          </div>
        </div>
      )}

      {activeTab === "Podcast" && <PodcastPlayer />}
    </div>
  );
};
