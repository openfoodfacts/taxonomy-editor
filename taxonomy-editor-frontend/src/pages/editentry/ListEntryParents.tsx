import { Link } from "react-router-dom";

import { Box, Typography } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";

import useFetch from "../../components/useFetch";
import type { ParentsAPIResponse } from "../../backend-types/types";

type Props = {
  fetchUrl: string;
  linkHrefPrefix: string;
};

const ListEntryParents = ({ fetchUrl, linkHrefPrefix }: Props) => {
  const { data, isPending, isError, errorMessage } =
    useFetch<ParentsAPIResponse>(fetchUrl);

  const relations = data ?? [];

  if (isError) {
    return (
      <Typography sx={{ ml: 4 }} variant="h5">
        {errorMessage}
      </Typography>
    );
  }

  if (isPending) {
    return (
      <Box
        sx={{
          textAlign: "center",
          my: 5,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {
        <Typography sx={{ ml: 4, mb: 1 }} variant="h5">
          Parents
        </Typography>
      }

      {relations.length === 0 ? (
        <Typography sx={{ ml: 8, mb: 1 }} variant="h6">
          None
        </Typography>
      ) : (
        relations.map((relation) => (
          <Box key={relation}>
            <Link
              to={`${linkHrefPrefix}/entry/${relation}`}
              style={{ color: "#0064c8", display: "inline-block" }}
            >
              <Typography sx={{ ml: 8, mb: 1 }} variant="h6">
                {relation}
              </Typography>
            </Link>
          </Box>
        ))
      )}
    </Box>
  );
};

export default ListEntryParents;
