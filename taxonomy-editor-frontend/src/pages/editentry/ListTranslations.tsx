import { Alert, Typography, Stack, Button, Box, Dialog } from "@mui/material";
import LanguageSelectionDialog from "./LanguageSelectionDialog";
import { useEffect, useState } from "react";
import ISO6391 from "iso-639-1";
import { TranslationTags } from "./TranslationTags";

const SHOWN_LANGUAGES_KEY = "shownLanguages";

/**
 * Sub-component for rendering translation of an "entry"
 */
export const ListTranslations = ({
  originalNodeObject,
  nodeObject,
  setNodeObject,
}) => {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false); // Used for Dialog component
  const [shownLanguageCodes, setShownLanguageCodes] = useState<string[]>([]); // Used for storing LCs that are shown in the interface

  // Helper functions for Dialog component
  const handleClose = () => {
    setIsDialogOpen(false);
  };
  const handleOpen = () => {
    setIsDialogOpen(true);
  };

  const xxLanguageExists = () => {
    const exists =
      nodeObject["tags_xx"] === undefined
        ? false
        : nodeObject["tags_xx"].length > 0;
    return exists;
  };

  const handleDialogConfirm = (newShownLanguageCodes: string[]) => {
    localStorage.setItem(
      SHOWN_LANGUAGES_KEY,
      JSON.stringify(newShownLanguageCodes)
    );

    if (xxLanguageExists() && !newShownLanguageCodes.includes("xx")) {
      newShownLanguageCodes = ["xx", ...newShownLanguageCodes];
    }
    setShownLanguageCodes(newShownLanguageCodes);

    setIsDialogOpen(false);
  };

  useEffect(() => {
    // get shown languages from local storage if it exists else use main language
    try {
      let rawLocalStorageShownLanguages =
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
          }
        );
      } else {
        localStorageShownLanguages = [];
      }

      if (localStorageShownLanguages) {
        // if shown languages is not empty, use it
        if (xxLanguageExists() && !localStorageShownLanguages.includes("xx")) {
          localStorageShownLanguages = ["xx", ...localStorageShownLanguages];
        }
        setShownLanguageCodes(localStorageShownLanguages);
      }
    } catch (e) {
      // shown languages is an empty list, when we can't parse the local storage
      console.log(e);
    }
  }, []);

  const saveTranslationsForLanguage = (language: string) => {
    return (translations: string[]) => {
      setNodeObject((prevState) => {
        const newNodeObject = { ...prevState };
        newNodeObject["tags_" + language] = translations;
        return newNodeObject;
      });
    };
  };

  const languagesToShow: string[] = shownLanguageCodes.filter(
    (languageCode) => languageCode !== nodeObject.main_language
  );
  languagesToShow.unshift(nodeObject.main_language);

  const numberOfLanguagesShownMessage =
    "(" +
    languagesToShow.length +
    " language" +
    (languagesToShow.length === 1 ? "" : "s") +
    " shown)";

  const hasFirstTranslationChanged: boolean[] = languagesToShow.map(
    (language: string) =>
      nodeObject[`tags_${language}`]?.[0] !==
      originalNodeObject[`tags_${language}`]?.[0]
  );

  const shownLanguagesInfo = languagesToShow.map((languageCode: string) => {
    const languageName =
      languageCode === "xx"
        ? "All languages"
        : ISO6391.getName(languageCode) +
          (languageCode === nodeObject.main_language ? " (main language)" : "");
    const alertMessage =
      "Changing the first translation will modify " +
      (languageCode === nodeObject.main_language
        ? "the ID of the node and "
        : "") +
      "the display name for this language!";
    return { languageCode, languageName, alertMessage };
  });

  return (
    <Box sx={{ ml: 4 }}>
      {/* Title */}
      <Stack direction="row" alignItems="center">
        <Typography sx={{ mt: 4, mb: 1 }} variant="h5">
          Translations
        </Typography>
        <Button sx={{ mt: 3.5, ml: 1 }} onClick={handleOpen}>
          {numberOfLanguagesShownMessage}
        </Button>
      </Stack>

      {/* Render translation tags for each language to show */}
      {shownLanguagesInfo.map(
        ({ languageCode, languageName, alertMessage }) => (
          <Stack key={languageCode}>
            <Stack direction="row" alignItems="center" sx={{ my: 0.5 }}>
              <Typography variant="h6">{languageName}</Typography>
            </Stack>
            {hasFirstTranslationChanged[
              languagesToShow.indexOf(languageCode)
            ] && (
              <Alert severity="warning" sx={{ mb: 1, width: "fit-content" }}>
                {alertMessage}
              </Alert>
            )}
            <Stack direction="row" sx={{ mr: 4 }}>
              {
                <TranslationTags
                  translations={nodeObject["tags_" + languageCode] ?? []}
                  saveTranslations={saveTranslationsForLanguage(languageCode)}
                />
              }
            </Stack>
          </Stack>
        )
      )}

      {/* Dialog box for adding translations */}
      <Dialog open={isDialogOpen} onClose={handleClose}>
        <LanguageSelectionDialog
          handleClose={handleClose}
          mainLanguageCode={nodeObject.main_language}
          handleDialogConfirm={handleDialogConfirm}
          shownLanguageCodes={shownLanguageCodes}
        />
      </Dialog>
    </Box>
  );
};
