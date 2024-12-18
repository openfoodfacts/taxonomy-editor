import { useState, useRef, useMemo } from "react";
import { Link, useParams, Params, useNavigate } from "react-router-dom";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Menu from "@mui/material/Menu";
import MenuIcon from "@mui/icons-material/Menu";
import Container from "@mui/material/Container";
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import ListSubheader from "@mui/material/ListSubheader";
import MuiLink from "@mui/material/Link";
import SettingsIcon from "@mui/icons-material/Settings";
import { useTranslation } from "react-i18next";
import logoUrl from "@/assets/logosmall.jpg";
import { useAppContext } from "./UseContext";

const getDisplayedPages = (
  params: Params<string>,
): Array<{ translationKey: string; url: string }> => {
  if (!params.taxonomyName || !params.branchName) {
    return [];
  }

  const navUrlPrefix = `${params.taxonomyName}/${params.branchName}/`;
  return [
    { url: navUrlPrefix + "search", translationKey: "Search" },
    { url: navUrlPrefix + "export", translationKey: "Export" },
    { url: navUrlPrefix + "errors", translationKey: "Errors" },
  ];
};

export const ResponsiveAppBar = () => {
  const params = useParams();
  const displayedPages = useMemo(() => getDisplayedPages(params), [params]);
  const { t } = useTranslation();
  const menuAnchorRef = useRef(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  const { taxonomyName, ownerName, description, clearContext } =
    useAppContext();

  const handleCloseNavMenu = () => {
    setIsMenuOpen(false);
  };

  const handleNavigation = (url: string) => {
    if (taxonomyName || ownerName || description) {
      const confirmLeave = window.confirm(
        "You have unsaved changes. Are you sure you want to leave?",
      );
      if (!confirmLeave) return; // Don't navigate if user cancels
      clearContext(); // Call the clearContext function to clear the form
    }
    navigate(url); // Proceed with the navigation
    handleCloseNavMenu(); // Close the menu
  };

  return (
    <AppBar position="sticky" sx={{ color: "#000", background: "#f2e9e4" }}>
      <Container maxWidth={false}>
        <Toolbar disableGutters>
          {/* Mobile content */}
          <Box
            sx={{ flexGrow: 1, display: { xs: "flex", md: "none" } }}
            ref={menuAnchorRef}
          >
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={() => setIsMenuOpen(true)}
              color="inherit"
            >
              <MenuIcon />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={menuAnchorRef.current}
              anchorOrigin={{
                vertical: "bottom",
                horizontal: "left",
              }}
              keepMounted
              transformOrigin={{
                vertical: "top",
                horizontal: "left",
              }}
              open={isMenuOpen}
              onClose={handleCloseNavMenu}
              sx={{
                display: { xs: "block", md: "none" },
              }}
            >
              {displayedPages.map((page) =>
                page.url ? (
                  <MenuItem
                    key={page.translationKey}
                    onClick={() => handleNavigation(`/${page.url}`)} // Use handleNavigation
                    component={Link}
                    to={`/${page.url}`}
                  >
                    <Typography textAlign="center">
                      {t(page.translationKey)}
                    </Typography>
                  </MenuItem>
                ) : (
                  <ListSubheader key={page.translationKey}>
                    {t(page.translationKey)}
                  </ListSubheader>
                ),
              )}
            </Menu>
          </Box>

          {/* Desktop content */}
          <Box
            sx={{
              display: { xs: "none", md: "flex" },
              flexDirection: "row",
              alignItems: "center",
              width: "100%",
              justifyContent: "space-between",
            }}
          >
            <Box
              sx={{
                display: { xs: "none", md: "flex" },
                flexDirection: "row",
                alignItems: "baseline",
              }}
            >
              <MuiLink
                sx={{ mr: 2, display: "flex", alignSelf: "center" }}
                component="a"
                href="/"
                onClick={(event) => {
                  event.preventDefault();
                  handleNavigation("/");
                }}
                rel="noopener"
              >
                <img
                  src={logoUrl}
                  width="50px"
                  height="50px"
                  alt="OpenFoodFacts logo"
                />
              </MuiLink>
              <Typography
                variant="h6"
                noWrap
                component="a" // Change to "a" for handling clicks with an `onClick` event
                href="/" // Set href to "/" for the homepage
                onClick={(event) => {
                  // Prevent the default navigation behavior
                  event.preventDefault();

                  // Call the handleNavigation to check for unsaved changes and navigate
                  handleNavigation("/"); // Navigate to homepage if no unsaved changes
                }}
                sx={{
                  mr: 2,
                  display: "flex",
                  alignSelf: "center",
                  fontFamily: "Plus Jakarta Sans",
                  fontWeight: 1000,
                  letterSpacing: ".1rem",
                  color: "inherit",
                  textDecoration: "none",
                  cursor: "pointer", // Add pointer cursor for better UX
                }}
              >
                Taxonomy Editor
              </Typography>

              {displayedPages.map((page) => (
                <Button
                  color="inherit"
                  key={page.url}
                  onClick={() => handleNavigation(`/${page.url}`)} // Use handleNavigation
                  sx={{
                    fontFamily: "Plus Jakarta Sans",
                    my: 2,
                    textTransform: "none",
                  }}
                  component={Link}
                  to={`/${page.url}`}
                >
                  {page.url === "settings" ? (
                    <SettingsIcon />
                  ) : (
                    t(page.translationKey)
                  )}
                </Button>
              ))}
            </Box>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};
