import { EntryNode } from "@/client";
import {
  Chip,
  Stack,
  TableBody,
  TableCell,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import { Link } from "react-router-dom";
import ISO6391 from "iso-639-1";

type Props = {
  entryNodes: EntryNode[];
  taxonomyName: string;
  branchName: string;
};

const EntryTitle = ({ id }: { id: string }) => {
  const languageCode = id.split(":", 1)[0];
  const languageName = ISO6391.getName(languageCode);
  return (
    <Typography variant="subtitle1">
      {id.slice(languageCode.length + 1)}
      <Tooltip title="Main language of the entry" placement="right" arrow>
        <Chip label={languageName} size="small" sx={{ ml: 1, mb: 0.5 }} />
      </Tooltip>
    </Typography>
  );
};

const displayTranslatedLanguages = (tags: Record<string, string[]>) => {
  const languageCodes = Object.keys(tags)
    .filter((tag) => tag.includes("_ids_"))
    .map((tag) => tag.split("_").at(-1) as string);
  const languageNames = languageCodes.map((code) => ISO6391.getName(code));
  return "Translated in " + languageNames.join(", ");
};

export const EntryNodesTableBody = ({
  entryNodes,
  taxonomyName,
  branchName,
}: Props) => {
  return (
    <>
      <TableBody>
        {entryNodes.map(({ id, isExternal, tags }) => (
          <TableRow
            key={id}
            hover
            component={Link}
            to={`/${taxonomyName}/${branchName}/entry/${id}`}
            sx={{ textDecoration: "none" }}
          >
            <TableCell align="left" component="td" scope="row">
              <Stack gap={0.5}>
                <EntryTitle id={id} />
                {isExternal && (
                  <Typography variant="subtitle2" color="secondary">
                    External Node
                  </Typography>
                )}
                <Typography variant="body2" color="inherit">
                  {Object.keys(tags).length === 0
                    ? "No translations"
                    : displayTranslatedLanguages(tags)}
                </Typography>
              </Stack>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </>
  );
};
