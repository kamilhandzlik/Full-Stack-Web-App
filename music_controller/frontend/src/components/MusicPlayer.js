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
  image_url,
  title,
  artist,
  is_playing,
  time,
  duration,
}) => {
  const songProgress = (time / duration) * 100;

  return (
    <Card
      sx={{
        display: "flex",
        alignItems: "center",
        padding: 2,
        gap: 2,
        maxWidth: 500,
      }}
    >
      <img
        src={image_url}
        alt="Album cover"
        style={{ width: 80, height: 80, borderRadius: 8 }}
      />
      <Grid container direction="column" justifyContent="center" xs={4}>
        <Typography variant="h6" noWrap>
          {title}
        </Typography>
        <Typography variant="subtitle2" color="textSecondary" noWrap>
          {artist}
        </Typography>
        <LinearProgress
          variant="determinate"
          value={songProgress}
          sx={{ height: 5, borderRadius: 2, mt: 1 }}
        />
      </Grid>
      <div>
        <IconButton>
          {is_playing ? <PauseIcon /> : <PlayArrowIcon />}
        </IconButton>
        <IconButton>
          <SkipNextIcon />
        </IconButton>
      </div>
    </Card>
  );
};

export default MusicPlayer;
