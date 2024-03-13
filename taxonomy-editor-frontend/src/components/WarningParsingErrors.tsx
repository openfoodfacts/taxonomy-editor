import { DefaultService } from "@/client";
import { useQuery } from "@tanstack/react-query";
import { CustomAlert } from "./CustomAlert";

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
