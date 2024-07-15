import {
  Alert,
  Typography,
  Stack,
  Button,
  Box,
  Dialog,
  Checkbox,
  IconButton,
  Tooltip,
} from "@mui/material";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import PushPinOutlinedIcon from "@/assets/icons/pushpin-line-grey.svg?react";
import LanguageSelectionDialog from "./LanguageSelectionDialog";
import { useMemo, useEffect, useState } from "react";
import ISO6391 from "iso-639-1";
import { TranslationTags } from "./TranslationTags";

export const SHOWN_LANGUAGES_KEY = "shownLanguages";

const getLanguageName = (languageCode: string): string => {
  if (languageCode === "xx") {
    return "Fallback translations";
  }
  const languageName = ISO6391.getName(languageCode);
  if (languageName === "") {
    return languageCode;
  }
  return languageName;
};

const sortByLanguageName = (lcA: any, lcB: any): number => {
  const languageNameA = getLanguageName(lcA);
  const languageNameB = getLanguageName(lcB);

  if (languageNameA < languageNameB) {
    return -1;
  } else if (languageNameA > languageNameB) {
    return 1;
  } else {
    return 0;
  }
};

/**
 * Sub-component for rendering translation of an "entry"
 */
export const ListTranslations = ({
  originalNodeObject,
  nodeObject,
  setNodeObject,
  isReadOnly,
}) => {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false); // Used for Dialog component
  const [shownLanguageCodes, setShownLanguageCodes] = useState<string[]>([]); // Used for storing LCs that are shown in the interface
  const [showExistingTranslations, setShowExistingTranslations] =
    useState<boolean>(false);

  const xxLanguageExists = useMemo(() => {
    const exists =
      nodeObject["tags_xx"] === undefined
        ? false
        : nodeObject["tags_xx"].length > 0;
    return exists;
  }, [nodeObject]);

  const handleLanguagePin = (languageCode: string) => {
    let newShownLanguageCodes: string[];
    if (shownLanguageCodes.includes(languageCode)) {
      newShownLanguageCodes = shownLanguageCodes.filter(
        (langCode) => langCode !== languageCode,
      );
    } else {
      newShownLanguageCodes = [...shownLanguageCodes, languageCode];
      newShownLanguageCodes.sort(sortByLanguageName);
    }
    localStorage.setItem(
      SHOWN_LANGUAGES_KEY,
      JSON.stringify(newShownLanguageCodes),
    );
    setShownLanguageCodes(newShownLanguageCodes);
  };

  // Helper functions for Dialog component
  const handleClose = () => {
    setIsDialogOpen(false);
  };
  const handleOpen = () => {
    setIsDialogOpen(true);
  };

  const handleDialogConfirm = (newLanguageCodes: string[]) => {
    let newShownLanguageCodes = [...shownLanguageCodes];
    newLanguageCodes.forEach((languageCode) => {
      if (shownLanguageCodes.includes(languageCode)) {
        newShownLanguageCodes = newShownLanguageCodes.filter(
          (langCode) => langCode !== languageCode,
        );
      } else {
        newShownLanguageCodes.push(languageCode);
        newShownLanguageCodes.sort(sortByLanguageName);
      }
    });
    localStorage.setItem(
      SHOWN_LANGUAGES_KEY,
      JSON.stringify(newShownLanguageCodes),
    );
    setShownLanguageCodes(newShownLanguageCodes);

    setIsDialogOpen(false);
  };

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

      if (localStorageShownLanguages) {
        // if shown languages is not empty, use it
        if (xxLanguageExists && !localStorageShownLanguages.includes("xx")) {
          localStorageShownLanguages = ["xx", ...localStorageShownLanguages];
        }
        setShownLanguageCodes(localStorageShownLanguages);
      }
    } catch (e) {
      // shown languages is an empty list, when we can't parse the local storage
      console.log(e);
    }
  }, [xxLanguageExists]);

  const saveTranslationsForLanguage = (language: string) => {
    return (translations: string[]) => {
      setNodeObject((prevState) => {
        const newNodeObject = { ...prevState };
        newNodeObject["tags_" + language] = translations;
        return newNodeObject;
      });
    };
  };

  let languagesToShow: string[];
  languagesToShow = shownLanguageCodes.filter(
    (languageCode) => languageCode !== nodeObject.mainLanguage,
  );
  if (shownLanguageCodes.includes("xx")) {
    languagesToShow = languagesToShow.filter(
      (languageCode) => languageCode !== "xx",
    );
    languagesToShow.unshift("xx");
  }
  languagesToShow.unshift(nodeObject.mainLanguage);

  if (showExistingTranslations) {
    languagesToShow.push(
      ...Object.keys(nodeObject)
        .filter(
          (key) =>
            key.startsWith("tags_") &&
            !key.startsWith("tags_ids_") &&
            (nodeObject[key]?.length > 0 ||
              originalNodeObject[key]?.length > 0),
        )
        .map((key) => key.slice(5))
        .filter((languageCode) => !languagesToShow.includes(languageCode))
        .sort(sortByLanguageName),
    );
  }

  const hasFirstTranslationChanged: boolean[] = languagesToShow.map(
    (language: string) =>
      originalNodeObject[`tags_${language}`]?.[0] &&
      nodeObject[`tags_${language}`]?.[0] &&
      nodeObject[`tags_${language}`]?.[0] !==
        originalNodeObject[`tags_${language}`]?.[0],
  );

  const shownLanguagesInfo = languagesToShow.map((languageCode: string) => {
    const languageName =
      getLanguageName(languageCode) +
      (languageCode === nodeObject.mainLanguage ? " (main language)" : "");
    const alertMessage =
      "Changing the first translation will modify " +
      (languageCode === nodeObject.mainLanguage
        ? "the ID of the node and "
        : "") +
      "the display name for this language!";
    return { languageCode, languageName, alertMessage };
  });

  return (
    <Box sx={{ ml: 4 }}>
      {/* Title */}
      <Stack direction="row" alignItems="center" sx={{ mt: 4 }}>
        <Typography sx={{ mb: 1, mr: 2 }} variant="h5">
          Translations
        </Typography>
        {/* if "xx" words exist, the "Fallback translations" are always
        displayed, the user can't choose */}
        <Checkbox
          checked={xxLanguageExists ? true : shownLanguageCodes.includes("xx")}
          disabled={xxLanguageExists}
          onClick={() => handleLanguagePin("xx")}
        />
        <Typography
          variant="h6"
          sx={{ color: `${xxLanguageExists ? "#bdbdbd" : ""}`, mr: 1 }}
        >
          Show fallback translations
        </Typography>
        <Checkbox
          checked={showExistingTranslations}
          onClick={() => {
            setShowExistingTranslations(!showExistingTranslations);
          }}
        />
        <Typography variant="h6">Show all existing translations</Typography>
      </Stack>

      {!["en", "xx"].includes(nodeObject.mainLanguage) && (
        <Alert severity="info" sx={{ width: "fit-content" }}>
          English or Fallback translations is not the main language for this
          entry. Please consider changing it to adhere to the prevailing
          convention.
        </Alert>
      )}

      {/* Render translation tags for each language to show */}
      {shownLanguagesInfo.map(
        ({ languageCode, languageName, alertMessage }) => {
          const isLanguageSelected = shownLanguageCodes.includes(languageCode);
          return (
            <Stack key={languageCode}>
              <Stack direction="row" alignItems="center" sx={{ my: 0.5 }}>
                <Typography
                  variant="h6"
                  sx={{
                    color: `${!isLanguageSelected ? "grey" : ""}`,
                  }}
                >
                  {languageName}
                </Typography>

                {languageCode !== "xx" && (
                  <Tooltip
                    title={`${
                      isLanguageSelected ? "Hide language" : "Pin language"
                    }`}
                    placement="right"
                    arrow
                  >
                    <IconButton
                      sx={{
                        color: "grey",
                        ml: 1,
                      }}
                      onClick={() => handleLanguagePin(languageCode)}
                    >
                      {!isLanguageSelected ? (
                        <PushPinOutlinedIcon width={24} height={24} />
                      ) : (
                        <VisibilityOffOutlinedIcon />
                      )}
                    </IconButton>
                  </Tooltip>
                )}
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
                    isReadOnly={isReadOnly}
                  />
                }
              </Stack>
            </Stack>
          );
        },
      )}

      <Button sx={{ my: 1 }} onClick={handleOpen}>
        Show another language
      </Button>

      {/* Dialog box for adding translations */}
      <Dialog open={isDialogOpen} onClose={handleClose}>
        <LanguageSelectionDialog
          handleClose={handleClose}
          mainLanguageCode={nodeObject.mainLanguage}
          handleDialogConfirm={handleDialogConfirm}
          shownLanguageCodes={shownLanguageCodes}
        />
      </Dialog>
    </Box>
  );
};
