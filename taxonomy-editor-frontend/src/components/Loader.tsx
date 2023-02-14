import React from "react"
import {Box}  from "@mui/material"
import CircularProgress from "@mui/material/CircularProgress";

const Loader = () => {
    return (
        <Box sx={{
                width: "100%",
                textAlign: "center",
                py: 10,
                m: 0
            }}>
            <CircularProgress />
        </Box>
    )
}

export default Loader
