import AudioPlayer from "react-h5-audio-player";
import "react-h5-audio-player/lib/styles.css";
import exampleAudio from "../assets/example.mp3";
import { useRef, useEffect } from "react";

const Player = ({ currentSrc, onClickNext, onClickPrevious }) => {
  return (
    <AudioPlayer
      autoPlay
      src={currentSrc}
      onPlay={(e) => console.log("onPlay")}
      onClickNext={(e) => onClickNext()}
      onClickPrevious={(e) => onClickPrevious()}
      customAdditionalControls={[]}
      showSkipControls={true}
      showJumpControls={false}
      // other props here
    />
  );
};

export default Player;
