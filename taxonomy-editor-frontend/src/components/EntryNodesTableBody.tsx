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
import { useEffect, useState } from "react";
import { SHOWN_LANGUAGES_KEY } from "@/pages/project/editentry/ListTranslations";

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

const getTranslations = (
  tags: Record<string, string[]>,
  shownLanguageCodes: string[],
) => {
  const result: string[] = [];

  shownLanguageCodes.forEach((languageCode) => {
    const languageName =
      languageCode === "xx"
        ? "Fallback translations"
        : ISO6391.getName(languageCode);
    const translations = tags[`tags_${languageCode}`];
    if (translations) {
      result.push(`${languageName}: ${translations.join(", ")}`);
    }
  });

  return result;
};

export const EntryNodesTableBody = ({
  entryNodes,
  taxonomyName,
  branchName,
}: Props) => {
  const [shownLanguageCodes, setShownLanguageCodes] = useState<string[]>([]);

  useEffect(() => {
    // get shown languages from local storage if it exists else use main language
    try {
      const rawLocalStorageShownLanguages =
        localStorage.getItem(SHOWN_LANGUAGES_KEY);
      let localStorageShownLanguages: string[] | null =
        rawLocalStorageShownLanguages
          ? JSON.parse(rawLocalStorageShownLanguages)
          : null;
      // validate that shown languages is an array of strings and filter all items that are valid language codes
      if (
        Array.isArray(localStorageShownLanguages) &&
        localStorageShownLanguages.every((item) => typeof item === "string")
      ) {
        localStorageShownLanguages = localStorageShownLanguages.filter(
          (item) => {
            return item === "xx" || ISO6391.validate(item);
          },
        );
      } else {
        localStorageShownLanguages = [];
      }
      setShownLanguageCodes(localStorageShownLanguages);
    } catch (e) {
      // shown languages is an empty list, when we can't parse the local storage
      console.log(e);
    }
  }, []);

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
                {getTranslations(tags, shownLanguageCodes).map((line, i) => (
                  <Typography key={i} variant="body2" color="inherit">
                    {line}
                  </Typography>
                ))}
              </Stack>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </>
  );
};
