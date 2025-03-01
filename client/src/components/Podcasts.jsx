import { useState, useRef, useEffect } from "react";
import Card from "./Card";
import Player from "./Player";
import podcastImg from "../assets/img1.jpg";
import podcastImg2 from "../assets/img2.jpg";
import podcastImg3 from "../assets/img3.jpg";
import examplePodcast from "../assets/example.mp3";
import examplePodcast2 from "../assets/example2.mp3";

const samplePodcasts = [
  {
    id: 1,
    title: "Mind & Motion",
    summary: "Boost your mental agility",
    src: examplePodcast,
    image: podcastImg,
  },
  {
    id: 2,
    title: "Personalized Learning",
    summary: "Adaptive learning strategies",
    src: examplePodcast2,
    image: podcastImg2,
  },
];

export default function PodcastPlayer() {
  const [currentPodcast, setCurrentPodcast] = useState(samplePodcasts[0]);
  const [podcasts, setPodCasts] = useState(samplePodcasts);

  useEffect(() => {
    // Fetch podcasts from an API
    const openingPodcast = {
      id: 1,
      title: "Daily Check-in",
      src: "/podcasts/combined_challenges.mp3",
      image: podcastImg,
    };

    const newsPodcast = {
      id: 2,
      title: "Your Health, Your News",
      src: "/podcasts/combined_news.mp3",
      image: podcastImg2,
    };

    const therapyPodcast = {
      id: 3,
      title: "Your Therapy Guide",
      src: "/podcasts/combined_therapy.mp3",
      image: podcastImg3,
    };

    setCurrentPodcast(openingPodcast);
    setPodCasts([openingPodcast, newsPodcast, therapyPodcast]);

    // setPodCasts(data);
    console.log("currentPodcast", currentPodcast);
  }, []);

  const handleClickNext = (currentId) => {
    const nextPodcast = podcasts.find(
      (podcast) => podcast.id === currentId + 1
    );
    if (nextPodcast) {
      setCurrentPodcast(nextPodcast);
    }
  };

  const handleClickPrevious = (currentId) => {
    const previousPodcast = podcasts.find(
      (podcast) => podcast.id === currentId - 1
    );
    if (previousPodcast) {
      setCurrentPodcast(previousPodcast);
    }
  };

  return (
    <>
      <div>
        {podcasts.map((podcast) => (
          <Card
            key={podcast.id}
            text={podcast.title}
            audio={podcast.src}
            image={podcast.image}
            onClick={() => setCurrentPodcast(podcast)}
            isActive={currentPodcast.id === podcast.id}
          />
        ))}
      </div>
      {currentPodcast && (
        <Player
          currentSrc={currentPodcast.src}
          key={currentPodcast.id}
          onClickNext={() => handleClickNext(currentPodcast.id)}
          onClickPrevious={() => handleClickPrevious(currentPodcast.id)}
        />
      )}
    </>
  );
}
