import Tags from "@yaireo/tagify/dist/react.tagify"; // React-wrapper file
import DragSort from "@yaireo/dragsort";
import "@yaireo/tagify/dist/tagify.css"; // Tagify CSS
import "@yaireo/dragsort/dist/dragsort.css";
import "./TranslationTags.css";
import { useMemo, useRef } from "react";

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

  if (isReadOnly) {
    return <Tags value={translations} readOnly />;
  }

  return (
    <Tags
      tagifyRef={tagifyRefDragSort}
      onChange={handleChange}
      value={translations}
    />
  );
};
