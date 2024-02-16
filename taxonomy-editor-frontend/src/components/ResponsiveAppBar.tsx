import { useState, useRef } from "react";
import { Link } from "react-router-dom";

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

type ResponsiveAppBarProps = {
  displayedPages: Array<{ translationKey: string; url: string }>;
};

const ResponsiveAppBar = ({ displayedPages }: ResponsiveAppBarProps) => {
  const { t } = useTranslation();
  const menuAnchorRef = useRef();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleCloseNavMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <AppBar position="sticky" sx={{ textColor: "#000", background: "#f2e9e4" }}>
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
                    onClick={handleCloseNavMenu}
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
                )
              )}
            </Menu>
          </Box>
          <Typography
            variant="h5"
            noWrap
            component="a"
            href=""
            sx={{
              mr: 2,
              display: { xs: "flex", md: "none" },
              flexGrow: 1,
              fontFamily: "Plus Jakarta Sans",
              fontWeight: 700,
              letterSpacing: ".1rem",
              color: "inherit",
              textDecoration: "none",
            }}
          >
            Taxonomy Editor
          </Typography>

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
                href="https://ui.taxonomy.openfoodfacts.net/"
                target="_blank"
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
                component={Link}
                to="/"
                sx={{
                  mr: 2,
                  display: "flex",
                  alignSelf: "center",
                  fontFamily: "Plus Jakarta Sans",
                  fontWeight: 1000,
                  letterSpacing: ".1rem",
                  color: "inherit",
                  textDecoration: "none",
                }}
              >
                Taxonomy Editor
              </Typography>

              {displayedPages.map((page) => (
                <Button
                  color="inherit"
                  key={page.url}
                  onClick={handleCloseNavMenu}
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

export default ResponsiveAppBar;
