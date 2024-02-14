import { Alert, AlertTitle } from "@mui/material";
import { DefaultService } from "@/client";
import { useQuery } from "@tanstack/react-query";

interface CustomAlertProps {
  severity: "error" | "warning" | "info" | "success";
  title?: string;
  message: string;
}

interface WarningParsingErrorsProps {
  taxonomyName: string;
  branchName: string;
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
  taxonomyName,
  branchName,
}) => {
  const { data: errorNode } = useQuery({
    queryKey: [
      "findAllErrorsTaxonomyNameBranchParsingErrorsGet",
      taxonomyName,
      branchName,
    ],
    queryFn: async () => {
      return await DefaultService.findAllErrorsTaxonomyNameBranchParsingErrorsGet(
        branchName,
        taxonomyName
      );
    },
  });

  if (errorNode?.errors.length !== 0) {
    return (
      <CustomAlert
        severity="warning"
        title="Parsing errors"
        message="This taxonomy has encountered parsing errors. 
        Please review and fix errors on the 'Errors' page, so that the 
        taxonomy can then be edited."
      />
    );
  }

  return null;
};
