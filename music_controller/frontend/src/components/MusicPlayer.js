import React from "react";
import {
  Grid,
  Typography,
  Card,
  IconButton,
  LinearProgress,
} from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";
import SkipNextIcon from "@mui/icons-material/SkipNext";

const MusicPlayer = ({
  title,
  artist,
  image_url,
  is_playing,
  time,
  duration,
}) => {
  const handlePlayback = async () => {
    const endpoint = is_playing
      ? "/spotify/player/pause"
      : "/spotify/player/play";
    await fetch(endpoint, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    });
  };

  const songProgress = (time / duration) * 100;

  return (
    <Card>
      <Grid container alignItems="center">
        <Grid item xs={4} textAlign="center">
          <img
            src={image_url}
            alt="Album cover"
            style={{ width: "100%", height: "auto" }}
          />
        </Grid>
        <Grid item xs={8} textAlign="center">
          <Typography component="h5" variant="h5">
            {title}
          </Typography>
          <Typography color="textSecondary" variant="subtitle1">
            {artist}
          </Typography>
          <div>
            <IconButton onClick={handlePlayback}>
              {is_playing ? <PauseIcon /> : <PlayArrowIcon />}
            </IconButton>
            <IconButton>
              <SkipNextIcon />
            </IconButton>
          </div>
        </Grid>
      </Grid>
      <LinearProgress variant="determinate" value={songProgress} />
    </Card>
  );
};

export default MusicPlayer;
