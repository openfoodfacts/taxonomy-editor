import { Alert, Typography, Stack, Button, Box, Dialog } from "@mui/material";
import LanguageSelectionDialog from "./LanguageSelectionDialog";
import { useCallback, useEffect, useState } from "react";
import ISO6391 from "iso-639-1";
import { TranslationTags } from "./TranslationTags";

const SHOWN_LANGUAGES_KEY = "shownLanguages";

/**
 * Sub-component for rendering translation of an "entry"
 */
const ListTranslations = ({
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

  // Used for addition of a translation language
  const handleAddTranslation = useCallback(
    (key: string) => {
      key = "tags_" + key; // LC must have a prefix "tags_"

      if (nodeObject[key]) {
        // If the key already exists, do nothing
        return;
      }
      // Make changes to the parent NodeObject
      setNodeObject((prevState) => {
        const newNodeObject = { ...prevState };
        newNodeObject[key] = [];
        return newNodeObject;
      });
    },
    [nodeObject, setNodeObject]
  );

  const handleDialogConfirm = (newShownLanguageCodes: string[]) => {
    newShownLanguageCodes.forEach((languageCode) => {
      handleAddTranslation(languageCode);
    });
    setShownLanguageCodes(newShownLanguageCodes);
    localStorage.setItem(
      SHOWN_LANGUAGES_KEY,
      JSON.stringify(newShownLanguageCodes)
    );
    setIsDialogOpen(false);
  };

  useEffect(() => {
    // get shown languages from local storage if it exists else use main language
    try {
      let localStorageShownLanguages: string[] | null = localStorage.getItem(
        SHOWN_LANGUAGES_KEY
      )
        ? JSON.parse(localStorage.getItem(SHOWN_LANGUAGES_KEY)!)
        : null;
      // validate that shown languages is an array of strings and filter all items that are valid language codes
      if (
        Array.isArray(localStorageShownLanguages) &&
        localStorageShownLanguages.every((item) => typeof item === "string")
      ) {
        localStorageShownLanguages = localStorageShownLanguages.filter((item) =>
          ISO6391.validate(item)
        );
      } else {
        localStorageShownLanguages = [];
      }

      if (localStorageShownLanguages) {
        // if shown languages is not empty, use it
        localStorageShownLanguages.forEach((languageCode) => {
          handleAddTranslation(languageCode);
        });
        setShownLanguageCodes(localStorageShownLanguages);
      }
    } catch (e) {
      // shown languages is an empty list, when we can't parse the local storage
      console.log(e);
    }
  }, [handleAddTranslation]);

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

  const translations: Record<string, string[]> = {};
  Object.keys(nodeObject).forEach((key: string) => {
    if (key.startsWith("tags") && !key.includes("ids")) {
      const languageCode = key.split("_")[1];
      if (languagesToShow.includes(languageCode)) {
        translations[languageCode] = nodeObject[key].map((tag: string) => tag);
      }
    }
  });

  const hasFirstTranslationChanged: boolean[] = languagesToShow.map(
    (language: string) =>
      nodeObject[`tags_${language}`]?.[0] !==
      originalNodeObject[`tags_${language}`]?.[0]
  );

  return (
    <Box sx={{ ml: 4 }}>
      {/* Title */}
      <Stack direction="row" alignItems="center">
        <Typography sx={{ mt: 4, mb: 1 }} variant="h5">
          Translations
        </Typography>
        <Button sx={{ mt: 3.5, ml: 1 }} onClick={handleOpen}>
          {"(" +
            languagesToShow.length +
            " language" +
            (languagesToShow.length === 1 ? "" : "s") +
            " shown)"}
        </Button>
      </Stack>

      {/* Render translation tags for each language to show */}
      {languagesToShow.map((language: string) => (
        <Stack key={language}>
          <Stack direction="row" alignItems="center" sx={{ my: 0.5 }}>
            <Typography variant="h6">
              {ISO6391.getName(language) +
                (language === nodeObject.main_language
                  ? " (main language)"
                  : "")}
            </Typography>
          </Stack>
          {hasFirstTranslationChanged[languagesToShow.indexOf(language)] && (
            <Alert severity="warning" sx={{ mb: 1, width: "fit-content" }}>
              Changing the first translation will modify{" "}
              {language === nodeObject.main_language
                ? "the ID of the node and "
                : ""}
              the display name for this language!
            </Alert>
          )}
          <Stack direction="row" sx={{ mr: 4 }}>
            {
              <TranslationTags
                translations={translations[language]}
                saveTranslations={saveTranslationsForLanguage(language)}
              />
            }
          </Stack>
        </Stack>
      ))}

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

export default ListTranslations;
