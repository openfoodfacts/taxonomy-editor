import {
  LoaderFunction,
  Outlet,
  useLoaderData,
  useParams,
} from "react-router-dom";
import { DefaultService, Project, ProjectStatus } from "@/client";
import { QueryClient, useQuery } from "@tanstack/react-query";
import { Box, CircularProgress, Typography } from "@mui/material";
import { ResponsiveAppBar } from "@/components/ResponsiveAppBar";

interface ProjectParams {
  taxonomyName: string;
  branchName: string;
}

const getProjectQuery = (taxonomyName: string, branchName: string) => ({
  queryKey: [taxonomyName, branchName],
  queryFn: async () => {
    return await DefaultService.getProjectInfoTaxonomyNameBranchProjectGet(
      branchName,
      taxonomyName
    );
  },
});

export const projectLoader =
  (queryClient: QueryClient): LoaderFunction =>
  async ({ params }) => {
    // https://github.com/remix-run/react-router/issues/8200#issuecomment-962520661
    const { taxonomyName, branchName } = params as unknown as ProjectParams;
    const projectQuery = getProjectQuery(taxonomyName, branchName);
    return queryClient.ensureQueryData(projectQuery);
  };

const ProjectLoading = () => {
  return (
    <Box
      sx={{
        textAlign: "center",
        my: 10,
      }}
    >
      <CircularProgress />
      <Typography sx={{ m: 5 }} variant="h6">
        Taxonomy parsing may take several minutes, depending on the complexity
        of the taxonomy being imported.
      </Typography>
    </Box>
  );
};

export const ProjectPage = () => {
  const initialData = useLoaderData() as Project;
  const { taxonomyName, branchName } = useParams() as unknown as ProjectParams;
  const { data: project } = useQuery({
    ...getProjectQuery(taxonomyName, branchName),
    initialData,
    refetchInterval: (query) => {
      return query.state.status === "success" &&
        query.state.data?.status === ProjectStatus.LOADING
        ? 2000
        : false;
    },
  });

  const navUrlPrefix = `${taxonomyName}/${branchName}/`;
  const navLink = [
    { url: navUrlPrefix + "entry", translationKey: "Nodes" },
    { url: navUrlPrefix + "search", translationKey: "Search" },
    { url: navUrlPrefix + "export", translationKey: "Export" },
    { url: navUrlPrefix + "errors", translationKey: "Errors" },
  ];

  return (
    <>
      <ResponsiveAppBar displayedPages={navLink} />
      {project.status === ProjectStatus.LOADING ? (
        <ProjectLoading />
      ) : (
        <Outlet />
      )}
    </>
  );
};
