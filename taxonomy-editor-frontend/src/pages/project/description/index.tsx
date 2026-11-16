import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Box, Typography } from "@mui/material";

import { toTitleCase } from "@/utils";
import { getProjectQuery } from "@/pages/project";

interface ProjectDescriptionParams {
  taxonomyName: string;
  branchName: string;
}

export const ProjectDescription = () => {
  const { taxonomyName, branchName } =
    useParams() as unknown as ProjectDescriptionParams;
  // already fetched by the project loader, so this is served from the cache
  const { data: project } = useQuery({
    ...getProjectQuery(taxonomyName, branchName),
    refetchOnMount: false,
  });

  if (!project) {
    return null;
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h4">Project description</Typography>
      <Typography variant="body1" color="text.secondary">
        {toTitleCase(project.taxonomyName)} &middot; {project.branchName}
        {project.ownerName && <> &middot; {project.ownerName}</>}
      </Typography>
      <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
        {project.description || "No description was given for this project."}
      </Typography>
    </Box>
  );
};
