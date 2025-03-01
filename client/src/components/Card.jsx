import React from "react";
import temp from "../assets/img1.jpg";

const Card = ({ text, audio, image, onClick, isActive }) => {
  return (
    <div
      className={`flex items-center gap-4 m-4 cursor-pointer rounded-lg shadow-lg border-0 p-2 
        ${
          isActive
            ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white"
            : "bg-gray-400 text-gray-800"
        }`}
      onClick={onClick}
    >
      <img
        src={image}
        className="w-8 h-8 object-cover rounded-full"
        alt={text}
      />
      <p className="font-bold text-white text-sm">{text}</p>
    </div>
  );
};

export default Card;
