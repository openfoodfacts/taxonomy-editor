import useFetch from "../../components/useFetch";
import { Box, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import Loader from "../../components/Loader";

const ListEntryParents = ({ url, urlPrefix }) => {
  const [relations, setRelations] = useState(null);
  /* eslint no-unused-vars: ["error", { varsIgnorePattern: "^__" }] */
  const {
    data: incomingData,
    isPending,
    isError,
    __isSuccess,
    errorMessage,
  } = useFetch(url);

  useEffect(() => {
    setRelations(incomingData);
  }, [incomingData]);

  // Check error in fetch
  if (isError) {
    return (
      <Typography sx={{ ml: 4 }} variant="h5">
        {errorMessage}
      </Typography>
    );
  }
  if (isPending) {
    return (
      <Loader />
    );
  }
  return (
    <Box>
      {
        <Typography sx={{ ml: 4, mb: 1 }} variant="h5">
          Parents
        </Typography>
      }

      {/* Renders parents or children of the node */}
      {relations &&
        relations.map((relation) => (
          <Box key={relation}>
            <Link
              to={`${urlPrefix}/entry/${relation}`}
              style={{ color: "#0064c8", display: "inline-block" }}
            >
              <Typography sx={{ ml: 8, mb: 1 }} variant="h6">
                {relation}
              </Typography>
            </Link>
          </Box>
        ))}

      {/* When no parents or children are present */}
      {relations && relations.length === 0 && (
        <Typography sx={{ ml: 8, mb: 1 }} variant="h6">
          {" "}
          None{" "}
        </Typography>
      )}
    </Box>
  );
};

export default ListEntryParents;
