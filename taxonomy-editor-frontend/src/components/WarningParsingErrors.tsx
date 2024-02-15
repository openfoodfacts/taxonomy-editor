import React from "react";
import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import useFetch from "./useFetch";

interface CustomAlertProps {
  severity: "error" | "warning" | "info" | "success";
  title?: string;
  message: string;
}

interface WarningParsingErrorsProps {
  baseUrl: string;
}

interface ParsingErrorsType {
  errors: string[];
}

const CustomAlert: React.FC<CustomAlertProps> = ({
  severity,
  title,
  message,
}) => {
  return (
    <Alert severity={severity}>
      {title && <AlertTitle>{title}</AlertTitle>}
      {message}
    </Alert>
  );
};

// warning users the taxonomy had parsing errors, so should not edit it
export const WarningParsingErrors: React.FC<WarningParsingErrorsProps> = ({
  baseUrl,
}) => {
  const { data: parsingErrors, isPending: isPendingParsingErrors } =
    useFetch<ParsingErrorsType>(`${baseUrl}parsing_errors`);
  if (!isPendingParsingErrors) {
    return (
      <>
        {parsingErrors && parsingErrors.errors.length !== 0 && (
          <CustomAlert
            severity="warning"
            title="Parsing errors"
            message="This taxonomy has encountered parsing errors. 
            Please review and fix errors on the 'Errors' page, so that the 
            taxonomy can then be edited."
          />
        )}
      </>
    );
  } else {
    return null;
  }
};

export default WarningParsingErrors;
