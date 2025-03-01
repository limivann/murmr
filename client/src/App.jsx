import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import { Tabs } from "./components/Tabs";

function App() {
  return (
    <div className="bg-gray-50 flex flex-col items-center p-2 rounded-4xl overflow-visible">
      <header className="text-center mb-4">
        <h1 className="text-2xl font-extrabold text-gray-800">murmr</h1>
        <p className="text-lg text-gray-600 mt-1">
          Intelligent Wellness, Spoken For You
        </p>
      </header>

      <main className="w-full max-w-4xl bg-white p-6 rounded-4xl shadow-lg relative -mt-3">
        <Tabs />
      </main>
    </div>
  );
}

export default App;
