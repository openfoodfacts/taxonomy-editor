import { Box, Button, Typography } from "@mui/material";
import { DestructuredEntryNode } from "@/backend-types/types";

/** Keep the entry's English definition and editing notes near its synonyms. */
export function EntryContext({
  node,
  isReadOnly,
}: {
  node: DestructuredEntryNode;
  isReadOnly: boolean;
}) {
  const sections = [
    ["prop_description_en", "Description"],
    ["prop_comment_en", "Comment"],
    ["prop_comments_en", "Comments"],
  ].filter(([key]) => typeof node[key] === "string" && node[key].trim());

  if (sections.length === 0) return null;

  return (
    <Box sx={{ width: "90%", maxWidth: "1000px", m: "auto", mb: 3 }}>
      {sections.map(([key, label]) => (
        <Box key={key} sx={{ mb: 2 }}>
          <Typography variant="h6" component="h2">
            {label} (English)
          </Typography>
          <Typography sx={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>
            {node[key]}
          </Typography>
        </Box>
      ))}
      {!isReadOnly && (
        <Button component="a" href="#entry-properties">
          Edit in properties
        </Button>
      )}
    </Box>
  );
}
