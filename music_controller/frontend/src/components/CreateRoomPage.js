import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FormControl,
  FormHelperText,
  Radio,
  RadioGroup,
  FormControlLabel,
  Button,
  Grid,
  Typography,
  TextField,
  Alert,
} from "@mui/material";

export default function CreateRoom({
  update = false,
  roomCode = null,
  updateCallback = () => {},
}) {
  const [guestCanPause, setGuestCanPause] = useState(true);
  const [votesToSkip, setVotesToSkip] = useState(2);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const navigate = useNavigate();

  const handleVotesChange = (e) => setVotesToSkip(Number(e.target.value));
  const handleGuestCanPauseChange = (e) =>
    setGuestCanPause(e.target.value === "true");

  const handleRoomAction = async () => {
    setErrorMsg("");
    setSuccessMsg("");

    const requestOptions = {
      method: update ? "PATCH" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        votes_to_skip: votesToSkip,
        guest_can_pause: guestCanPause,
        ...(update && { code: roomCode }), // Dodaj kod pokoju tylko dla PATCH
      }),
    };

    try {
      const response = await fetch(
        update ? "/api/update-room" : "/api/create-room",
        requestOptions
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const data = await response.json();

      if (update) {
        setSuccessMsg("Room updated successfully!");
        updateCallback(); // Wywołaj callback aktualizacji, jeśli istnieje
      } else {
        navigate(`/room/${data.code}`);
      }
    } catch (error) {
      setErrorMsg(
        `Failed to ${update ? "update" : "create"} room: ${error.message}`
      );
    }
  };

  return (
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <Typography component="h4" variant="h4">
          {update ? "Update Room" : "Create A Room"}
        </Typography>
      </Grid>

      {errorMsg && (
        <Grid item xs={12} align="center">
          <Alert severity="error">{errorMsg}</Alert>
        </Grid>
      )}

      {successMsg && (
        <Grid item xs={12} align="center">
          <Alert severity="success">{successMsg}</Alert>
        </Grid>
      )}

      <Grid item xs={12} align="center">
        <FormControl component="fieldset">
          <FormHelperText>Guest Control of Playback State</FormHelperText>
          <RadioGroup
            row
            defaultValue="true"
            onChange={handleGuestCanPauseChange}
          >
            <FormControlLabel
              value="true"
              control={<Radio color="primary" />}
              label="Play/Pause"
              labelPlacement="bottom"
            />
            <FormControlLabel
              value="false"
              control={<Radio color="secondary" />}
              label="No Control"
              labelPlacement="bottom"
            />
          </RadioGroup>
        </FormControl>
      </Grid>

      <Grid item xs={12} align="center">
        <FormControl>
          <TextField
            required
            type="number"
            onChange={handleVotesChange}
            value={votesToSkip}
            inputProps={{ min: 1, style: { textAlign: "center" } }}
          />
          <FormHelperText>Votes Required To Skip Song</FormHelperText>
        </FormControl>
      </Grid>

      <Grid item xs={12} align="center">
        <Button
          color="secondary"
          variant="contained"
          onClick={handleRoomAction}
        >
          {update ? "Update Room" : "Create A Room"}
        </Button>
      </Grid>

      {!update && (
        <Grid item xs={12} align="center">
          <Button
            color="primary"
            variant="contained"
            onClick={() => navigate("/")}
          >
            Back
          </Button>
        </Grid>
      )}
    </Grid>
  );
}
