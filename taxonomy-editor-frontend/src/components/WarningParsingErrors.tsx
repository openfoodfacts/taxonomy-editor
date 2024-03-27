import { DefaultService } from "@/client";
import { Alert, AlertTitle } from "@mui/material";
import { useQuery } from "@tanstack/react-query";

interface WarningParsingErrorsProps {
  taxonomyName: string;
  branchName: string;
}

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

  if (errorNode && errorNode?.errors.length !== 0) {
    return (
      <Alert severity="warning">
        <AlertTitle>Parsing errors</AlertTitle>
        This taxonomy has encountered parsing errors. Please review and fix
        errors on the &apos;Errors&apos; page, so that the taxonomy can then be
        edited.
      </Alert>
    );
  }

  return null;
};
