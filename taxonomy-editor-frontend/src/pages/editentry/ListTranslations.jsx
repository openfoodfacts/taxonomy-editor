import {
  Typography,
  TextField,
  Stack,
  Button,
  IconButton,
  Box,
  Dialog,
} from "@mui/material";
import LanguageSelectionDialog from "./LanguageSelectionDialog";
import { useCallback, useEffect, useState } from "react";
import AddBoxIcon from "@mui/icons-material/AddBox";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import ISO6391 from "iso-639-1";

const SHOWN_LANGUAGES_KEY = "shownLanguages";

/**
 * Sub-component for rendering translation of an "entry"
 */
const ListTranslations = ({ nodeObject, setNodeObject }) => {
  const [renderedTranslations, setRenderedTranslations] = useState([]); // Stores state of all tags
  const [mainLangRenderedTranslations, setMainLangRenderedTranslations] =
    useState([]); // Stores state of main language's tags
  const [isDialogOpen, setIsDialogOpen] = useState(false); // Used for Dialog component
  const [shownLanguages, setShownLanguages] = useState([]); // Used for storing LCs that are shown in the interface

  const [expandedLanguages, setExpandedLanguages] = useState([]);
  // Helper functions for Dialog component
  const handleClose = () => {
    setIsDialogOpen(false);
  };
  const handleOpen = () => {
    setIsDialogOpen(true);
  };

  // Used for addition of a translation language
  const handleAddTranslation = useCallback(
    (key) => {
      key = "tags_" + key; // LC must have a prefix "tags_"
      const uuidKey = key + "_uuid"; // Format for the uuid

      if (nodeObject[key]) {
        // If the key already exists, do nothing
        return;
      }
      // Make changes to the parent NodeObject
      setNodeObject((prevState) => {
        const newNodeObject = { ...prevState };
        newNodeObject[key] = [];
        newNodeObject[uuidKey] = [Math.random().toString()];
        return newNodeObject;
      });
    },
    [nodeObject, setNodeObject]
  );

  // Used for deleting a translation language
  const handleDeleteTranslation = (key) => {
    key = "tags_" + key; // LC must have a prefix "tags_"
    const uuidKey = key + "_uuid"; // Format for the uuid

    // Make changes to the parent NodeObject
    setNodeObject((prevState) => {
      const newNodeObject = { ...prevState };
      newNodeObject[key] = [];
      newNodeObject[uuidKey] = [];
      return newNodeObject;
    });
  };

  const handleDialogConfirm = (newShownLanguageCodes) => {
    newShownLanguageCodes.forEach((languageCode) => {
      handleAddTranslation(languageCode);
    });
    setShownLanguages(newShownLanguageCodes);
    localStorage.setItem(
      SHOWN_LANGUAGES_KEY,
      JSON.stringify(newShownLanguageCodes)
    );
    setIsDialogOpen(false);
  };

  const handleToggleExpand = (newLanguageCode) => {
    if (expandedLanguages.includes(newLanguageCode)) {
      setExpandedLanguages((prev) =>
        prev.filter((languageCodeItem) => languageCodeItem !== newLanguageCode)
      );
    } else {
      const newExpandedLanguages = [...expandedLanguages, newLanguageCode];
      setExpandedLanguages(newExpandedLanguages);
    }
  };

  // Changes the translations to be rendered
  // Dependent on changes occuring in "nodeObject"
  useEffect(() => {
    // Main langauge tags are considered separately, since they have to be rendered first
    const mainLangTags = [];
    const otherLangTags = [];
    const allLanguageCodes = [];
    Object.keys(nodeObject).forEach((key) => {
      // Get all tags and its corresponding language code
      // Tagids need to be recomputed, so shouldn't be rendered
      // Eg: tags_fr

      if (
        key.startsWith("tags") &&
        !key.includes("ids") &&
        !key.includes("str")
      ) {
        if (key.endsWith("uuid")) {
          const uuids = nodeObject[key];
          // If tags are for main language, add them to mainLangTags
          if (key.includes(nodeObject.main_language)) {
            nodeObject["tags_" + nodeObject["main_language"]].forEach(
              (tag, index) =>
                mainLangTags.push({
                  index: uuids[index],
                  tag: tag,
                })
            );
          }

          // If tags are not for the main language, add them to otherLangTags
          else {
            // Slice the language code
            const languageCode = key.split("_").slice(1, -1)[0];
            allLanguageCodes.push(languageCode);
            // General format for storing tags for different lc's
            const tobeInsertedObj = { languageCode: languageCode, tags: [] };
            const tagsKey = key.split("_").slice(0, -1).join("_");
            nodeObject[tagsKey].forEach((tag, index) =>
              tobeInsertedObj["tags"].push({
                index: uuids[index], // Give a unique identifier for each tag
                tag: tag,
              })
            );
            otherLangTags.push(tobeInsertedObj);
          }
        }
      }
    });
    // Set states
    setMainLangRenderedTranslations(mainLangTags);
    // sort othelangtags alphabetically
    otherLangTags.sort((a, b) => {
      // sort according to language codes
      if (a.languageCode < b.languageCode) {
        return -1;
      }
      if (a.languageCode > b.languageCode) {
        return 1;
      }
      return 0;
    });
    setRenderedTranslations(otherLangTags);
  }, [nodeObject]);

  useEffect(() => {
    // get shown languages from local storage if it exists else use main language
    try {
      let localStorageShownLanguages = JSON.parse(
        localStorage.getItem(SHOWN_LANGUAGES_KEY)
      );
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
        setShownLanguages(localStorageShownLanguages);
        localStorageShownLanguages.forEach((languageCode) => {
          handleAddTranslation(languageCode);
        });
      }
    } catch (e) {
      // shown languages is an empty list, when we can't parse the local storage
      console.log(e);
    }
  }, [handleAddTranslation]);

  // Helper function used for changing state
  const changeData = (key, index, value) => {
    let updatedTags = []; // Stores all the tags of a language code

    if (key === nodeObject["main_language"]) {
      // Update state in correct format after duplication
      const updatedObj = { index: index, tag: value };
      updatedTags = mainLangRenderedTranslations.map((el) =>
        el.index === index ? updatedObj : el
      );
      setMainLangRenderedTranslations(updatedTags);
    } else {
      let duplicateOtherTags = []; // Stores the updated state for "renderedTranslations"
      const updatedObj = { index: index, tag: value };
      renderedTranslations.forEach((allTagsObj) => {
        // Check if update LC and current element LC are same
        // If LC is same, the element's tags needs to be updated
        if (allTagsObj["languageCode"] === key) {
          const newTags = allTagsObj["tags"].map((el) =>
            el.index === index ? updatedObj : el
          );

          // Append according to format used in "renderedTranslations"
          duplicateOtherTags.push({
            languageCode: key,
            tags: newTags,
          });
          updatedTags = [...newTags]; // Assign to updatedTags for later use
        }
        // If LC is not the same, element doesn't require any changes
        else {
          duplicateOtherTags.push(allTagsObj);
        }
      });
      // Set state
      setRenderedTranslations(duplicateOtherTags);
    }

    let tagsToBeInserted = updatedTags.map((el) => el.tag); // Removes unique idenitifer from each tag

    key = "tags_" + key; // LC must have a prefix "tags_"

    // Make changes to the parent NodeObject
    setNodeObject((prevState) => {
      const newNodeObject = { ...prevState };
      newNodeObject[key] = tagsToBeInserted;
      return newNodeObject;
    });
  };

  // Helper function for adding a translation for a LC
  const handleAdd = (key) => {
    if (!expandedLanguages.includes(key)) {
      handleToggleExpand(key);
    }
    let tagsToBeInserted = [];
    const newUUID = Math.random().toString();
    // State of "MainLangRenderedTranslations" is updated according to format used
    if (key === nodeObject.main_language) {
      const duplicateMainLangRenderedTranslations = [
        ...mainLangRenderedTranslations,
        { index: newUUID, tag: "" },
      ];
      setMainLangRenderedTranslations(duplicateMainLangRenderedTranslations); // Set state

      // Updated tags assigned for later use
      tagsToBeInserted = duplicateMainLangRenderedTranslations.map(
        (el) => el.tag
      );
    }
    // State of "renderedTranslations" is updated according to format used
    else {
      const newRenderedTranslations = [...renderedTranslations];
      newRenderedTranslations.map((allTagsObj) =>
        allTagsObj["languageCode"] === key
          ? (allTagsObj["tags"].push({ index: newUUID, tag: "" }),
            // Updated tags assigned for later use
            (tagsToBeInserted = allTagsObj["tags"].map((el) => el.tag)))
          : allTagsObj
      );
      setRenderedTranslations(newRenderedTranslations); // Set state
    }
    // Set state of main NodeObject
    setNodeObject((prevState) => {
      const newNodeObject = { ...prevState };
      newNodeObject["tags_" + key] = tagsToBeInserted;
      newNodeObject["tags_" + key + "_uuid"].push(newUUID);
      return newNodeObject;
    });
  };

  const handleDelete = (key, index) => {
    let tagsToBeInserted = [];
    // State of "MainLangRenderedTranslations" is updated according to format used
    if (key === nodeObject.main_language) {
      const duplicateMainLangRenderedTranslations =
        mainLangRenderedTranslations.filter((obj) => !(index === obj.index));
      setMainLangRenderedTranslations(duplicateMainLangRenderedTranslations); // Set state

      // Updated tags assigned for later use
      tagsToBeInserted = duplicateMainLangRenderedTranslations.map(
        (el) => el.tag
      );
    }
    // State of "renderedTranslations" is updated according to format used
    else {
      const newRenderedTranslations = [];
      renderedTranslations.forEach((allTagsObj) => {
        if (allTagsObj["languageCode"] === key) {
          const unDeletedTags = allTagsObj["tags"].filter(
            (tagObj) => !(tagObj.index === index)
          );
          newRenderedTranslations.push({
            languageCode: key,
            tags: unDeletedTags,
          });
          // Updated tags assigned for later use
          tagsToBeInserted = [...unDeletedTags].map((el) => el.tag);
        } else {
          newRenderedTranslations.push(allTagsObj);
        }
      });
      setRenderedTranslations(newRenderedTranslations); // Set state
    }
    // Set state of main NodeObject
    setNodeObject((prevState) => {
      const newNodeObject = { ...prevState };
      newNodeObject["tags_" + key] = tagsToBeInserted;
      newNodeObject["tags_" + key + "_uuid"] = newNodeObject[
        "tags_" + key + "_uuid"
      ].filter((currIndex) => !(currIndex === index));
      return newNodeObject;
    });
  };

  return (
    <Box sx={{ ml: 4 }}>
      {/* Title */}
      <Stack direction="row" alignItems="center">
        <Typography sx={{ mt: 4, mb: 1 }} variant="h5">
          Translations
        </Typography>
        <Button sx={{ mt: 3.5, ml: 1 }} onClick={handleOpen}>
          {"(" + shownLanguages.length + " languages shown)"}
        </Button>
      </Stack>

      {/* Main Language */}
      <Stack direction="row" alignItems="center">
        <Typography variant="h6">
          {nodeObject && ISO6391.getName(nodeObject.main_language)}
        </Typography>
        <IconButton
          sx={{ ml: 1 }}
          onClick={() => handleAdd(nodeObject.main_language)}
        >
          <AddBoxIcon />
        </IconButton>
      </Stack>

      {/* Render main language tags */}
      {nodeObject &&
        mainLangRenderedTranslations.map(({ index, tag }) => {
          return (
            <Stack
              sx={{ ml: 2 }}
              key={index}
              direction="row"
              alignItems="center"
            >
              <TextField
                size="small"
                sx={{ mt: 1 }}
                onChange={(event) => {
                  changeData(
                    nodeObject["main_language"],
                    index,
                    event.target.value
                  );
                }}
                value={tag}
                variant="outlined"
              />

              <IconButton
                sx={{ ml: 1, mt: 1 }}
                onClick={() => handleDelete(nodeObject.main_language, index)}
              >
                <DeleteOutlineIcon />
              </IconButton>
            </Stack>
          );
        })}

      {/* All other languages */}
      {renderedTranslations.map((allTagsObj) => {
        if (shownLanguages.includes(allTagsObj["languageCode"])) {
          const lang = allTagsObj["languageCode"];
          const tagValue = allTagsObj["tags"];
          return (
            <Box key={lang}>
              <Stack sx={{ mt: 2 }} direction="row" alignItems="center">
                <Typography variant="h6">{ISO6391.getName(lang)}</Typography>
                <IconButton sx={{ ml: 1 }} onClick={() => handleAdd(lang)}>
                  <AddBoxIcon />
                </IconButton>
                <IconButton onClick={() => handleDeleteTranslation(lang)}>
                  <DeleteOutlineIcon />
                </IconButton>
                <IconButton onClick={() => handleToggleExpand(lang)}>
                  {expandedLanguages.includes(lang) ? (
                    <VisibilityIcon />
                  ) : (
                    <VisibilityOffIcon />
                  )}
                </IconButton>
              </Stack>
              {/* Render all related tags */}
              {tagValue.length > 0 ? (
                tagValue.map((tagObj) => {
                  const index = tagObj["index"];
                  const tag = tagObj["tag"];
                  return (
                    expandedLanguages.includes(lang) && (
                      <Stack
                        key={index}
                        sx={{ ml: 2 }}
                        direction="row"
                        alignItems="center"
                      >
                        <TextField
                          size="small"
                          sx={{ mt: 1 }}
                          onChange={(event) => {
                            changeData(lang, index, event.target.value);
                          }}
                          value={tag}
                          variant="outlined"
                        />
                        <IconButton
                          sx={{ ml: 1, mt: 1 }}
                          onClick={() => handleDelete(lang, index)}
                        >
                          <DeleteOutlineIcon />
                        </IconButton>
                      </Stack>
                    )
                  );
                })
              ) : (
                <Button sx={{ ml: 2 }} onClick={() => handleAdd(lang)}>
                  Add a Translation
                </Button>
              )}
            </Box>
          );
        } else {
          return null;
        }
      })}

      {/* Dialog box for adding translations */}
      <Dialog open={isDialogOpen} onClose={handleClose}>
        <LanguageSelectionDialog
          handleClose={handleClose}
          mainLanguage={nodeObject.main_language}
          handleDialogConfirm={handleDialogConfirm}
          shownLanguages={shownLanguages}
        />
      </Dialog>
    </Box>
  );
};

export default ListTranslations;
