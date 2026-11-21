import TagsPkg from "@yaireo/tagify/dist/react.tagify"; // React-wrapper file
import DragSort from "@yaireo/dragsort";
import "@yaireo/tagify/dist/tagify.css"; // Tagify CSS
import "@yaireo/dragsort/dist/dragsort.css";
import "./TranslationTags.css";
import { useMemo, useRef } from "react";

const Tags = TagsPkg.default ?? TagsPkg;

// A synonym can contain a comma: "2,5" (between digits) or "\," (escaped),
// as in the taxonomy files. Only split on the other commas.
// A comma after a digit waits for the next character to decide.
// The pattern must start with "," because Tagify uses its first character
// to join pasted lines.
const SYNONYM_DELIMITERS = String.raw`,(?<![\\\d],)|(?<=\d),(?=\D)`;

// Tagify splits every string of its initial value on the delimiters,
// objects are taken as whole tags.
const toTagifyValue = (translations: string[]) =>
  translations.map((value) => ({ value }));

type TranslationTagsProps = {
  translations: string[];
  saveTranslations: (translations: string[]) => void;
  isReadOnly: boolean;
};

export const TranslationTags = ({
  translations,
  saveTranslations,
  isReadOnly,
}: TranslationTagsProps) => {
  const tagifyRefDragSort = useRef<typeof Tags>(null);

  const handleDragEnd = () => {
    tagifyRefDragSort.current?.updateValueByDOMTags();
  };

  const handleChange = (e) => {
    const translations: string[] = e.detail.tagify
      .getCleanValue()
      .map((tag) => tag.value);
    saveTranslations(translations);
  };

  // Inspired from the codesandbox example in https://github.com/yairEO/tagify#react
  useMemo(() => {
    if (tagifyRefDragSort.current)
      new DragSort(tagifyRefDragSort.current.DOM.scope, {
        selector: ".tagify__tag",
        callbacks: {
          dragEnd: handleDragEnd,
        },
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tagifyRefDragSort.current]);

  const value = useMemo(() => toTagifyValue(translations), [translations]);

  if (isReadOnly) {
    return <Tags value={value} readOnly />;
  }

  return (
    <Tags
      tagifyRef={tagifyRefDragSort}
      onChange={handleChange}
      value={value}
      settings={{ delimiters: SYNONYM_DELIMITERS }}
    />
  );
};
