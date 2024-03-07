import { Link } from "react-router-dom";

import { Box, Stack, Typography } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";

import useFetch from "@/components/useFetch";
import type { ParentsAPIResponse } from "@/backend-types/types";

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

  if (isPending && !data) {
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

  if (!relations.length) {
    return (
      <Box>
        <Typography sx={{ ml: 4, mb: 1 }} variant="h5">
          No parents
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography sx={{ ml: 4, mb: 1 }} variant="h5">
        Parents
      </Typography>
      <Stack direction="row" flexWrap="wrap">
        {relations.map((relation) => (
          <Link
            key={relation}
            to={`${linkHrefPrefix}/entry/${relation}`}
            style={{ color: "#0064c8", display: "inline-block" }}
          >
            <Typography sx={{ ml: 8, mb: 1 }} variant="h6">
              {relation}
            </Typography>
          </Link>
        ))}
      </Stack>
    </Box>
  );
};

export default ListEntryParents;
