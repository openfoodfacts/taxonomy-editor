import { Alert, AlertTitle } from "@mui/material";
import { SxProps } from "@mui/material";

interface CustomAlertProps {
  severity: "error" | "warning" | "info" | "success";
  title?: string;
  message: string;
  sx?: SxProps;
}

export const CustomAlert: React.FC<CustomAlertProps> = ({
  severity,
  title,
  message,
  sx,
}) => {
  return (
    <Alert severity={severity} sx={sx}>
      {title && <AlertTitle>{title}</AlertTitle>}
      {message}
    </Alert>
  );
};
