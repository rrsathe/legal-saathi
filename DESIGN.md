---
version: alpha
name: Harvey
description: Harvey presents a restrained, editorial, law-firm-grade aesthetic. Warm near-black ink (#0F0E0D) sits on pure white, with a ladder of warm stone greys for secondary text, hairlines and muted surfaces. Dark charcoal panels and a near-black footer invert the palette for emphasis. Headlines use the HarveySerifFont serif at large display sizes with tight leading and slight negative tracking. Everything else runs on HarveySansFont at compact 14–24px sizes. Color accents are nearly absent; a rare electric yellow highlight (#F6F202) and blue focus rings are the only chromatic moments. Corners are modest (3–8px), with pill shapes reserved for select controls.
colors:
  primary: "#0F0E0D"
  on-primary: "#FFFFFF"
  ink: "#0F0E0D"
  ink-secondary: "#33312C"
  muted: "#706D66"
  muted-soft: "#8F8B85"
  surface: "#FFFFFF"
  surface-muted: "#F2F1F0"
  surface-dark: "#1F1D1A"
  surface-black: "#000000"
  hairline: "#CCCAC6"
  border-strong: "#ADABA5"
  border-dark: "#33312C"
  on-dark: "#FFFFFF"
  highlight: "#F6F202"
  focus-ring: "#99C8FF"
  focus-ring-strong: "#005FCC"
typography:
  hero-display:
    fontFamily: HarveySerifFont
    fontSize: 72px
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: -0.9px
  display-lg:
    fontFamily: HarveySerifFont
    fontSize: 48px
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: -0.48px
  display-md:
    fontFamily: HarveySerifFont
    fontSize: 32px
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: -0.32px
  display-sm:
    fontFamily: HarveySerifFont
    fontSize: 24px
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: -0.24px
  headline:
    fontFamily: HarveySansFont
    fontSize: 32px
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: -0.32px
  title-lg:
    fontFamily: HarveySansFont
    fontSize: 24px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: -0.24px
  title-md:
    fontFamily: HarveySansFont
    fontSize: 20px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: normal
  body-lg:
    fontFamily: HarveySansFont
    fontSize: 20px
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: normal
  button-lg:
    fontFamily: HarveySansFont
    fontSize: 20px
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: -0.24px
  body:
    fontFamily: HarveySansFont
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: normal
  body-tight:
    fontFamily: HarveySansFont
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: normal
  body-strong:
    fontFamily: HarveySansFont
    fontSize: 16px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: normal
  label:
    fontFamily: HarveySansFont
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: normal
  caption:
    fontFamily: HarveySansFont
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: normal
  list-item:
    fontFamily: HarveySansFont
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.45
    letterSpacing: normal
  nav-link:
    fontFamily: HarveySansFont
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: normal
rounded:
  xs: 3px
  sm: 4px
  md: 8px
  full: 9999px
spacing:
  section-padding-y: 64px
  footer-landing-column-gap: 16px
  footer-landing-gap: 16px
  footer-landing-inner-max-width: 1728px
  header-landing-mobile-gap: 10px
  header-landing-mobile-inner-max-width: 1920px
  footer-landing-mobile-column-gap: 28px
  footer-landing-mobile-gap: 14px
  footer-landing-mobile-inner-max-width: 1728px
  header-inner-gap: 4px
  header-inner-2-gap: 4px
  header-inner-2-inner-max-width: 1920px
  header-inner-2-mobile-gap: 10px
  header-inner-2-mobile-inner-max-width: 1920px
  header-inner-3-gap: 4px
  footer-inner-gap: 16px
  card-4-grid-gap: 16px
  card-4-grid-row-gap: 64px
  card-6-grid-gap: 128px
  card-7-grid-gap: 32px
  button-primary-padding-y: 7px
  button-primary-padding-left: 12px
  button-primary-padding-right: 7px
  button-secondary-padding-y: 20px
  button-secondary-padding-x: 20px
  input-padding-y: 20px
  input-padding-left: 20px
  input-padding-right: 40px
  button-ghost-3-padding-y: 8px
  button-ghost-3-padding-x: 8px
  button-primary-2-padding-x: 20px
  input-2-padding-x: 16px
  select-padding-left: 16px
  select-padding-right: 40px
  select-2-padding-left: 16px
  select-2-padding-right: 40px
components:
  button-ghost:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    height: 72px
  button-ghost-label:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  button-ghost-icon:
    size: 16px
  card:
    textColor: "#0F0E0D"
    height: 96px
  card-link:
    textColor: "#0F0E0D"
    padding: 8px
    height: 96px
    width: 229px
  card-media:
    height: 58px
    width: 82px
  hero:
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
  hero-group:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  hero-title:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 72px
      fontWeight: 400
      lineHeight: 75.6px
      letterSpacing: -0.9px
  navigation:
    textColor: "#0F0E0D"
    height: 72px
  navigation-button:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    height: 72px
    width: 74px
  navigation-link:
    textColor: "#0F0E0D"
    height: 72px
    width: 69px
  navigation-2:
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 394px
  navigation-2-title:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
      letterSpacing: -0.14px
  navigation-2-link:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  close-button:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    padding: 8px
    height: 32px
  close-button-icon:
    size: 16px
  header-landing:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 106px
  header-landing-group:
    backgroundColor: "#0F0E0D99"
  header-landing-group-3:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  header-landing-logo:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 400
      lineHeight: 18.2px
  header-landing-logo-text-2:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-landing-menu-toggle:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    padding: 8px
    size: 32px
  header-landing-menu-toggle-icon:
    size: 16px
  header-landing-text:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 28px
      fontWeight: 400
      lineHeight: 39.2px
  header-landing-cta:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    height: 72px
  header-landing-nav-link:
    textColor: "#FAFAF9"
    height: 72px
    width: 69px
  header-landing-menu-toggle-2:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    height: 72px
    width: 80px
  header-landing-menu-toggle-3:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    rounded: 4px
    height: 32px
    width: 78px
  header-landing-cta-2:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
    rounded: 4px
  header-landing-text-2:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 14px
  header-landing-menu-toggle-3-hover:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  header-landing-menu-toggle-3-focus:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  header-landing-cta-2-hover:
    backgroundColor: "#8F8B85"
  footer-landing:
    backgroundColor: "#0F0E0D"
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 699px
  footer-landing-heading:
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 24px
      fontWeight: 400
      lineHeight: 25.2px
      letterSpacing: -0.24px
  footer-landing-link:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
    rounded: 4px
  footer-landing-text:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 500
      lineHeight: 16px
  footer-landing-logo:
    height: 32px
    width: 45px
  footer-landing-inner-2:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 400
      lineHeight: 18.2px
  footer-landing-heading-2:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
      letterSpacing: -0.14px
  footer-landing-nav-link:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  footer-landing-nav-link-icon:
    size: 24px
  footer-landing-link-hover:
    backgroundColor: "#8F8B85"
  footer-landing-nav-link-hover:
    textColor: "#CCCAC6"
  header-landing-mobile:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 106px
  header-landing-mobile-group:
    backgroundColor: "#FAFAF9B8"
  header-landing-mobile-group-3:
    backgroundColor: "#0F0E0D"
    textColor: "#FAFAF9"
  header-landing-mobile-logo:
    textColor: "#FAFAF9"
  header-landing-mobile-logo-text:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-landing-mobile-text:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 28px
      fontWeight: 400
      lineHeight: 39.2px
  header-landing-mobile-menu-toggle:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    height: 25px
    width: 24px
  header-landing-mobile-menu-toggle-icon:
    height: 25px
    width: 24px
  footer-landing-mobile:
    backgroundColor: "#0F0E0D"
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 1435px
  footer-landing-mobile-heading:
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 24px
      fontWeight: 400
      lineHeight: 25.2px
      letterSpacing: -0.24px
  footer-landing-mobile-link:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
    rounded: 4px
  footer-landing-mobile-text:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 500
      lineHeight: 16px
  footer-landing-mobile-logo:
    height: 32px
    width: 45px
  footer-landing-mobile-heading-2:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
      letterSpacing: -0.14px
  footer-landing-mobile-nav-link:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  footer-landing-mobile-nav-link-icon:
    size: 24px
  footer-landing-mobile-inner-2:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 400
      lineHeight: 18.2px
  footer-landing-mobile-nav-link-hover:
    textColor: "#CCCAC6"
  card-2:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 330px
  card-2-group:
    rounded: 4px
  card-2-media:
    height: 252px
    width: 448px
  card-2-text:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 24px
      fontWeight: 500
      lineHeight: 31.2px
      letterSpacing: -0.24px
  footer-link-column:
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 394px
  footer-link-column-title:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
      letterSpacing: -0.14px
  footer-link-column-link:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  announcement-banner:
    textColor: "#0F0E0D"
    height: 106px
  announcement-banner-group:
    backgroundColor: "#FAFAF9B8"
  announcement-banner-group-3:
    backgroundColor: "#0F0E0D"
    textColor: "#FAFAF9"
  announcement-banner-button:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    padding: 8px
    size: 32px
  header-inner:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 72px
  header-inner-group:
    backgroundColor: "#0F0E0D"
  header-inner-cta:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    height: 72px
  header-inner-text:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-inner-icon:
    size: 16px
  header-inner-nav-link:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-inner-button:
    backgroundColor: transparent
    textColor: "#0F0E0D"
  button-primary:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    rounded: 4px
    height: 32px
  button-primary-label:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  button-primary-icon:
    size: 18px
  button-primary-hover:
    backgroundColor: "#0F0E0D"
    textColor: "#FAFAF9"
  button-primary-focus:
    backgroundColor: "#0F0E0D"
    textColor: "#FAFAF9"
  button-secondary:
    backgroundColor: transparent
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 20.8px
    rounded: 4px
    padding: 20px
    height: 63px
  button-secondary-group:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 20.8px
  button-secondary-icon:
    size: 16px
  button-secondary-hover:
    textColor: "#FAFAF9"
  button-ghost-2:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    height: 72px
  button-ghost-2-label:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  button-ghost-2-icon:
    size: 16px
  input:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 20.8px
    rounded: 4px
    height: 63px
    width: 298px
  card-3:
    backgroundColor: "#0F0E0D"
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    rounded: 8px
    height: 448px
  card-3-media:
    size: 448px
  card-3-media-2:
    height: 57px
    width: 120px
  card-3-group-7:
    padding: 32px
  card-3-title:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 20px
      fontWeight: 400
      lineHeight: 26px
      letterSpacing: -0.2px
  card-4:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
  card-4-group:
    rounded: 4px
  card-4-group-2:
    backgroundColor: "#1F1D1A"
  card-4-media:
    rounded: 4px
    height: 100px
    width: 84px
  card-4-body:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 24px
      fontWeight: 500
      lineHeight: 31.2px
  card-5:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
  card-5-body:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 20px
      fontWeight: 400
      lineHeight: 26px
  card-5-body-2:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 72px
      fontWeight: 400
      lineHeight: 75.6px
      letterSpacing: -0.9px
  play-button:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    height: 448px
  logo-carousel:
    textColor: "#0F0E0D"
    height: 60px
  logo-carousel-media:
    height: 60px
    width: 93px
  pagination:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 27px
  pagination-link:
    textColor: "#33312C"
    size: 20px
  pagination-icon:
    size: 20px
  pagination-link-active:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 20px
      fontWeight: 400
      lineHeight: 26px
  pagination-link-2:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 20px
      fontWeight: 400
      lineHeight: 26px
  pagination-icon-2:
    size: 20px
  announcement-banner-2:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    padding: 8px
    height: 32px
  announcement-banner-2-icon:
    size: 16px
  header-inner-2:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 106px
  header-inner-2-group:
    backgroundColor: "#0F0E0D99"
  header-inner-2-group-3:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  header-inner-2-logo:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 400
      lineHeight: 18.2px
  header-inner-2-logo-text-2:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-inner-2-menu-toggle:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    padding: 8px
    size: 32px
  header-inner-2-menu-toggle-icon:
    size: 16px
  header-inner-2-text:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 28px
      fontWeight: 400
      lineHeight: 39.2px
  header-inner-2-cta:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    height: 72px
  header-inner-2-nav-link:
    textColor: "#FAFAF9"
    height: 72px
    width: 69px
  header-inner-2-menu-toggle-2:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    height: 72px
    width: 80px
  header-inner-2-cta-2:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    rounded: 4px
    height: 32px
  header-inner-2-cta-3:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
    rounded: 4px
  header-inner-2-text-2:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 14px
  header-inner-2-cta-2-hover:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  header-inner-2-cta-2-focus:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  header-inner-2-cta-3-hover:
    backgroundColor: "#8F8B85"
  header-inner-2-mobile:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 106px
  header-inner-2-mobile-group:
    backgroundColor: "#FAFAF9B8"
  header-inner-2-mobile-group-3:
    backgroundColor: "#0F0E0D"
    textColor: "#FAFAF9"
  header-inner-2-mobile-logo:
    textColor: "#FAFAF9"
  header-inner-2-mobile-logo-text:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-inner-2-mobile-text:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 28px
      fontWeight: 400
      lineHeight: 39.2px
  header-inner-2-mobile-menu-toggle:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    height: 25px
    width: 24px
  header-inner-2-mobile-menu-toggle-icon:
    height: 25px
    width: 24px
  button-secondary-2:
    backgroundColor: "#FAFAF933"
    textColor: "#0F0E0D"
    height: 72px
  button-secondary-2-icon:
    height: 25px
    width: 24px
  button-ghost-3:
    backgroundColor: transparent
    textColor: "#FAFAF9"
    padding: 8px
    height: 32px
  button-ghost-3-icon:
    size: 16px
  card-6:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 675px
  card-6-title:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 32px
      fontWeight: 500
      lineHeight: 35.2px
      letterSpacing: -0.32px
  card-6-body:
    textColor: "#33312C"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 20px
      fontWeight: 500
      lineHeight: 26px
  card-6-group-4:
    rounded: 8px
  card-6-media:
    height: 516px
    width: 688px
  card-6-media-2:
    height: 516px
    width: 688px
  card-6-title-2:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 500
      lineHeight: 20.8px
      letterSpacing: -0.16px
  card-6-body-2:
    textColor: "#33312C"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 20.8px
  card-7:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
  card-7-title:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 500
      lineHeight: 20.8px
      letterSpacing: -0.16px
  card-7-body:
    textColor: "#33312C"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 20.8px
  video-player:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    height: 774px
  video-player-group:
    rounded: 8px
  link-list:
    textColor: "#FFFFFF"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 394px
  link-list-title:
    textColor: "#8F8B85"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
      letterSpacing: -0.14px
  link-list-link:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  banner:
    textColor: "#FAFAF9"
    height: 106px
  banner-group:
    backgroundColor: "#0F0E0D99"
  banner-group-3:
    backgroundColor: "#FAFAF9"
    textColor: "#0F0E0D"
  banner-button:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    padding: 8px
    size: 32px
  breadcrumb:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 21px
  breadcrumb-item:
    textColor: "#706D66"
  breadcrumb-link:
    textColor: "#706D66"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 500
      lineHeight: 20.8px
  breadcrumb-text-active:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 500
      lineHeight: 20.8px
  header-inner-3:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    height: 72px
  header-inner-3-cta:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 20px
    height: 72px
  header-inner-3-text:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-inner-3-icon:
    size: 16px
  header-inner-3-nav-link:
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  header-inner-3-button:
    backgroundColor: transparent
    textColor: "#FAFAF9"
  button-primary-2:
    backgroundColor: "#0F0E0D"
    textColor: "#FAFAF9"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 500
      lineHeight: 24px
    rounded: 4px
    height: 48px
  button-primary-2-hover:
    backgroundColor: "#33312C"
  input-2:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    rounded: 4px
    height: 48px
    width: 352px
  select:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    rounded: 4px
    height: 48px
    width: 736px
  select-2:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    rounded: 4px
    height: 48px
    width: 352px
  form-field-group:
    textColor: "#333333"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 13px
      fontWeight: 400
      lineHeight: 19.5px
    height: 93px
  form-field-group-group-3:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 20.8px
  form-field-group-text:
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 20.8px
  form-field-group-field:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 24px
    rounded: 4px
  logo-item:
    textColor: "#FFFFFF"
    height: 60px
  logo-item-media:
    height: 60px
    width: 93px
  checkbox:
    backgroundColor: transparent
    textColor: "#0F0E0D"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 16px
      fontWeight: 400
      lineHeight: 19.2px
    rounded: 4px
    height: 20px
    width: 20px
  footer-inner:
    backgroundColor: "#FAFAF9"
    textColor: "#706D66"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 400
      lineHeight: 18.2px
    padding: 32px
    height: 82px
  footer-inner-link:
    textColor: "#706D66"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  footer-inner-text:
    textColor: "#706D66"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  footer-inner-link-hover:
    textColor: "#0F0E0D"
  footer-inner-mobile:
    backgroundColor: "#FAFAF9"
    textColor: "#706D66"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 400
      lineHeight: 18.2px
    padding: 28px
    height: 74px
  footer-inner-mobile-link:
    textColor: "#706D66"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  footer-inner-mobile-text:
    textColor: "#706D66"
    typography:
      fontFamily: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif
      fontSize: 14px
      fontWeight: 500
      lineHeight: 18.2px
  footer-inner-mobile-link-hover:
    textColor: "#0F0E0D"
---

# Harvey

## Overview

Harvey reads like a law firm's letterhead rebuilt as software. The palette is almost entirely warm monochrome: **Ink** (`ink`, #0F0E0D) on **Paper** (`surface`, #FFFFFF), with a ladder of stone greys for secondary text and rules. Large `HarveySerifFont` headlines at weight 400 carry the editorial voice. Every functional surface (nav, buttons, forms, cards, footer) runs on `HarveySansFont` at compact 14–24px sizes. The register is calm and expensive. The site never raises its voice with color.

Density is low and the rhythm is airy. Sections breathe on a 64px vertical cadence (`section-padding-y`) and alternate between off-white bands and near-black bands (customer stories, CTA, footer). Hierarchy comes from three moves:

- **Typeface switch.** Serif means statement, sans means interface.
- **Size jump.** The display ladder leaps from 24px to 72px.
- **Tonal inversion.** A whole band flips to ink.

Weight does almost no work. Only 400 and 500 exist.

Chromatic accent is close to nonexistent. **Highlighter Yellow** (`highlight`, #F6F202) appears as a rare small mark. Blue exists only as focus-ring tokens. Depth comes from tonal contrast, hairline rules, frosted translucent headers and a single soft shadow tier. Corners stay small (4px on controls, 8px on media cards), so the geometry feels architectural rather than friendly.

**Key Characteristics:**
- Serif display (`hero-display` 72px, weight 400, -0.9px tracking) over a sans UI layer. Two families, never three.
- Warm near-black **Ink** (`primary`, #0F0E0D) serves as both text color and inverted-band fill. There is no brand hue.
- Only weights 400 and 500. Serif is always 400; 500 is the sans emphasis cut.
- Full-width off-white and near-black bands replace cards-with-shadows as the main structuring device.
- Frosted headers: translucent fills with `blur(16px)` backdrop on `header-landing`, `header-inner-2`, `announcement-banner` and their mobile variants.
- Small-radius rectilinear controls: `rounded.sm` (4px) on buttons, inputs, selects and checkboxes.
- Hairline rules in **Stone Rule** (`hairline`, #CCCAC6) separate stats rows and feature lists. A dark rule (`border-dark`, #33312C) separates footer zones.
- Low density, generous whitespace, 64px section rhythm.

## Colors

A warm-neutral, near-monochrome palette. Every grey leans slightly brown so the white canvas never feels clinical. There are no gradients anywhere in the system; fills are always flat.

### Brand & Ink
- **Ink** (`primary` / `ink`, #0F0E0D): the brand color. It is used for body and heading text, the solid fill of `button-primary-2`, the hover fill of `button-primary`, the dark footer (`footer-landing` background) and inverted bands. Use it in place of pure black for type.
- **On Ink** (`on-primary` / `on-dark`, #FFFFFF): text on Ink fills and dark bands, for example the `footer-landing` root text and `footer-landing-heading`.
- **Highlighter Yellow** (`highlight`, #F6F202): the only saturated brand-adjacent hue. It appears as small surface marks on 4 pages. Treat it as a highlighter stroke, never as a button or band fill.

### Surfaces
- **Paper** (`surface`, #FFFFFF): the default page canvas.
- **Linen** (`surface-muted`, #F2F1F0): a quiet muted panel for low-emphasis blocks.
- **Charcoal Tile** (`surface-dark`, #1F1D1A): raised tiles inside dark sections, for example the `card-4-group-2` fill. It sits one step lighter than Ink, so cards lift through tone alone.
- **True Black** (`surface-black`, #000000): media and video backdrops only. Never use it for text.
- Components also use a warm off-white, #FAFAF9. It appears as the `card-6` and `hero-group` background, as `footer-landing-nav-link` text, and as the `header-landing-cta-2` / `footer-landing-link` pill fill. It is not a token; map it to `surface` when rebuilding unless exact parity matters.

### Text
- **Ink** (`ink`, #0F0E0D): primary copy.
- **Graphite** (`ink-secondary`, #33312C): secondary paragraph copy, for example `card-6-body` and `card-7-body`.
- **Stone** (`muted`, #706D66): tertiary text such as breadcrumbs (`breadcrumb-link`) and the light legal footer (`footer-inner`).
- **Pebble** (`muted-soft`, #8F8B85): eyebrow titles on dark (`footer-landing-heading-2`, `link-list-title`), inactive pagination (`pagination-link-2`) and `button-secondary` label text. It doubles as the hover fill of `footer-landing-link` and the focus-ring color in `button-primary-2`.

### Hairlines & Borders
- **Stone Rule** (`hairline`, #CCCAC6): 1px top rules on `card-6-group` and `card-7`, and a 2px top rule on `card-5`. It is also the hover text color of `footer-landing-nav-link`.
- **Field Border** (`border-strong`, #ADABA5): resting 1px border on `input-2`, `select`, `select-2`, `checkbox` and `form-field-group-field`. On hover and focus it darkens to Ink.
- **Dark Rule** (`border-dark`, #33312C): borders on dark surfaces, including `footer-landing-columns` bottom rule, `button-secondary` outline and the `input` outline in the dark newsletter field.

### Component & State Colors
These were measured on components and states, never in page sampling:
- **Focus Halo** (`focus-ring`, #99C8FF): soft blue focus ring.
- **Focus Blue** (`focus-ring-strong`, #005FCC): high-contrast focus ring.

Use them only for keyboard focus. Visible focus treatments on most recipes are instead grey rings built from Paper and Pebble.

## Typography

### Font Family
- **HarveySerifFont** (proprietary serif): the display voice. It is used for hero headlines, section titles, the big stats numerals in `card-5`, the `footer-landing-heading` and the 28px statement text in headers (`header-inner-2-text`). It is always weight 400.
- **HarveySansFont** (proprietary grotesque): everything else, including nav, buttons, body, labels, forms, cards and footer. The declared fallback stack is -apple-system, system-ui, Segoe UI, Roboto and Helvetica Neue.

### Hierarchy
| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `hero-display` | 72px | 400 | 1.05 | -0.9px | Serif H1 hero headline, big stat numerals |
| `display-lg` | 48px | 400 | 1.05 | -0.48px | Serif page and section H1/H2 |
| `display-md` | 32px | 400 | 1.05 | -0.32px | Serif H2/H3, blockquotes |
| `display-sm` | 24px | 400 | 1.05 | -0.24px | Serif H3, footer statement heading |
| `headline` | 32px | 500 | 1.1 | -0.32px | Sans feature titles (`card-6-title`) |
| `title-lg` | 24px | 500 | 1.3 | -0.24px | Sans card titles (`card-2-text`, `card-4-body`) |
| `title-md` | 20px | 500 | 1.3 | normal | Emphasized lead lines |
| `body-lg` | 20px | 400 | 1.3 | normal | Lead paragraphs, card descriptions, active pagination |
| `button-lg` | 20px | 400 | 1.05 | -0.24px | Large text buttons / spans |
| `body` | 16px | 400 | 1.5 | normal | Default running text, inputs, links |
| `body-tight` | 16px | 400 | 1.3 | normal | Labels, compact paragraphs, secondary button text |
| `body-strong` | 16px | 500 | 1.3 | normal | Small headings (`card-7-title`), breadcrumbs |
| `label` | 14px | 500 | 1.3 | normal | Nav labels, eyebrow titles, footer links |
| `caption` | 14px | 400 | 1.3 | normal | Captions, legal text, meta |
| `list-item` | 14px | 500 | 1.45 | normal | List rows and list buttons |
| `nav-link` | 14px | 500 | 1 | normal | Single-line nav links |

### Principles
- **Two weights only.** 400 and 500. Weight 600+ is deliberately absent; emphasis comes from switching to the serif or scaling up, not from bolding.
- **The serif never goes bold.** Every `display-*` token is 400. The `headline` and `title-*` tokens are the sans at 500 for UI-ish headings.
- **Tracking scales with size.** Display sizes tighten at roughly -1% of font size (-0.24px at 24px, -0.32px at 32px, -0.48px at 48px). The hero tightens a little further to -0.9px at 72px. Sans text at 20px and below uses normal tracking, except the eyebrow titles, which carry -0.14px (`footer-landing-heading-2`).
- **Leading tightens as size grows.** Serif display is set solid at 1.05. Sans headings sit at 1.1–1.3. Only long-form `body` opens to 1.5.
- **Compact UI scale.** Interface type lives at 14–16px. The 20px and 24px sizes are for leads and card titles, not controls.

### Note on Font Substitutes
Both families are proprietary.

- **Serif substitute: Source Serif 4 or Newsreader.** Use the regular (400) optical display cut. Keep the 1.05 line height and the negative tracking from the tokens; if the substitute runs wider, tighten an extra -0.01em at 48px and above.
- **Sans substitute: Inter.** Use 400 and 500 only. Inter's x-height is generous, so consider dropping body sizes visually by about 0.5px or keeping line heights as tokenized. Avoid Inter's 600 even if it is tempting for headings.

## Layout

### Spacing System
No single `base` step was tokenized. The measured values cluster on a 4/8-multiple rhythm with a few component-specific exceptions.

| Token | Value | Measured on |
|---|---|---|
| `section-padding-y` | 64px | Vertical padding between the page's sections, measured on the page itself rather than a component |
| `header-inner-gap` / `header-inner-2-gap` / `header-inner-3-gap` | 4px | Gap between desktop nav items |
| `header-landing-mobile-gap` / `header-inner-2-mobile-gap` | 10px | Gap in the mobile header logo row |
| `footer-landing-gap` | 16px | Stack gap in the footer logo column |
| `footer-landing-column-gap` | 16px | Column gap of the desktop footer link grid |
| `footer-landing-mobile-column-gap` | 28px | Column gap of the mobile footer link grid |
| `footer-landing-mobile-gap` | 14px | Stack gap inside mobile footer link groups |
| `footer-inner-gap` | 16px | Gap in the light legal footer bar |
| `button-primary-padding-y` | 7px | `button-primary` vertical padding |
| `button-primary-padding-left` / `button-primary-padding-right` | 12px / 7px | `button-primary` asymmetric padding (label left, icon right) |
| `button-primary-2-padding-x` | 20px | Solid Ink button horizontal padding |
| `button-secondary-padding-y` / `button-secondary-padding-x` | 20px / 20px | Outlined dark button |
| `button-ghost-3-padding-y` / `button-ghost-3-padding-x` | 8px / 8px | Icon-only ghost button |
| `input-padding-y` / `input-padding-left` / `input-padding-right` | 20px / 20px / 40px | Dark newsletter input (right side reserves room for the submit icon) |
| `input-2-padding-x` | 16px | Light form input |
| `select-padding-left` / `select-padding-right` | 16px / 40px | Select, right side reserves the chevron |
| `select-2-padding-left` / `select-2-padding-right` | 16px / 40px | Half-width select |

### Grid & Container
- **Containers.** The header inner row is capped at 1920px (`header-inner-2-inner-max-width`, `header-landing-mobile-inner-max-width`). The footer content is capped at 1728px (`footer-landing-inner-max-width`). The layout is effectively full-bleed with side gutters, not a narrow centered column.
- **Grid gaps.**
  - Dark case-study tiles sit 16px apart horizontally (`card-4-grid-gap`) and 64px apart vertically (`card-4-grid-row-gap`).
  - Alternating text/media feature rows stack with 128px between them (`card-6-grid-gap`).
  - Feature list items stack with 32px between them (`card-7-grid-gap`).
- **Column patterns from the screenshots.** A two-column hero split places the serif headline left and subcopy plus CTA right. Logo walls run as wide wordmark rows. Article and case-study cards form multi-column rows. Feature blocks split text against media. Stats render as label-left, numeral-right rows divided by hairlines. Article pages narrow to a centered reading column.

### Whitespace Philosophy
Whitespace is the luxury signal. Sections are separated by 64px (`section-padding-y`) plus a band-color change, so content never crowds a transition. Feature rows get very wide separation (`card-6-grid-gap`). Within components, spacing stays tight and functional: 4px between nav items, 16px between cards. The contrast between generous macro-space and compact micro-space is the system. Don't fill empty space with decoration; let a single serif headline own a band.

### Measured Layout

Every spacing token restates a measurement of a verified component recipe, or the step those measurements share. `section-padding-y` is measured directly on the page sections and feeds no step.

- `section-padding-y`: 64px (vertical padding repeated on the page sections: 3 section edges on 1 page)
- `footer-landing-column-gap`: 16px (`footer-landing`, column gap of the `footer-landing-nav` grid)
- `footer-landing-gap`: 16px (`footer-landing`, gap of `footer-landing-group-2`)
- `footer-landing-inner-max-width`: 1728px (`footer-landing`, max width of `footer-landing-inner`)
- `header-landing-mobile-gap`: 10px (`header-landing-mobile`, gap of `header-landing-mobile-group-7`)
- `header-landing-mobile-inner-max-width`: 1920px (`header-landing-mobile`, max width of `header-landing-mobile-inner`)
- `footer-landing-mobile-column-gap`: 28px (`footer-landing-mobile`, column gap of the `footer-landing-mobile-nav` grid)
- `footer-landing-mobile-gap`: 14px (`footer-landing-mobile`, gap of `footer-landing-mobile-group-4`)
- `footer-landing-mobile-inner-max-width`: 1728px (`footer-landing-mobile`, max width of `footer-landing-mobile-inner`)
- `header-inner-gap`: 4px (`header-inner`, gap of `header-inner-nav-item`)
- `header-inner-2-gap`: 4px (`header-inner-2`, gap of `header-inner-2-nav-item`)
- `header-inner-2-inner-max-width`: 1920px (`header-inner-2`, max width of `header-inner-2-inner`)
- `header-inner-2-mobile-gap`: 10px (`header-inner-2-mobile`, gap of `header-inner-2-mobile-group-7`)
- `header-inner-2-mobile-inner-max-width`: 1920px (`header-inner-2-mobile`, max width of `header-inner-2-mobile-inner`)
- `header-inner-3-gap`: 4px (`header-inner-3`, gap of `header-inner-3-nav-item`)
- `footer-inner-gap`: 16px (`footer-inner`, gap of `footer-inner`)
- `card-4-grid-gap`: 16px (`card-4`, column gap of the grid its instances sit in)
- `card-4-grid-row-gap`: 64px (`card-4`, row gap of the grid its instances sit in)
- `card-6-grid-gap`: 128px (`card-6`, column gap of the grid its instances sit in)
- `card-7-grid-gap`: 32px (`card-7`, column gap of the grid its instances sit in)
- `button-primary-padding-y`: 7px (`button-primary`, vertical padding of the root)
- `button-primary-padding-left`: 12px (`button-primary`, left padding of the root)
- `button-primary-padding-right`: 7px (`button-primary`, right padding of the root)
- `button-secondary-padding-y`: 20px (`button-secondary`, vertical padding of the root)
- `button-secondary-padding-x`: 20px (`button-secondary`, horizontal padding of the root)
- `input-padding-y`: 20px (`input`, vertical padding of the root)
- `input-padding-left`: 20px (`input`, left padding of the root)
- `input-padding-right`: 40px (`input`, right padding of the root)
- `button-ghost-3-padding-y`: 8px (`button-ghost-3`, vertical padding of the root)
- `button-ghost-3-padding-x`: 8px (`button-ghost-3`, horizontal padding of the root)
- `button-primary-2-padding-x`: 20px (`button-primary-2`, horizontal padding of the root)
- `input-2-padding-x`: 16px (`input-2`, horizontal padding of the root)
- `select-padding-left`: 16px (`select`, left padding of the root)
- `select-padding-right`: 40px (`select`, right padding of the root)
- `select-2-padding-left`: 16px (`select-2`, left padding of the root)
- `select-2-padding-right`: 40px (`select-2`, right padding of the root)

The card grid lays out in 6 columns; the footer in 11 columns; the card-4 grid in 3 columns at desktop.
The footer lays out in 5 columns at mobile.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| 0 · Base surface | No outline; depth from tonal banding: **Paper** (`surface`, #FFFFFF) or the warm off-white #FAFAF9 on `card-6` and `footer-inner`, against **Ink** (`primary`, #0F0E0D) on `footer-landing` and `card-3` | Default page sections; dark bands for stories, CTA and footer |
| 1 · Tonal tile | **Charcoal** (`surface-dark`, #1F1D1A) fill on `card-4-group-2`, sitting on a near-black band | Cards inside dark sections lift by being lighter, not by casting |
| 2 · Hairline | `border-top: 1px solid #CCCAC6` (`hairline`) on `card-6-group`, `card-6-group-6`, `card-7`; `2px solid #CCCAC6` on `card-5` (flagged: the `card-5-group` y did not reproduce the measured 43px); `border-bottom: 1px solid #33312C` (`border-dark`) on `footer-landing-columns` | Stat rows, feature lists, footer column divider |
| 3 · Control outline | `1px solid #ADABA5` (`border-strong`) on `input-2`, `select`, `select-2`, `checkbox`, darkening to `1px solid #0F0E0D` on hover/focus; `1px solid #0F0E0D` on `button-primary`; `1px solid #33312C` on `button-secondary` and `input` (focus `1px solid #FAFAF9`) | Form fields and outlined buttons |
| 4 · Frosted glass | `backdrop-filter: blur(16px)` over translucent fills #0F0E0D99 or #FAFAF9B8 on `header-inner-2-group`, `announcement-banner-group`, `header-landing-mobile-group`, `header-inner-2-mobile-group`; `blur(6px)` with fill #FAFAF933 and `1px solid #FAFAF94D` on `button-secondary-2` | Fixed header bar and announcement strip; glass control over media |
| 5 · Floating shadow | `box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.1) 0px 4px 6px -4px` | Truly floating overlays such as the white cookie modal card |
| Focus ring | `box-shadow: … #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px …` on `header-inner-2-cta-3` and `footer-landing-link`; `#8F8B85 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px` on `button-primary-2` | Keyboard focus, drawn as a spread ring in **Stone** (`muted-soft`, #8F8B85), never a blur |

**Shadow philosophy.** Harvey builds depth in layers of restraint. Most hierarchy comes from tonal contrast (off-white sections against Ink bands, Charcoal tiles on black) and from warm hairlines that rule off rows rather than box them. Glass is the signature move for chrome: the fixed header and announcement strip use `blur(16px)` over a semi-transparent Ink or off-white fill, and the glass button over media uses a lighter `blur(6px)`. Keep that frosting; never swap it for an opaque bar. A real cast shadow belongs to the system as its top tier: a soft, low-opacity two-layer drop (`0px 10px 15px -3px` plus `0px 4px 6px -4px`, both at `rgba(0, 0, 0, 0.1)`), used on floating overlays like the cookie modal. Do not spread it onto cards, buttons or inputs. Those stay on tonal fills and 1px outlines. Focus is expressed with zero-blur spread rings via `box-shadow`, so focus states never read as elevation.

## Shapes

### Border Radius Scale
| Token | Value | Use |
|---|---|---|
| `rounded.xs` | 3px | Rare small details (measured on 4 pages, not on any recipe) |
| `rounded.sm` | 4px | The control radius: `button-primary`, `button-primary-2`, `button-secondary`, `input`, `input-2`, `select`, `select-2`, `checkbox`, `form-field-group-field`, the off-white header and footer CTAs (`header-landing-cta-2`, `footer-landing-link`), small card groups (`card-2-group`, `card-4-group`, `card-4-media`) |
| `rounded.md` | 8px | Large media and feature containers: `card-6-group-4`, `video-player-group`, and `card-3` (flagged: the render matched 8% of the original pixels, below the 96% required) |
| `rounded.full` | 9999px | Reserved for round controls, such as the frosted `button-secondary-2` media control; measured on 2 pages |

The geometry is crisp and architectural. Corners are softened just enough to feel modern, never enough to feel playful. The rule is simple:

- **Controls take 4px.** Buttons, fields, checkboxes and small CTAs.
- **Big imagery takes 8px.** Media panels, video frames and large feature cards.
- **Full rounding is the exception.** It appears only on circular icon or media controls, never on text buttons or nav items, which stay rectangular.

Logo walls use bare wordmarks with no container shape at all.

## Components

Each component below was distilled from the live page: the recipe is a standalone, placeholder-filled reproduction with literal values, and every frontmatter key named in the anatomy carries the same measurements. A verified component reproduced the original in every check; a flagged one is shipped with the reason it did not; one marked not verifiable could not be compared with the original, which says nothing about the recipe.



### Button, ghost

**Verification**: verified against the live page at desktop.

**Anatomy**

- `button-ghost`: the component root, a `<button>` (`.c-button-ghost`)
- `button-ghost-group`: inner flex row (`.c-button-ghost__group`)
- `button-ghost-label`: label text, 8 characters (`.c-button-ghost__label`)
- `button-ghost-icon`: icon placeholder, 16px (`.c-button-ghost__icon`)

**Recipe**

```html
<div class="c-button-ghost-scope">
  <button class="c-button-ghost" type="button">
    <div class="c-button-ghost__group">
      <span class="c-button-ghost__label">lorem ip</span>
      <span class="c-button-ghost__icon" aria-hidden="true"></span>
    </div>
  </button>
</div>
```

```css
.c-button-ghost-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
}

.c-button-ghost {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-button-ghost__group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-button-ghost__label {
  display: block;
  box-sizing: border-box;
  line-height: 18.2px;
}

.c-button-ghost__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: transform, translate, scale, rotate;
}
```

**States**

- No hover or focus change was observed.

### Card

**Verification**: verified against the live page at desktop.

**Anatomy**

- Group: 6 instances in a 6-column grid; the recipe carries the values they all share
- `card`: the component root, a `<div>` (`.c-card`)
- `card-link`: link (`.c-card__link`)
- `card-media`: image placeholder, 82x58px (`.c-card__media`)

**Recipe**

```html
<div class="c-card-scope">
  <div class="c-card">
    <a class="c-card__link" href="#">
      <span class="c-card__media" aria-hidden="true"></span>
    </a>
  </div>
</div>
```

```css
.c-card-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  height: 96px;
  position: relative;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition: opacity 0.5s cubic-bezier(0.7, 0, 0.3, 1);
}

.c-card__link {
  display: block;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  color: #0F0E0D;
  cursor: pointer;
  text-decoration-line: none;
  transition: opacity 0.3s cubic-bezier(0.7, 0, 0.3, 1);
}

.c-card__media {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 82px;
  height: 58px;
  max-width: 66.6667%;
  max-height: 60%;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
  transition: opacity 0.3s cubic-bezier(0.7, 0, 0.3, 1);
  margin-top: 19.2031px;
  margin-bottom: 19.2031px;
}
```

**States**

- No hover or focus change was observed.

### Hero

**Verification**: flagged, the `hero-title` y did not reproduce the measured 64px after 2 correction attempts.

**Anatomy**

- Group: 4 instances in a 1-column grid; the recipe carries the values they all share
- `hero`: the component root, a `<div>` (`.c-hero`)
- `hero-group`: inner group (`.c-hero__group`)
- `hero-group-2`: inner grid (`.c-hero__group-2`, 2 instances)
- `hero-group-3`: inner block (`.c-hero__group-3`)
- `hero-title`: heading, 35 characters (`.c-hero__title`)
- `hero-group-4`: inner flex row (`.c-hero__group-4`), content not captured
- `hero-group-5`: inner block (`.c-hero__group-5`)
- `hero-group-6`: inner block (`.c-hero__group-6`), content not captured

**Recipe**

```html
<div class="c-hero-scope">
  <div class="c-hero">
    <section class="c-hero__group">
      <div class="c-hero__group-2">
        <div class="c-hero__group-3">
          <h1 class="c-hero__title">lorem ipsum dolor sit amet consecte</h1>
          <div class="c-hero__group-4"></div>
        </div>
      </div>
      <div class="c-hero__group-5">
        <div class="c-hero__group-2">
          <div class="c-hero__group-6"></div>
        </div>
      </div>
    </section>
  </div>
</div>
```

```css
.c-hero-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-hero {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-hero__group {
  display: block;
  box-sizing: border-box;
  background-color: #FAFAF9;
  color: #0F0E0D;
}

.c-hero__group-2 {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(6, minmax(0px, 1fr));
  box-sizing: border-box;
  width: 100%;
  max-width: 1728px;
  padding-right: 32px;
  padding-left: 32px;
  margin-right: auto;
  margin-left: auto;
}

.c-hero__group-3 {
  box-sizing: border-box;
}

.c-hero__title {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 72px;
  font-weight: 400;
  line-height: 75.6px;
  letter-spacing: -0.9px;
}

.c-hero__group-4 {
  display: flex;
  box-sizing: border-box;
}

.c-hero__group-5 {
  display: block;
  box-sizing: border-box;
  margin-top: 64px;
}

.c-hero__group-6 {
  display: block;
  box-sizing: border-box;
}
```

**States**

- No hover or focus change was observed.

### Navigation

**Verification**: verified against the live page at desktop.

**Anatomy**

- `navigation`: the component root, a `<nav>` (`.c-navigation`)
- `navigation-list`: inner flex row (`.c-navigation__list`)
- `navigation-item`: inner flex row (`.c-navigation__item`, 6 instances)
- `navigation-button`: button (`.c-navigation__button`, 4 instances)
- `navigation-group`: inner flex row (`.c-navigation__group`, 4 instances), content not captured
- `navigation-link`: link (`.c-navigation__link`, 2 instances)
- `navigation-group-2`: inner block (`.c-navigation__group-2`, 2 instances), content not captured

**Recipe**

```html
<div class="c-navigation-scope">
  <nav class="c-navigation">
    <ul class="c-navigation__list">
      <li class="c-navigation__item">
        <button class="c-navigation__button" type="button">
          <div class="c-navigation__group"></div>
        </button>
      </li>
      <li class="c-navigation__item">
        <button class="c-navigation__button" type="button">
          <div class="c-navigation__group"></div>
        </button>
      </li>
      <li class="c-navigation__item">
        <a class="c-navigation__link" href="#">
          <div class="c-navigation__group-2"></div>
        </a>
      </li>
      <li class="c-navigation__item">
        <a class="c-navigation__link" href="#">
          <div class="c-navigation__group-2"></div>
        </a>
      </li>
      <li class="c-navigation__item">
        <button class="c-navigation__button" type="button">
          <div class="c-navigation__group"></div>
        </button>
      </li>
      <li class="c-navigation__item">
        <button class="c-navigation__button" type="button">
          <div class="c-navigation__group"></div>
        </button>
      </li>
    </ul>
  </nav>
</div>
```

```css
.c-navigation-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-navigation {
  display: inline-flex;
  align-items: center;
  border-spacing: 0px;
  box-sizing: border-box;
  position: relative;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-navigation__list {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  margin: 0px;
  list-style-type: disc;
}

.c-navigation__item {
  display: flex;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  height: 100%;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  padding-right: 16px;
  padding-left: 16px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-navigation__button {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-navigation__group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-navigation__link {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  width: max-content;
  height: 100%;
  color: #0F0E0D;
  cursor: pointer;
  line-height: 18.2px;
  text-decoration-line: none;
  text-align: center;
  white-space: nowrap;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0, 0.7, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-navigation__group-2 {
  display: block;
  box-sizing: border-box;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}
```

**States**

- No hover or focus change was observed.

### Navigation (2)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `navigation-2`: the component root, a `<nav>` (`.c-navigation-2`), content not captured
- `navigation-2-group`: inner flex column (`.c-navigation-2__group`, 2 instances)
- `navigation-2-title`: heading, 8 characters (`.c-navigation-2__title`, 2 instances)
- `navigation-2-list`: inner flex column (`.c-navigation-2__list`, 2 instances)
- `navigation-2-link`: link, 8-character label (`.c-navigation-2__link`, 16 instances), content not captured
- `navigation-2-item`: inner group (`.c-navigation-2__item`), content not captured

**Recipe**

```html
<div class="c-navigation-2-scope">
  <nav class="c-navigation-2">
    <div class="c-navigation-2__group">
      <h3 class="c-navigation-2__title">lorem ip</h3>
      <ul class="c-navigation-2__list">
        <a class="c-navigation-2__link" href="#">lorem ip</a>
        <a class="c-navigation-2__link" href="#">lorem</a>
        <a class="c-navigation-2__link" href="#">lorem</a>
        <a class="c-navigation-2__link" href="#">lorem ips</a>
        <a class="c-navigation-2__link" href="#">lorem</a>
        <a class="c-navigation-2__link" href="#">lorem ipsum do</a>
        <a class="c-navigation-2__link" href="#">lorem ipsum dolor sit</a>
        <a class="c-navigation-2__link" href="#">lorem ipsum dolo</a>
        <a class="c-navigation-2__link" href="#">lorem ips</a>
        <a class="c-navigation-2__link" href="#">lorem ipsum d</a>
        <a class="c-navigation-2__link" href="#">lorem ipsum</a>
      </ul>
    </div>
    <div class="c-navigation-2__group">
      <h3 class="c-navigation-2__title">lorem ips</h3>
      <ul class="c-navigation-2__list">
        <a class="c-navigation-2__link" href="#">lorem ipsu</a>
        <a class="c-navigation-2__link" href="#">lorem ipsum d</a>
        <a class="c-navigation-2__link" href="#">lorem ipsu</a>
        <a class="c-navigation-2__link" href="#">lorem ip</a>
        <a class="c-navigation-2__link" href="#">lorem ips</a>
        <li class="c-navigation-2__item"></li>
      </ul>
    </div>
  </nav>
</div>
```

```css
.c-navigation-2-scope {
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-navigation-2 {
  display: inline-grid;
  gap: 16px;
  grid-template-columns: repeat(5, minmax(0px, 1fr));
  border-spacing: 0px;
  box-sizing: border-box;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-navigation-2__group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}

.c-navigation-2__title {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #8F8B85;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  letter-spacing: -0.14px;
}

.c-navigation-2__list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  padding: 0px;
  margin: 0px;
  list-style-type: none;
}

.c-navigation-2__link {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  color: #FAFAF9;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  text-decoration-line: none;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.7, 0, 0.3, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-navigation-2__item {
  display: list-item;
  box-sizing: border-box;
}
```

**States**

- No hover or focus change was observed.

### Close button

**Verification**: verified against the live page at desktop.

**Anatomy**

- `close-button`: the component root, a `<button>` (`.c-close-button`)
- `close-button-icon`: icon placeholder, 16px (`.c-close-button__icon`)

**Recipe**

```html
<div class="c-close-button-scope">
  <button class="c-close-button" type="button">
    <span class="c-close-button__icon" aria-hidden="true"></span>
  </button>
</div>
```

```css
.c-close-button-scope {
  background-color: #C7C7C6;
  color: #424140;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
}

.c-close-button {
  display: inline-flex;
  flex-shrink: 0;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 50%;
  right: 32px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-close-button__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition: opacity 0.3s cubic-bezier(0.3, 0.3, 0.3, 1);
}
```

**States**

- No hover or focus change was observed.

### Header (landing)

**Verification**: desktop flagged, the render matched 5% of the original pixels, below the 96% required after 2 correction attempts; mobile verified against the live page at mobile.

Variant observed on https://www.harvey.ai/.

**Anatomy**

- `header-landing`: the component root, a `<header>` (`.c-header-landing`)
- `header-landing-group`: inner block (`.c-header-landing__group`)
- `header-landing-group-2`: inner block (`.c-header-landing__group-2`)
- `header-landing-group-3`: inner grid (`.c-header-landing__group-3`)
- `header-landing-group-4`: inner flex row (`.c-header-landing__group-4`)
- `header-landing-group-5`: inner flex row (`.c-header-landing__group-5`)
- `header-landing-logo`: link (`.c-header-landing__logo`)
- `header-landing-logo-text`: label text, 80 characters (`.c-header-landing__logo-text`)
- `header-landing-logo-text-2`: label text, 10 characters (`.c-header-landing__logo-text-2`)
- `header-landing-menu-toggle`: button (`.c-header-landing__menu-toggle`)
- `header-landing-menu-toggle-icon`: icon placeholder, 16px (`.c-header-landing__menu-toggle-icon`)
- `header-landing-inner`: inner flex row (`.c-header-landing__inner`)
- `header-landing-group-6`: inner flex row (`.c-header-landing__group-6`)
- `header-landing-group-7`: inner flex row (`.c-header-landing__group-7`)
- `header-landing-text`: label text, 8 characters (`.c-header-landing__text`)
- `header-landing-nav`: inner flex row (`.c-header-landing__nav`)
- `header-landing-nav-list`: inner flex row (`.c-header-landing__nav-list`)
- `header-landing-nav-item`: inner flex row (`.c-header-landing__nav-item`, 6 instances)
- `header-landing-cta`: the `button-ghost` button (`.c-header-landing__cta`, 3 instances)
- `header-landing-group-8`: inner flex row (`.c-header-landing__group-8`, 4 instances), content not captured
- `header-landing-nav-link`: link (`.c-header-landing__nav-link`, 2 instances)
- `header-landing-group-9`: inner block (`.c-header-landing__group-9`, 2 instances), content not captured
- `header-landing-menu-toggle-2`: button (`.c-header-landing__menu-toggle-2`)
- `header-landing-group-10`: inner flex row (`.c-header-landing__group-10`)
- `header-landing-group-11`: inner flex row (`.c-header-landing__group-11`)
- `header-landing-group-12`: inner flex row (`.c-header-landing__group-12`)
- `header-landing-group-13`: inner block (`.c-header-landing__group-13`)
- `header-landing-menu-toggle-3`: button (`.c-header-landing__menu-toggle-3`), content not captured
- `header-landing-cta-2`: link (`.c-header-landing__cta-2`)
- `header-landing-text-2`: label text, 14 characters (`.c-header-landing__text-2`)

**Desktop recipe**

```html
<div class="c-header-landing-scope">
  <header class="c-header-landing">
    <div class="c-header-landing__group"></div>
    <div class="c-header-landing__group-2">
      <div class="c-header-landing__group-3">
        <div class="c-header-landing__group-4">
          <div class="c-header-landing__group-5">
            <a class="c-header-landing__logo" href="#">
              <span class="c-header-landing__logo-text">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lor</span>
              <span class="c-header-landing__logo-text-2">lorem ipsu</span>
            </a>
          </div>
          <button class="c-header-landing__menu-toggle" type="button">
            <span class="c-header-landing__menu-toggle-icon" aria-hidden="true"></span>
          </button>
        </div>
      </div>
      <div class="c-header-landing__inner">
        <div class="c-header-landing__group-6">
          <div class="c-header-landing__group-7">
            <div class="c-header-landing__text">lorem ip</div>
          </div>
          <nav class="c-header-landing__nav">
            <ul class="c-header-landing__nav-list">
              <li class="c-header-landing__nav-item">
                <button class="c-header-landing__cta" type="button">
                  <div class="c-header-landing__group-8"></div>
                </button>
              </li>
              <li class="c-header-landing__nav-item">
                <button class="c-header-landing__cta" type="button">
                  <div class="c-header-landing__group-8"></div>
                </button>
              </li>
              <li class="c-header-landing__nav-item">
                <a class="c-header-landing__nav-link" href="#">
                  <div class="c-header-landing__group-9"></div>
                </a>
              </li>
              <li class="c-header-landing__nav-item">
                <a class="c-header-landing__nav-link" href="#">
                  <div class="c-header-landing__group-9"></div>
                </a>
              </li>
              <li class="c-header-landing__nav-item">
                <button class="c-header-landing__cta" type="button">
                  <div class="c-header-landing__group-8"></div>
                </button>
              </li>
              <li class="c-header-landing__nav-item">
                <button class="c-header-landing__menu-toggle-2" type="button">
                  <div class="c-header-landing__group-8"></div>
                </button>
              </li>
            </ul>
          </nav>
          <div class="c-header-landing__group-10">
            <div class="c-header-landing__group-11">
              <div class="c-header-landing__group-12">
                <div class="c-header-landing__group-13">
                  <button class="c-header-landing__menu-toggle-3" type="button"></button>
                </div>
              </div>
              <a class="c-header-landing__cta-2" href="#">
                <p class="c-header-landing__text-2">lorem ipsum do</p>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</div>
```

```css
.c-header-landing-scope {
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-landing {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  position: fixed;
  top: 0px;
  right: 0px;
  left: 0px;
  z-index: 100;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__group {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: #0F0E0D99;
  backdrop-filter: blur(16px);
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__group-2 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  position: relative;
}

.c-header-landing__group-3 {
  display: grid;
  grid-template-rows: 1fr;
  box-sizing: border-box;
  position: relative;
  z-index: 30;
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-size: 14px;
  line-height: 18.2px;
  text-align: center;
  padding-right: 32px;
  padding-left: 32px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: grid-template-rows, color, background-color;
}

.c-header-landing__group-3::after {
  content: "";
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 1440px;
  background-color: #FAFAF9;
}

.c-header-landing__group-4 {
  display: flex;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-header-landing__group-5 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding-top: 8px;
  padding-bottom: 8px;
}

.c-header-landing__logo {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  gap: 10px;
  box-sizing: border-box;
  color: #0F0E0D;
  cursor: pointer;
  text-decoration-line: none;
}

.c-header-landing__logo-text-2 {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  position: relative;
  font-weight: 500;
}

.c-header-landing__menu-toggle {
  display: flex;
  flex-shrink: 0;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 50%;
  right: 32px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  margin-right: -8px;
}

.c-header-landing__menu-toggle-icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition: opacity 0.3s cubic-bezier(0.3, 0.3, 0.3, 1);
}

.c-header-landing__inner {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 72px;
  max-width: 1920px;
  position: relative;
  padding-right: 32px;
  padding-left: 32px;
  margin-right: auto;
  margin-left: auto;
}

.c-header-landing__group-6 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
}

.c-header-landing__group-7 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.c-header-landing__text {
  display: block;
  box-sizing: border-box;
  cursor: pointer;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 28px;
  line-height: 39.2px;
}

.c-header-landing__nav {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  position: relative;
  margin-right: auto;
  margin-left: 16px;
}

.c-header-landing__nav-list {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  margin: 0px;
  list-style-type: disc;
}

.c-header-landing__nav-item {
  display: flex;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  height: 100%;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  padding-right: 16px;
  padding-left: 16px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__cta {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-landing__group-8 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-header-landing__nav-link {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  width: max-content;
  height: 100%;
  color: #FAFAF9;
  cursor: pointer;
  line-height: 18.2px;
  text-decoration-line: none;
  text-align: center;
  white-space: nowrap;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0, 0.7, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__group-9 {
  display: block;
  box-sizing: border-box;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__menu-toggle-2 {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-landing__group-10 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
}

.c-header-landing__group-11 {
  display: flex;
  align-items: center;
  gap: 16px;
  box-sizing: border-box;
  height: 100%;
}

.c-header-landing__group-12 {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__group-13 {
  display: block;
  box-sizing: border-box;
  position: relative;
}

.c-header-landing__menu-toggle-3 {
  display: flex;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  height: 32px;
  padding: 7px 7px 7px 12px;
  background-color: transparent;
  color: #FAFAF9;
  border: 1px solid #FAFAF9;
  border-radius: 4px;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__cta-2 {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  height: 32px;
  background-color: #FAFAF9;
  color: #0F0E0D;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 14px;
  text-decoration-line: none;
  white-space: nowrap;
  padding-right: 12px;
  padding-left: 12px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing__text-2 {
  display: block;
  box-sizing: border-box;
  margin: 0px;
}

.c-header-landing__menu-toggle-3:hover {
  background-color: #FAFAF9;
  color: #0F0E0D;
}

.c-header-landing__menu-toggle-3:focus {
  background-color: #FAFAF9;
  color: #0F0E0D;
}

.c-header-landing__cta-2:hover {
  background-color: #8F8B85;
}

.c-header-landing__cta-2:focus {
  box-shadow: transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px;
  outline: none;
}
```

**Mobile anatomy**

- `header-landing-mobile`: the component root, a `<header>` (`.c-header-landing-mobile`)
- `header-landing-mobile-group`: inner block (`.c-header-landing-mobile__group`)
- `header-landing-mobile-group-2`: inner block (`.c-header-landing-mobile__group-2`)
- `header-landing-mobile-group-3`: inner grid (`.c-header-landing-mobile__group-3`)
- `header-landing-mobile-group-4`: inner flex row (`.c-header-landing-mobile__group-4`)
- `header-landing-mobile-group-5`: inner flex row (`.c-header-landing-mobile__group-5`)
- `header-landing-mobile-group-6`: inner flex row (`.c-header-landing-mobile__group-6`)
- `header-landing-mobile-logo`: link (`.c-header-landing-mobile__logo`)
- `header-landing-mobile-group-7`: inner flex row (`.c-header-landing-mobile__group-7`, 2 instances)
- `header-landing-mobile-group-8`: inner group (`.c-header-landing-mobile__group-8`, 2 instances), content not captured
- `header-landing-mobile-logo-text`: label text, 10 characters (`.c-header-landing-mobile__logo-text`, 2 instances)
- `header-landing-mobile-inner`: inner flex row (`.c-header-landing-mobile__inner`)
- `header-landing-mobile-group-9`: inner flex row (`.c-header-landing-mobile__group-9`)
- `header-landing-mobile-group-10`: inner flex row (`.c-header-landing-mobile__group-10`)
- `header-landing-mobile-text`: label text, 8 characters (`.c-header-landing-mobile__text`)
- `header-landing-mobile-group-11`: inner flex row (`.c-header-landing-mobile__group-11`)
- `header-landing-mobile-group-12`: inner flex row (`.c-header-landing-mobile__group-12`)
- `header-landing-mobile-menu-toggle`: button (`.c-header-landing-mobile__menu-toggle`)
- `header-landing-mobile-menu-toggle-icon`: icon placeholder, 24x25px (`.c-header-landing-mobile__menu-toggle-icon`)

**Mobile recipe**

```html
<div class="c-header-landing-mobile-scope">
  <header class="c-header-landing-mobile">
    <div class="c-header-landing-mobile__group"></div>
    <div class="c-header-landing-mobile__group-2">
      <div class="c-header-landing-mobile__group-3">
        <div class="c-header-landing-mobile__group-4">
          <div class="c-header-landing-mobile__group-5">
            <div class="c-header-landing-mobile__group-6">
              <a class="c-header-landing-mobile__logo" href="#">
                <span class="c-header-landing-mobile__group-7">
                  <span class="c-header-landing-mobile__group-8"></span>
                  <span class="c-header-landing-mobile__logo-text">lorem ipsu</span>
                </span>
                <span class="c-header-landing-mobile__group-7">
                  <span class="c-header-landing-mobile__group-8"></span>
                  <span class="c-header-landing-mobile__logo-text">lorem ipsu</span>
                </span>
              </a>
            </div>
          </div>
        </div>
      </div>
      <div class="c-header-landing-mobile__inner">
        <div class="c-header-landing-mobile__group-9">
          <div class="c-header-landing-mobile__group-10">
            <div class="c-header-landing-mobile__text">lorem ip</div>
          </div>
          <div class="c-header-landing-mobile__group-11">
            <div class="c-header-landing-mobile__group-12">
              <button class="c-header-landing-mobile__menu-toggle" type="button">
                <span class="c-header-landing-mobile__menu-toggle-icon" aria-hidden="true"></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</div>
```

```css
.c-header-landing-mobile-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-landing-mobile {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  position: fixed;
  top: 0px;
  right: 0px;
  left: 0px;
  z-index: 100;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing-mobile__group {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: #FAFAF9B8;
  backdrop-filter: blur(16px);
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-landing-mobile__group-2 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  position: relative;
}

.c-header-landing-mobile__group-3 {
  display: grid;
  grid-template-rows: 1fr;
  box-sizing: border-box;
  position: relative;
  z-index: 30;
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-size: 14px;
  line-height: 18.2px;
  text-align: left;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: grid-template-rows, color, background-color;
}

.c-header-landing-mobile__group-3::after {
  content: "";
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 390px;
  background-color: #0F0E0D;
}

.c-header-landing-mobile__group-4 {
  display: flex;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-header-landing-mobile__group-5 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding-top: 8px;
  padding-bottom: 8px;
}

.c-header-landing-mobile__group-6 {
  display: flex;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-header-landing-mobile__logo {
  display: flex;
  box-sizing: border-box;
  width: max-content;
  color: #FAFAF9;
  cursor: pointer;
  transform: matrix(1, 0, 0, 1, -221.88, 0);
  text-decoration-line: none;
  white-space: nowrap;
}

.c-header-landing-mobile__group-7 {
  display: flex;
  align-items: center;
  gap: 10px;
  box-sizing: border-box;
  padding-right: 16px;
  padding-left: 16px;
}

.c-header-landing-mobile__group-8 {
  display: block;
  box-sizing: border-box;
}

.c-header-landing-mobile__logo-text {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  font-weight: 500;
}

.c-header-landing-mobile__inner {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 72px;
  max-width: 1920px;
  position: relative;
  padding-right: 28px;
  padding-left: 28px;
  margin-right: auto;
  margin-left: auto;
}

.c-header-landing-mobile__group-9 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
}

.c-header-landing-mobile__group-10 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.c-header-landing-mobile__text {
  display: block;
  box-sizing: border-box;
  cursor: pointer;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 28px;
  line-height: 39.2px;
}

.c-header-landing-mobile__group-11 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
}

.c-header-landing-mobile__group-12 {
  display: flex;
  align-items: center;
  gap: 8px;
  box-sizing: border-box;
}

.c-header-landing-mobile__menu-toggle {
  display: block;
  box-sizing: border-box;
  padding: 0px;
  position: relative;
  z-index: 30;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-landing-mobile__menu-toggle-icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 24px;
  height: 25px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
}

.c-header-landing-mobile__logo:focus {
  transform: matrix(1, 0, 0, 1, -276.884, 0);
}
```

**States**

- `header-landing-menu-toggle-3` hover (`header-landing-menu-toggle-3-hover`): background-color #FAFAF9, color #0F0E0D
- `header-landing-menu-toggle-3` focus (`header-landing-menu-toggle-3-focus`): background-color #FAFAF9, color #0F0E0D
- `header-landing-cta-2` hover (`header-landing-cta-2-hover`): background-color #8F8B85
- `header-landing-cta-2` focus: box-shadow transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px, outline none
- mobile, `header-landing-mobile-logo` focus: transform matrix(1, 0, 0, 1, -276.884, 0)

### Footer (landing)

**Verification**: desktop verified against the live page at desktop; mobile verified against the live page at mobile.

Variant observed on https://www.harvey.ai/.

**Anatomy**

- `footer-landing`: the component root, a `<footer>` (`.c-footer-landing`)
- `footer-landing-inner`: inner block (`.c-footer-landing__inner`)
- `footer-landing-columns`: inner flex row (`.c-footer-landing__columns`)
- `footer-landing-heading`: heading, 50 characters (`.c-footer-landing__heading`)
- `footer-landing-link`: link (`.c-footer-landing__link`)
- `footer-landing-text`: label text, 14 characters (`.c-footer-landing__text`)
- `footer-landing-columns-2`: inner flex row (`.c-footer-landing__columns-2`)
- `footer-landing-group`: inner flex column (`.c-footer-landing__group`)
- `footer-landing-logo`: icon placeholder, 45x32px (`.c-footer-landing__logo`)
- `footer-landing-group-2`: inner flex column (`.c-footer-landing__group-2`)
- `footer-landing-inner-2`: label text, 60 characters (`.c-footer-landing__inner-2`)
- `footer-landing-nav`: inner grid (`.c-footer-landing__nav`)
- `footer-landing-group-3`: inner flex column (`.c-footer-landing__group-3`, 5 instances), content not captured
- `footer-landing-heading-2`: heading, 8 characters (`.c-footer-landing__heading-2`, 5 instances)
- `footer-landing-list`: inner flex column (`.c-footer-landing__list`, 4 instances)
- `footer-landing-nav-link`: link (`.c-footer-landing__nav-link`, 31 instances)
- `footer-landing-text-2`: label text, 8 characters (`.c-footer-landing__text-2`, 31 instances)
- `footer-landing-group-4`: inner group (`.c-footer-landing__group-4`, 31 instances)
- `footer-landing-nav-link-icon`: icon placeholder, 24px (`.c-footer-landing__nav-link-icon`)

**Desktop recipe**

```html
<div class="c-footer-landing-scope">
  <footer class="c-footer-landing">
    <div class="c-footer-landing__inner">
      <section class="c-footer-landing__columns">
        <h3 class="c-footer-landing__heading">lorem ipsum dolor sit amet consectetur adipiscing</h3>
        <a class="c-footer-landing__link" href="#">
          <p class="c-footer-landing__text">lorem ipsum do</p>
        </a>
      </section>
      <div class="c-footer-landing__columns-2">
        <div class="c-footer-landing__group">
          <span class="c-footer-landing__logo" aria-hidden="true"></span>
          <div class="c-footer-landing__group-2">
            <p class="c-footer-landing__inner-2">lorem ipsum dolor sit amet consectetur adipiscing elit sed d</p>
          </div>
        </div>
        <nav class="c-footer-landing__nav">
          <div class="c-footer-landing__group-3">
            <h3 class="c-footer-landing__heading-2">lorem ip</h3>
            <ul class="c-footer-landing__list">
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ip</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ips</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum do</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum dolor sit</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum dolo</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ips</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum d</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
            </ul>
          </div>
          <div class="c-footer-landing__group-3">
            <h3 class="c-footer-landing__heading-2">lorem ips</h3>
            <ul class="c-footer-landing__list">
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsu</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum d</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsu</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ip</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ips</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum dol</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
            </ul>
          </div>
          <div class="c-footer-landing__group-3">
            <h3 class="c-footer-landing__heading-2">lorem i</h3>
            <ul class="c-footer-landing__list">
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ips</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ip</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem i</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ip</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
            </ul>
          </div>
          <div class="c-footer-landing__group-3">
            <h3 class="c-footer-landing__heading-2">lorem ips</h3>
            <ul class="c-footer-landing__list">
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lore</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum d</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum do</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ipsum do</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__text-2">lorem ips</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
              <a class="c-footer-landing__nav-link" href="#">
                <span class="c-footer-landing__nav-link-icon" aria-hidden="true"></span>
                <span class="c-footer-landing__text-2">lorem ipsum dolor si</span>
                <span class="c-footer-landing__group-4"></span>
              </a>
            </ul>
          </div>
          <div class="c-footer-landing__group-3">
            <h3 class="c-footer-landing__heading-2">lorem</h3>
          </div>
        </nav>
      </div>
    </div>
  </footer>
</div>
```

```css
.c-footer-landing-scope {
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-landing {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-landing__inner {
  display: block;
  box-sizing: border-box;
  max-width: 1728px;
  padding: 64px 32px;
  margin-right: auto;
  margin-left: auto;
}

.c-footer-landing__columns {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  padding-bottom: 64px;
  border-bottom-width: 1px;
  border-bottom-style: solid;
  border-bottom-color: #33312C;
}

.c-footer-landing__heading {
  display: block;
  box-sizing: border-box;
  width: 100%;
  margin: 0px;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 24px;
  font-weight: 400;
  line-height: 25.2px;
  letter-spacing: -0.24px;
}

.c-footer-landing__link {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  height: 48px;
  background-color: #FAFAF9;
  color: #0F0E0D;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  line-height: 16px;
  text-decoration-line: none;
  white-space: nowrap;
  padding-right: 20px;
  padding-left: 20px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-footer-landing__text {
  display: block;
  box-sizing: border-box;
  margin: 0px;
}

.c-footer-landing__columns-2 {
  display: flex;
  box-sizing: border-box;
  margin-top: 64px;
}

.c-footer-landing__group {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
}

.c-footer-landing__logo {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 45px;
  height: 32px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
}

.c-footer-landing__group-2 {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  margin-right: 32px;
}

.c-footer-landing__inner-2 {
  display: block;
  box-sizing: border-box;
  max-width: 224px;
  margin: 0px;
  color: #8F8B85;
  font-size: 14px;
  line-height: 18.2px;
}

.c-footer-landing__nav {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(5, minmax(0px, 1fr));
  box-sizing: border-box;
  margin-left: auto;
}

.c-footer-landing__group-3 {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}

.c-footer-landing__heading-2 {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #8F8B85;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  letter-spacing: -0.14px;
}

.c-footer-landing__list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  padding: 0px;
  margin: 0px;
  list-style-type: none;
}

.c-footer-landing__nav-link {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  color: #FAFAF9;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  text-decoration-line: none;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.7, 0, 0.3, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-footer-landing__group-4 {
  display: block;
  box-sizing: border-box;
  width: 12px;
  position: relative;
  margin-left: 4px;
}

.c-footer-landing__nav-link-icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 24px;
  height: 24px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  margin-right: 4px;
}

.c-footer-landing__link:hover {
  background-color: #8F8B85;
}

.c-footer-landing__link:focus {
  box-shadow: transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px;
  outline: none;
}

.c-footer-landing__nav-link:hover {
  color: #CCCAC6;
}
```

**Mobile anatomy**

- `footer-landing-mobile`: the component root, a `<footer>` (`.c-footer-landing-mobile`)
- `footer-landing-mobile-inner`: inner block (`.c-footer-landing-mobile__inner`)
- `footer-landing-mobile-group`: inner flex column (`.c-footer-landing-mobile__group`)
- `footer-landing-mobile-heading`: heading, 50 characters (`.c-footer-landing-mobile__heading`)
- `footer-landing-mobile-link`: link (`.c-footer-landing-mobile__link`)
- `footer-landing-mobile-text`: label text, 14 characters (`.c-footer-landing-mobile__text`)
- `footer-landing-mobile-group-2`: inner flex column (`.c-footer-landing-mobile__group-2`)
- `footer-landing-mobile-group-3`: inner flex column (`.c-footer-landing-mobile__group-3`)
- `footer-landing-mobile-logo`: icon placeholder, 45x32px (`.c-footer-landing-mobile__logo`)
- `footer-landing-mobile-nav`: inner grid (`.c-footer-landing-mobile__nav`)
- `footer-landing-mobile-group-4`: inner flex column (`.c-footer-landing-mobile__group-4`, 5 instances)
- `footer-landing-mobile-heading-2`: heading, 8 characters (`.c-footer-landing-mobile__heading-2`, 5 instances)
- `footer-landing-mobile-list`: inner flex column (`.c-footer-landing-mobile__list`, 5 instances)
- `footer-landing-mobile-nav-link`: link, 8-character label (`.c-footer-landing-mobile__nav-link`, 35 instances)
- `footer-landing-mobile-nav-link-icon`: icon placeholder, 24px (`.c-footer-landing-mobile__nav-link-icon`)
- `footer-landing-mobile-text-2`: label text, 20 characters (`.c-footer-landing-mobile__text-2`)
- `footer-landing-mobile-group-5`: inner flex column (`.c-footer-landing-mobile__group-5`)
- `footer-landing-mobile-inner-2`: label text, 60 characters (`.c-footer-landing-mobile__inner-2`)

**Mobile recipe**

```html
<div class="c-footer-landing-mobile-scope">
  <footer class="c-footer-landing-mobile">
    <div class="c-footer-landing-mobile__inner">
      <section class="c-footer-landing-mobile__group">
        <h3 class="c-footer-landing-mobile__heading">lorem ipsum dolor sit amet consectetur adipiscing</h3>
        <a class="c-footer-landing-mobile__link" href="#">
          <p class="c-footer-landing-mobile__text">lorem ipsum do</p>
        </a>
      </section>
      <div class="c-footer-landing-mobile__group-2">
        <div class="c-footer-landing-mobile__group-3">
          <span class="c-footer-landing-mobile__logo" aria-hidden="true"></span>
        </div>
        <nav class="c-footer-landing-mobile__nav">
          <div class="c-footer-landing-mobile__group-4">
            <h3 class="c-footer-landing-mobile__heading-2">lorem ip</h3>
            <ul class="c-footer-landing-mobile__list">
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ip</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ips</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum do</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum dolor sit</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum dolo</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ips</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum d</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum</a>
            </ul>
          </div>
          <div class="c-footer-landing-mobile__group-4">
            <h3 class="c-footer-landing-mobile__heading-2">lorem ips</h3>
            <ul class="c-footer-landing-mobile__list">
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsu</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum d</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsu</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ip</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ips</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum dol</a>
            </ul>
          </div>
          <div class="c-footer-landing-mobile__group-4">
            <h3 class="c-footer-landing-mobile__heading-2">lorem i</h3>
            <ul class="c-footer-landing-mobile__list">
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ips</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ip</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem i</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ip</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum</a>
            </ul>
          </div>
          <div class="c-footer-landing-mobile__group-4">
            <h3 class="c-footer-landing-mobile__heading-2">lorem ips</h3>
            <ul class="c-footer-landing-mobile__list">
              <a class="c-footer-landing-mobile__nav-link" href="#">lore</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum d</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum do</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ipsum do</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ips</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">
                <span class="c-footer-landing-mobile__nav-link-icon" aria-hidden="true"></span>
                <span class="c-footer-landing-mobile__text-2">lorem ipsum dolor si</span>
              </a>
            </ul>
          </div>
          <div class="c-footer-landing-mobile__group-4">
            <h3 class="c-footer-landing-mobile__heading-2">lorem</h3>
            <ul class="c-footer-landing-mobile__list">
              <a class="c-footer-landing-mobile__nav-link" href="#">l</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ip</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem i</a>
              <a class="c-footer-landing-mobile__nav-link" href="#">lorem ips</a>
            </ul>
          </div>
        </nav>
      </div>
      <div class="c-footer-landing-mobile__group-5">
        <p class="c-footer-landing-mobile__inner-2">lorem ipsum dolor sit amet consectetur adipiscing elit sed d</p>
      </div>
    </div>
  </footer>
</div>
```

```css
.c-footer-landing-mobile-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-landing-mobile {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-landing-mobile__inner {
  display: block;
  box-sizing: border-box;
  max-width: 1728px;
  padding: 56px 28px;
  margin-right: auto;
  margin-left: auto;
}

.c-footer-landing-mobile__group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-sizing: border-box;
  padding-bottom: 56px;
  border-bottom-width: 1px;
  border-bottom-style: solid;
  border-bottom-color: #33312C;
}

.c-footer-landing-mobile__heading {
  display: block;
  box-sizing: border-box;
  width: 100%;
  margin: 0px 0px 28px;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 24px;
  font-weight: 400;
  line-height: 25.2px;
  letter-spacing: -0.24px;
}

.c-footer-landing-mobile__link {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  height: 48px;
  background-color: #FAFAF9;
  color: #0F0E0D;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  line-height: 16px;
  text-decoration-line: none;
  white-space: nowrap;
  padding-right: 20px;
  padding-left: 20px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-footer-landing-mobile__text {
  display: block;
  box-sizing: border-box;
  margin: 0px;
}

.c-footer-landing-mobile__group-2 {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  margin-top: 56px;
}

.c-footer-landing-mobile__group-3 {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  margin-bottom: 56px;
}

.c-footer-landing-mobile__logo {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 45px;
  height: 32px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
}

.c-footer-landing-mobile__nav {
  display: grid;
  gap: 28px;
  grid-template-columns: repeat(2, minmax(0px, 1fr));
  box-sizing: border-box;
  margin-bottom: 56px;
}

.c-footer-landing-mobile__group-4 {
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-sizing: border-box;
}

.c-footer-landing-mobile__heading-2 {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #8F8B85;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  letter-spacing: -0.14px;
}

.c-footer-landing-mobile__list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-sizing: border-box;
  padding: 0px;
  margin: 0px;
  list-style-type: none;
}

.c-footer-landing-mobile__nav-link {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  color: #FAFAF9;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  text-decoration-line: none;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.7, 0, 0.3, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-footer-landing-mobile__nav-link-icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 24px;
  height: 24px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  margin-right: 4px;
}

.c-footer-landing-mobile__group-5 {
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-sizing: border-box;
  margin-top: 28px;
}

.c-footer-landing-mobile__inner-2 {
  display: block;
  box-sizing: border-box;
  max-width: 224px;
  margin: 0px;
  color: #8F8B85;
  font-size: 14px;
  line-height: 18.2px;
}

.c-footer-landing-mobile__link:focus {
  box-shadow: transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px;
  outline: none;
}

.c-footer-landing-mobile__nav-link:hover {
  color: #CCCAC6;
}
```

**States**

- `footer-landing-link` hover (`footer-landing-link-hover`): background-color #8F8B85
- `footer-landing-link` focus: box-shadow transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px, outline none
- `footer-landing-nav-link` hover (`footer-landing-nav-link-hover`): color #CCCAC6
- mobile, `footer-landing-mobile-link` focus: box-shadow transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px, outline none
- mobile, `footer-landing-mobile-nav-link` hover (`footer-landing-mobile-nav-link-hover`): color #CCCAC6

### Card (2)

**Verification**: not verifiable, what the page placed in it (photos, media, ads) covers most of it and nothing else differs, so the comparison could not be judged.

**Anatomy**

- Group: 3 instances in a 3-column grid, 16px gap; the recipe carries the values they all share
- `card-2`: the component root, a `<a>` (`.c-card-2`)
- `card-2-group`: inner block (`.c-card-2__group`)
- `card-2-media`: image placeholder, 448x252px (`.c-card-2__media`)
- `card-2-group-2`: inner flex column (`.c-card-2__group-2`)
- `card-2-title`: heading, 0 characters (`.c-card-2__title`)
- `card-2-text`: label text, 28 characters (`.c-card-2__text`)

**Recipe**

```html
<div class="c-card-2-scope">
  <a class="c-card-2" href="#">
    <div class="c-card-2__group">
      <span class="c-card-2__media" aria-hidden="true"></span>
    </div>
    <div class="c-card-2__group-2">
      <h3 class="c-card-2__title">
        <strong class="c-card-2__text">lorem ipsum dolor sit amet c</strong>
      </h3>
    </div>
  </a>
</div>
```

```css
.c-card-2-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card-2 {
  display: inline-flex;
  flex-direction: column;
  gap: 16px;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #0F0E0D;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  text-decoration-line: none;
}

.c-card-2__group {
  display: block;
  box-sizing: border-box;
  width: 100%;
  aspect-ratio: 16 / 9;
  position: relative;
  overflow-x: hidden;
  overflow-y: hidden;
  border-radius: 4px;
}

.c-card-2__media {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 448px;
  height: 252px;
  max-width: 100%;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
  transition: scale 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.c-card-2__group-2 {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  margin-right: 16px;
}

.c-card-2__title {
  display: flow-root;
  box-sizing: border-box;
  margin: 0px;
  overflow-x: hidden;
  overflow-y: hidden;
  font-size: 24px;
  font-weight: 400;
  line-height: 31.2px;
  letter-spacing: -0.24px;
}

.c-card-2__text {
  display: inline;
  box-sizing: border-box;
  font-weight: 500;
}
```

**States**

- No hover or focus change was observed.

### Footer link columns

**Verification**: verified against the live page at desktop.

**Anatomy**

- `footer-link-column`: the component root, a `<nav>` (`.c-footer-link-column`), content not captured
- `footer-link-column-group`: inner flex column (`.c-footer-link-column__group`, 2 instances)
- `footer-link-column-title`: heading, 8 characters (`.c-footer-link-column__title`, 2 instances)
- `footer-link-column-list`: inner flex column (`.c-footer-link-column__list`, 2 instances)
- `footer-link-column-link`: link, 8-character label (`.c-footer-link-column__link`, 16 instances), content not captured
- `footer-link-column-item`: inner group (`.c-footer-link-column__item`), content not captured

**Recipe**

```html
<div class="c-footer-link-column-scope">
  <nav class="c-footer-link-column">
    <div class="c-footer-link-column__group">
      <h3 class="c-footer-link-column__title">lorem ip</h3>
      <ul class="c-footer-link-column__list">
        <a class="c-footer-link-column__link" href="#">lorem ip</a>
        <a class="c-footer-link-column__link" href="#">lorem</a>
        <a class="c-footer-link-column__link" href="#">lorem</a>
        <a class="c-footer-link-column__link" href="#">lorem ips</a>
        <a class="c-footer-link-column__link" href="#">lorem</a>
        <a class="c-footer-link-column__link" href="#">lorem ipsum do</a>
        <a class="c-footer-link-column__link" href="#">lorem ipsum dolor sit</a>
        <a class="c-footer-link-column__link" href="#">lorem ipsum dolo</a>
        <a class="c-footer-link-column__link" href="#">lorem ips</a>
        <a class="c-footer-link-column__link" href="#">lorem ipsum d</a>
        <a class="c-footer-link-column__link" href="#">lorem ipsum</a>
      </ul>
    </div>
    <div class="c-footer-link-column__group">
      <h3 class="c-footer-link-column__title">lorem ips</h3>
      <ul class="c-footer-link-column__list">
        <a class="c-footer-link-column__link" href="#">lorem ipsu</a>
        <a class="c-footer-link-column__link" href="#">lorem ipsum d</a>
        <a class="c-footer-link-column__link" href="#">lorem ipsu</a>
        <a class="c-footer-link-column__link" href="#">lorem ip</a>
        <a class="c-footer-link-column__link" href="#">lorem ips</a>
        <li class="c-footer-link-column__item"></li>
      </ul>
    </div>
  </nav>
</div>
```

```css
.c-footer-link-column-scope {
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-link-column {
  display: inline-grid;
  gap: 16px;
  grid-template-columns: repeat(5, minmax(0px, 1fr));
  border-spacing: 0px;
  box-sizing: border-box;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-link-column__group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}

.c-footer-link-column__title {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #8F8B85;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  letter-spacing: -0.14px;
}

.c-footer-link-column__list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  padding: 0px;
  margin: 0px;
  list-style-type: none;
}

.c-footer-link-column__link {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  color: #FAFAF9;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  text-decoration-line: none;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.7, 0, 0.3, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-footer-link-column__item {
  display: list-item;
  box-sizing: border-box;
}
```

**States**

- No hover or focus change was observed.

### Announcement banner

**Verification**: verified against the live page at desktop.

**Anatomy**

- `announcement-banner`: the component root, a `<header>` (`.c-announcement-banner`)
- `announcement-banner-group`: inner block (`.c-announcement-banner__group`)
- `announcement-banner-group-2`: inner block (`.c-announcement-banner__group-2`)
- `announcement-banner-group-3`: inner grid (`.c-announcement-banner__group-3`)
- `announcement-banner-group-4`: inner flex row (`.c-announcement-banner__group-4`)
- `announcement-banner-group-5`: inner flex row (`.c-announcement-banner__group-5`), content not captured
- `announcement-banner-button`: button (`.c-announcement-banner__button`), content not captured
- `announcement-banner-group-6`: inner flex row (`.c-announcement-banner__group-6`)
- `announcement-banner-group-7`: inner flex row (`.c-announcement-banner__group-7`)
- `announcement-banner-group-8`: inner flex row (`.c-announcement-banner__group-8`), content not captured
- `announcement-banner-group-9`: inner flex row (`.c-announcement-banner__group-9`), content not captured
- `announcement-banner-group-10`: inner flex row (`.c-announcement-banner__group-10`), content not captured

**Recipe**

```html
<div class="c-announcement-banner-scope">
  <header class="c-announcement-banner">
    <div class="c-announcement-banner__group"></div>
    <div class="c-announcement-banner__group-2">
      <div class="c-announcement-banner__group-3">
        <div class="c-announcement-banner__group-4">
          <div class="c-announcement-banner__group-5"></div>
          <button class="c-announcement-banner__button" type="button"></button>
        </div>
      </div>
      <div class="c-announcement-banner__group-6">
        <div class="c-announcement-banner__group-7">
          <div class="c-announcement-banner__group-8"></div>
          <nav class="c-announcement-banner__group-9"></nav>
          <div class="c-announcement-banner__group-10"></div>
        </div>
      </div>
    </div>
  </header>
</div>
```

```css
.c-announcement-banner-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-announcement-banner {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  position: fixed;
  top: 0px;
  right: 0px;
  left: 0px;
  z-index: 100;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-announcement-banner__group {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: #FAFAF9B8;
  backdrop-filter: blur(16px);
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-announcement-banner__group-2 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  position: relative;
}

.c-announcement-banner__group-3 {
  display: grid;
  grid-template-rows: 1fr;
  box-sizing: border-box;
  position: relative;
  z-index: 30;
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-size: 14px;
  line-height: 18.2px;
  text-align: center;
  padding-right: 32px;
  padding-left: 32px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: grid-template-rows, color, background-color;
}

.c-announcement-banner__group-3::after {
  content: "";
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 1440px;
  background-color: #0F0E0D;
}

.c-announcement-banner__group-4 {
  display: flex;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-announcement-banner__group-5 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding-top: 8px;
  padding-bottom: 8px;
}

.c-announcement-banner__button {
  display: flex;
  flex-shrink: 0;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 50%;
  right: 32px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  margin-right: -8px;
}

.c-announcement-banner__group-6 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 72px;
  max-width: 1920px;
  position: relative;
  padding-right: 32px;
  padding-left: 32px;
  margin-right: auto;
  margin-left: auto;
}

.c-announcement-banner__group-7 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
}

.c-announcement-banner__group-8 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.c-announcement-banner__group-9 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  position: relative;
  margin-right: auto;
  margin-left: 16px;
}

.c-announcement-banner__group-10 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
}
```

**States**

- No hover or focus change was observed.

### Header (inner)

**Verification**: verified against the live page at desktop.

Variant observed on https://www.harvey.ai/blog/harvey-raises-dollar550m-at-a-dollar155b-valuation-to-help-legal-teams-own-their-intelligence.

**Anatomy**

- `header-inner`: the component root, a `<nav>` (`.c-header-inner`)
- `header-inner-group`: inner block (`.c-header-inner__group`)
- `header-inner-nav`: inner flex row (`.c-header-inner__nav`)
- `header-inner-nav-item`: inner flex row (`.c-header-inner__nav-item`, 6 instances)
- `header-inner-cta`: the `button-ghost` button (`.c-header-inner__cta`, 3 instances)
- `header-inner-group-2`: inner flex row (`.c-header-inner__group-2`, 4 instances)
- `header-inner-text`: label text, 8 characters (`.c-header-inner__text`, 4 instances)
- `header-inner-icon`: icon placeholder, 16px (`.c-header-inner__icon`, 4 instances)
- `header-inner-nav-link`: link, 9-character label (`.c-header-inner__nav-link`, 2 instances)
- `header-inner-button`: button (`.c-header-inner__button`)

**Recipe**

```html
<div class="c-header-inner-scope">
  <nav class="c-header-inner">
    <div class="c-header-inner__group"></div>
    <ul class="c-header-inner__nav">
      <li class="c-header-inner__nav-item">
        <button class="c-header-inner__cta" type="button">
          <div class="c-header-inner__group-2">
            <span class="c-header-inner__text">lorem ip</span>
            <span class="c-header-inner__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
      <li class="c-header-inner__nav-item">
        <button class="c-header-inner__cta" type="button">
          <div class="c-header-inner__group-2">
            <span class="c-header-inner__text">lorem ips</span>
            <span class="c-header-inner__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
      <li class="c-header-inner__nav-item">
        <a class="c-header-inner__nav-link" href="#">lorem ips</a>
      </li>
      <li class="c-header-inner__nav-item">
        <a class="c-header-inner__nav-link" href="#">lorem ip</a>
      </li>
      <li class="c-header-inner__nav-item">
        <button class="c-header-inner__cta" type="button">
          <div class="c-header-inner__group-2">
            <span class="c-header-inner__text">lorem ips</span>
            <span class="c-header-inner__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
      <li class="c-header-inner__nav-item">
        <button class="c-header-inner__button" type="button">
          <div class="c-header-inner__group-2">
            <span class="c-header-inner__text">lorem i</span>
            <span class="c-header-inner__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
    </ul>
  </nav>
</div>
```

```css
.c-header-inner-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-inner {
  display: inline-flex;
  align-items: center;
  border-spacing: 0px;
  box-sizing: border-box;
  position: relative;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-inner__group {
  display: block;
  box-sizing: border-box;
  width: 79.8125px;
  height: 1px;
  position: absolute;
  bottom: 0px;
  left: 535.312px;
  z-index: 10001;
  background-color: #0F0E0D;
  opacity: 0.359248;
}

.c-header-inner__nav {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  margin: 0px;
  list-style-type: disc;
}

.c-header-inner__nav-item {
  display: flex;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  height: 100%;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  padding-right: 16px;
  padding-left: 16px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner__cta {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-inner__group-2 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-header-inner__text {
  display: block;
  box-sizing: border-box;
  line-height: 18.2px;
}

.c-header-inner__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: transform, translate, scale, rotate;
}

.c-header-inner__nav-link {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  width: max-content;
  height: 100%;
  color: #0F0E0D;
  cursor: pointer;
  line-height: 18.2px;
  text-decoration-line: none;
  text-align: center;
  white-space: nowrap;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0, 0.7, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner__button {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}
```

**States**

- No hover or focus change was observed.

### Button, primary

**Verification**: verified against the live page at desktop.

**Anatomy**

- `button-primary`: the component root, a `<button>` (`.c-button-primary`)
- `button-primary-label`: label text, 5 characters (`.c-button-primary__label`)
- `button-primary-icon`: icon placeholder, 18px (`.c-button-primary__icon`)

**Recipe**

```html
<div class="c-button-primary-scope">
  <button class="c-button-primary" type="button">
    <span class="c-button-primary__label">lorem</span>
    <span class="c-button-primary__icon" aria-hidden="true"></span>
  </button>
</div>
```

```css
.c-button-primary-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
}

.c-button-primary {
  display: flex;
  align-items: center;
  column-gap: 4px;
  border-spacing: 0px;
  box-sizing: border-box;
  height: 32px;
  padding: 7px 7px 7px 12px;
  background-color: transparent;
  color: #0F0E0D;
  border: 1px solid #0F0E0D;
  border-radius: 4px;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-button-primary__label {
  display: block;
  box-sizing: border-box;
  line-height: 18.2px;
}

.c-button-primary__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 18px;
  height: 18px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: transform, translate, scale, rotate;
}

.c-button-primary:hover {
  background-color: #0F0E0D;
  color: #FAFAF9;
}

.c-button-primary:focus {
  background-color: #0F0E0D;
  color: #FAFAF9;
}
```

**States**

- hover (`button-primary-hover`): background-color #0F0E0D, color #FAFAF9
- focus (`button-primary-focus`): background-color #0F0E0D, color #FAFAF9

### Button, secondary

**Verification**: verified against the live page at desktop.

**Anatomy**

- `button-secondary`: the component root, a `<button>` (`.c-button-secondary`)
- `button-secondary-group`: inner flex row (`.c-button-secondary__group`)
- `button-secondary-label`: label text, 13 characters (`.c-button-secondary__label`)
- `button-secondary-icon`: icon placeholder, 16px (`.c-button-secondary__icon`)

**Recipe**

```html
<div class="c-button-secondary-scope">
  <button class="c-button-secondary" type="button">
    <div class="c-button-secondary__group">
      <span class="c-button-secondary__label">lorem ipsum d</span>
      <span class="c-button-secondary__icon" aria-hidden="true"></span>
    </div>
  </button>
</div>
```

```css
.c-button-secondary-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-button-secondary {
  display: inline-block;
  flex-grow: 1;
  flex-basis: 0%;
  border-spacing: 0px;
  box-sizing: border-box;
  max-width: 100%;
  padding: 20px;
  background-color: transparent;
  color: #8F8B85;
  border: 1px solid #33312C;
  border-radius: 4px;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 20.8px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-button-secondary__group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-button-secondary__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: transform, translate, scale, rotate;
}

.c-button-secondary:hover {
  color: #FAFAF9;
}
```

**States**

- hover (`button-secondary-hover`): color #FAFAF9

### Button, ghost (2)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `button-ghost-2`: the component root, a `<button>` (`.c-button-ghost-2`)
- `button-ghost-2-group`: inner flex row (`.c-button-ghost-2__group`)
- `button-ghost-2-label`: label text, 8 characters (`.c-button-ghost-2__label`)
- `button-ghost-2-icon`: icon placeholder, 16px (`.c-button-ghost-2__icon`)

**Recipe**

```html
<div class="c-button-ghost-2-scope">
  <button class="c-button-ghost-2" type="button">
    <div class="c-button-ghost-2__group">
      <span class="c-button-ghost-2__label">lorem ip</span>
      <span class="c-button-ghost-2__icon" aria-hidden="true"></span>
    </div>
  </button>
</div>
```

```css
.c-button-ghost-2-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
}

.c-button-ghost-2 {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-button-ghost-2__group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-button-ghost-2__label {
  display: block;
  box-sizing: border-box;
  line-height: 18.2px;
}

.c-button-ghost-2__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: transform, translate, scale, rotate;
}
```

**States**

- No hover or focus change was observed.

### Input

**Verification**: verified against the live page at desktop.

**Anatomy**

- `input`: the component root, a `<input>` (`.c-input`), 27-character placeholder

**Recipe**

```html
<div class="c-input-scope">
  <input class="c-input" type="search" placeholder="lorem ipsum dolor sit amet">
</div>
```

```css
.c-input-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-input {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  width: 298px;
  height: 63px;
  padding: 20px 40px 20px 20px;
  overflow-x: clip;
  overflow-y: clip;
  background-color: transparent;
  color: #FAFAF9;
  border: 1px solid #33312C;
  border-radius: 4px;
  cursor: text;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 20.8px;
  letter-spacing: normal;
  text-transform: none;
  text-align: start;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-input:focus {
  border: 1px solid #FAFAF9;
  outline: none;
}
```

**States**

- focus: border 1px solid #FAFAF9, outline none

### Card (3)

**Verification**: flagged, the render matched 8% of the original pixels, below the 96% required (instance 1) after 2 correction attempts.

**Anatomy**

- Group: 6 instances in a 3-column grid, 16px gap; the recipe carries the values they all share
- `card-3`: the component root, a `<a>` (`.c-card-3`)
- `card-3-group`: inner block (`.c-card-3__group`)
- `card-3-group-2`: inner block (`.c-card-3__group-2`)
- `card-3-group-3`: inner block (`.c-card-3__group-3`, 2 instances), content not captured
- `card-3-media`: image placeholder, 448px (`.c-card-3__media`)
- `card-3-group-4`: inner block (`.c-card-3__group-4`)
- `card-3-group-5`: inner flex column (`.c-card-3__group-5`)
- `card-3-media-2`: image placeholder, 120x57px (`.c-card-3__media-2`)
- `card-3-group-6`: inner block (`.c-card-3__group-6`)
- `card-3-group-7`: inner flex column (`.c-card-3__group-7`)
- `card-3-title`: heading, 98 characters (`.c-card-3__title`)

**Recipe**

```html
<div class="c-card-3-scope">
  <a class="c-card-3" href="#">
    <div class="c-card-3__group">
      <div class="c-card-3__group-2">
        <div class="c-card-3__group-3">
          <div class="c-card-3__group-3"></div>
        </div>
      </div>
      <span class="c-card-3__media" aria-hidden="true"></span>
    </div>
    <div class="c-card-3__group-4"></div>
    <div class="c-card-3__group-5">
      <span class="c-card-3__media-2" aria-hidden="true"></span>
      <div class="c-card-3__group-6">
        <div class="c-card-3__group-7">
          <h4 class="c-card-3__title">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lorem ipsum dolor sit</h4>
        </div>
      </div>
    </div>
  </a>
</div>
```

```css
.c-card-3-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card-3 {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  aspect-ratio: 1 / 1;
  position: relative;
  overflow-x: hidden;
  overflow-y: hidden;
  background-color: #0F0E0D;
  color: #FAFAF9;
  border-radius: 8px;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  text-decoration-line: none;
}

.c-card-3__group {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  transition: opacity 0.5s cubic-bezier(0.7, 0, 0.3, 1);
}

.c-card-3__group-2 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-card-3__group-3 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
}

.c-card-3__media {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 448px;
  height: 448px;
  max-width: 100%;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
  transition: opacity 0.3s cubic-bezier(0.7, 0, 0.3, 1);
}

.c-card-3__group-4 {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-image: linear-gradient(to top, #000000 0%, #00000033 20%);
}

.c-card-3__group-5 {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  transition: opacity 0.5s cubic-bezier(0.7, 0, 0.3, 1);
}

.c-card-3__media-2 {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 120px;
  height: 57px;
  max-width: 120px;
  min-height: 32px;
  max-height: 80px;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
  margin-top: 32px;
  margin-left: 32px;
}

.c-card-3__group-6 {
  display: block;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-card-3__group-7 {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 40px;
  box-sizing: border-box;
  padding: 32px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.7, 0, 0.3, 1);
  transition-property: transform, translate, scale, rotate;
}

.c-card-3__title {
  display: block;
  box-sizing: border-box;
  width: 100%;
  margin: 0px;
  font-size: 20px;
  font-weight: 400;
  line-height: 26px;
  letter-spacing: -0.2px;
}
```

**States**

- No hover or focus change was observed.

### Card (4)

**Verification**: verified against the live page at desktop.

**Anatomy**

- Group: 6 instances in a 3-column grid, 16px gap; the recipe carries the values they all share
- `card-4`: the component root, a `<a>` (`.c-card-4`)
- `card-4-group`: inner flex row (`.c-card-4__group`)
- `card-4-group-2`: inner block (`.c-card-4__group-2`)
- `card-4-media`: image placeholder, 84x100px (`.c-card-4__media`)
- `card-4-body`: label text, 71 characters (`.c-card-4__body`)

**Recipe**

```html
<div class="c-card-4-scope">
  <a class="c-card-4" href="#">
    <figure class="c-card-4__group">
      <div class="c-card-4__group-2"></div>
      <span class="c-card-4__media" aria-hidden="true"></span>
    </figure>
    <p class="c-card-4__body">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod t</p>
  </a>
</div>
```

```css
.c-card-4-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card-4 {
  display: inline-flex;
  flex-direction: column;
  gap: 16px;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #FAFAF9;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  text-decoration-line: none;
}

.c-card-4__group {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  aspect-ratio: 4 / 3;
  margin: 0px;
  position: relative;
  overflow-x: hidden;
  overflow-y: hidden;
  border-radius: 4px;
}

.c-card-4__group-2 {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: #1F1D1A;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.c-card-4__media {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 84px;
  height: 100px;
  max-width: 300px;
  max-height: 100px;
  position: relative;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
  border-radius: 4px;
}

.c-card-4__body {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  font-size: 24px;
  font-weight: 500;
  line-height: 31.2px;
}
```

**States**

- No hover or focus change was observed.

### Card (5)

**Verification**: flagged, the `card-5-group` y did not reproduce the measured 43px after 2 correction attempts.

**Anatomy**

- Group: 3 instances in a 1-column grid; the recipe carries the values they all share
- `card-5`: the component root, a `<div>` (`.c-card-5`)
- `card-5-group`: inner block (`.c-card-5__group`)
- `card-5-body`: label text, 21 characters (`.c-card-5__body`)
- `card-5-body-2`: label text, 3 characters (`.c-card-5__body-2`)

**Recipe**

```html
<div class="c-card-5-scope">
  <div class="c-card-5">
    <div class="c-card-5__group">
      <p class="c-card-5__body">lorem ipsum dolor sit</p>
    </div>
    <p class="c-card-5__body-2">lor</p>
  </div>
</div>
```

```css
.c-card-5-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card-5 {
  display: grid;
  align-items: center;
  gap: 16px;
  grid-template-columns: repeat(6, minmax(0px, 1fr));
  border-spacing: 0px;
  box-sizing: border-box;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  padding-top: 32px;
  border-top-width: 2px;
  border-top-style: solid;
  border-top-color: #CCCAC6;
}

.c-card-5__group {
  display: block;
  box-sizing: border-box;
  width: 100%;
  margin-bottom: 16px;
}

.c-card-5__body {
  display: block;
  box-sizing: border-box;
  margin: 0px 0px 16px;
  font-size: 20px;
  line-height: 26px;
}

.c-card-5__body-2 {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 72px;
  line-height: 75.6px;
  letter-spacing: -0.9px;
}

.c-card-5:hover {
  padding: 32px 0px;
}

.c-card-5:focus {
  padding: 32px 0px;
}
```

**States**

- hover: padding 32px 0px
- focus: padding 32px 0px

### Play button

**Verification**: verified against the live page at desktop.

**Anatomy**

- `play-button`: the component root, a `<button>` (`.c-play-button`)

**Recipe**

```html
<div class="c-play-button-scope">
  <button class="c-play-button" type="button"></button>
</div>
```

```css
.c-play-button-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-play-button {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 0px;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}
```

**States**

- No hover or focus change was observed.

### Logo carousel

**Verification**: not verifiable, what the page placed in it (photos, media, ads) covers most of it and nothing else differs, so the comparison could not be judged.

**Anatomy**

- Group: 6 instances in a 24-column grid; the recipe carries the values they all share
- `logo-carousel`: the component root, a `<li>` (`.c-logo-carousel`)
- `logo-carousel-media`: image placeholder, 93x60px (`.c-logo-carousel__media`)

**Recipe**

```html
<div class="c-logo-carousel-scope">
  <li class="c-logo-carousel">
    <span class="c-logo-carousel__media" aria-hidden="true"></span>
  </li>
</div>
```

```css
.c-logo-carousel-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-logo-carousel {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  list-style-type: none;
  padding-right: 24px;
  padding-left: 24px;
}

.c-logo-carousel__media {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 93px;
  height: 60px;
  max-width: 100%;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
}
```

**States**

- No hover or focus change was observed.

### Pagination

**Verification**: verified against the live page at desktop.

**Anatomy**

- `pagination`: the component root, a `<nav>` (`.c-pagination`)
- `pagination-link`: link (`.c-pagination__link`)
- `pagination-icon`: icon placeholder, 20px (`.c-pagination__icon`)
- `pagination-list`: inner flex row (`.c-pagination__list`)
- `pagination-link-active`: link, 1-character label (`.c-pagination__link-active`)
- `pagination-link-2`: link, 1-character label (`.c-pagination__link-2`, 5 instances)
- `pagination-icon-2`: icon placeholder, 20px (`.c-pagination__icon-2`)

**Recipe**

```html
<div class="c-pagination-scope">
  <nav class="c-pagination">
    <a class="c-pagination__link" href="#">
      <span class="c-pagination__icon" aria-hidden="true"></span>
    </a>
    <ul class="c-pagination__list">
      <a class="c-pagination__link-active" href="#">l</a>
      <a class="c-pagination__link-2" href="#">l</a>
      <a class="c-pagination__link-2" href="#">l</a>
      <a class="c-pagination__link-2" href="#">l</a>
      <a class="c-pagination__link-2" href="#">l</a>
      <a class="c-pagination__link-2" href="#">l</a>
    </ul>
    <span class="c-pagination__icon-2" aria-hidden="true"></span>
  </nav>
</div>
```

```css
.c-pagination-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-pagination {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  padding-right: 24px;
}

.c-pagination__link {
  display: block;
  box-sizing: border-box;
  color: #33312C;
  cursor: auto;
  text-decoration-line: none;
  transition: opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.c-pagination__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 20px;
  height: 20px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
}

.c-pagination__list {
  display: flex;
  align-items: center;
  gap: 8px;
  box-sizing: border-box;
  padding: 0px;
  margin: 0px;
  list-style-type: none;
}

.c-pagination__link-active {
  display: inline;
  box-sizing: border-box;
  color: #FAFAF9;
  cursor: pointer;
  font-size: 20px;
  line-height: 26px;
  text-decoration-line: none;
  transition: opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  padding-right: 8px;
  padding-left: 8px;
}

.c-pagination__link-2 {
  display: inline;
  box-sizing: border-box;
  color: #8F8B85;
  cursor: pointer;
  font-size: 20px;
  line-height: 26px;
  text-decoration-line: none;
  transition: opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  padding-right: 8px;
  padding-left: 8px;
}

.c-pagination__icon-2 {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 20px;
  height: 20px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  cursor: pointer;
}
```

**States**

- No hover or focus change was observed.

### Announcement banner (2)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `announcement-banner-2`: the component root, a `<button>` (`.c-announcement-banner-2`)
- `announcement-banner-2-icon`: icon placeholder, 16px (`.c-announcement-banner-2__icon`)

**Recipe**

```html
<div class="c-announcement-banner-2-scope">
  <button class="c-announcement-banner-2" type="button">
    <span class="c-announcement-banner-2__icon" aria-hidden="true"></span>
  </button>
</div>
```

```css
.c-announcement-banner-2-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
}

.c-announcement-banner-2 {
  display: inline-flex;
  flex-shrink: 0;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 50%;
  right: 32px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-announcement-banner-2__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition: opacity 0.3s cubic-bezier(0.3, 0.3, 0.3, 1);
}
```

**States**

- No hover or focus change was observed.

### Header (inner, 2)

**Verification**: desktop verified against the live page at desktop; mobile verified against the live page at mobile.

Variant observed on https://www.harvey.ai/customers.

**Anatomy**

- `header-inner-2`: the component root, a `<header>` (`.c-header-inner-2`)
- `header-inner-2-group`: inner block (`.c-header-inner-2__group`)
- `header-inner-2-group-2`: inner block (`.c-header-inner-2__group-2`)
- `header-inner-2-group-3`: inner grid (`.c-header-inner-2__group-3`)
- `header-inner-2-group-4`: inner flex row (`.c-header-inner-2__group-4`)
- `header-inner-2-group-5`: inner flex row (`.c-header-inner-2__group-5`)
- `header-inner-2-logo`: link (`.c-header-inner-2__logo`)
- `header-inner-2-logo-text`: label text, 80 characters (`.c-header-inner-2__logo-text`)
- `header-inner-2-logo-text-2`: label text, 10 characters (`.c-header-inner-2__logo-text-2`)
- `header-inner-2-menu-toggle`: button (`.c-header-inner-2__menu-toggle`)
- `header-inner-2-menu-toggle-icon`: icon placeholder, 16px (`.c-header-inner-2__menu-toggle-icon`)
- `header-inner-2-inner`: inner flex row (`.c-header-inner-2__inner`)
- `header-inner-2-group-6`: inner flex row (`.c-header-inner-2__group-6`)
- `header-inner-2-group-7`: inner flex row (`.c-header-inner-2__group-7`)
- `header-inner-2-text`: label text, 8 characters (`.c-header-inner-2__text`)
- `header-inner-2-nav`: inner flex row (`.c-header-inner-2__nav`)
- `header-inner-2-nav-list`: inner flex row (`.c-header-inner-2__nav-list`)
- `header-inner-2-nav-item`: inner flex row (`.c-header-inner-2__nav-item`, 6 instances)
- `header-inner-2-cta`: the `button-ghost-2` button (`.c-header-inner-2__cta`, 3 instances)
- `header-inner-2-group-8`: inner flex row (`.c-header-inner-2__group-8`, 4 instances), content not captured
- `header-inner-2-nav-link`: link (`.c-header-inner-2__nav-link`, 2 instances)
- `header-inner-2-group-9`: inner block (`.c-header-inner-2__group-9`, 2 instances), content not captured
- `header-inner-2-menu-toggle-2`: button (`.c-header-inner-2__menu-toggle-2`)
- `header-inner-2-group-10`: inner flex row (`.c-header-inner-2__group-10`)
- `header-inner-2-group-11`: inner flex row (`.c-header-inner-2__group-11`)
- `header-inner-2-group-12`: inner flex row (`.c-header-inner-2__group-12`)
- `header-inner-2-group-13`: inner block (`.c-header-inner-2__group-13`)
- `header-inner-2-cta-2`: the `button-primary` button (`.c-header-inner-2__cta-2`), content not captured
- `header-inner-2-cta-3`: link (`.c-header-inner-2__cta-3`)
- `header-inner-2-text-2`: label text, 14 characters (`.c-header-inner-2__text-2`)

**Desktop recipe**

```html
<div class="c-header-inner-2-scope">
  <header class="c-header-inner-2">
    <div class="c-header-inner-2__group"></div>
    <div class="c-header-inner-2__group-2">
      <div class="c-header-inner-2__group-3">
        <div class="c-header-inner-2__group-4">
          <div class="c-header-inner-2__group-5">
            <a class="c-header-inner-2__logo" href="#">
              <span class="c-header-inner-2__logo-text">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lor</span>
              <span class="c-header-inner-2__logo-text-2">lorem ipsu</span>
            </a>
          </div>
          <button class="c-header-inner-2__menu-toggle" type="button">
            <span class="c-header-inner-2__menu-toggle-icon" aria-hidden="true"></span>
          </button>
        </div>
      </div>
      <div class="c-header-inner-2__inner">
        <div class="c-header-inner-2__group-6">
          <div class="c-header-inner-2__group-7">
            <div class="c-header-inner-2__text">lorem ip</div>
          </div>
          <nav class="c-header-inner-2__nav">
            <ul class="c-header-inner-2__nav-list">
              <li class="c-header-inner-2__nav-item">
                <button class="c-header-inner-2__cta" type="button">
                  <div class="c-header-inner-2__group-8"></div>
                </button>
              </li>
              <li class="c-header-inner-2__nav-item">
                <button class="c-header-inner-2__cta" type="button">
                  <div class="c-header-inner-2__group-8"></div>
                </button>
              </li>
              <li class="c-header-inner-2__nav-item">
                <a class="c-header-inner-2__nav-link" href="#">
                  <div class="c-header-inner-2__group-9"></div>
                </a>
              </li>
              <li class="c-header-inner-2__nav-item">
                <a class="c-header-inner-2__nav-link" href="#">
                  <div class="c-header-inner-2__group-9"></div>
                </a>
              </li>
              <li class="c-header-inner-2__nav-item">
                <button class="c-header-inner-2__cta" type="button">
                  <div class="c-header-inner-2__group-8"></div>
                </button>
              </li>
              <li class="c-header-inner-2__nav-item">
                <button class="c-header-inner-2__menu-toggle-2" type="button">
                  <div class="c-header-inner-2__group-8"></div>
                </button>
              </li>
            </ul>
          </nav>
          <div class="c-header-inner-2__group-10">
            <div class="c-header-inner-2__group-11">
              <div class="c-header-inner-2__group-12">
                <div class="c-header-inner-2__group-13">
                  <button class="c-header-inner-2__cta-2" type="button"></button>
                </div>
              </div>
              <a class="c-header-inner-2__cta-3" href="#">
                <p class="c-header-inner-2__text-2">lorem ipsum do</p>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</div>
```

```css
.c-header-inner-2-scope {
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-inner-2 {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  position: fixed;
  top: 0px;
  right: 0px;
  left: 0px;
  z-index: 100;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__group {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: #0F0E0D99;
  backdrop-filter: blur(16px);
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__group-2 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  position: relative;
}

.c-header-inner-2__group-3 {
  display: grid;
  grid-template-rows: 1fr;
  box-sizing: border-box;
  position: relative;
  z-index: 30;
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-size: 14px;
  line-height: 18.2px;
  text-align: center;
  padding-right: 32px;
  padding-left: 32px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: grid-template-rows, color, background-color;
}

.c-header-inner-2__group-3::after {
  content: "";
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 1440px;
  background-color: #FAFAF9;
}

.c-header-inner-2__group-4 {
  display: flex;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-header-inner-2__group-5 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding-top: 8px;
  padding-bottom: 8px;
}

.c-header-inner-2__logo {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  gap: 10px;
  box-sizing: border-box;
  color: #0F0E0D;
  cursor: pointer;
  text-decoration-line: none;
}

.c-header-inner-2__logo-text-2 {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  position: relative;
  font-weight: 500;
}

.c-header-inner-2__menu-toggle {
  display: flex;
  flex-shrink: 0;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 50%;
  right: 32px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  margin-right: -8px;
}

.c-header-inner-2__menu-toggle-icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition: opacity 0.3s cubic-bezier(0.3, 0.3, 0.3, 1);
}

.c-header-inner-2__inner {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 72px;
  max-width: 1920px;
  position: relative;
  padding-right: 32px;
  padding-left: 32px;
  margin-right: auto;
  margin-left: auto;
}

.c-header-inner-2__group-6 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
}

.c-header-inner-2__group-7 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.c-header-inner-2__text {
  display: block;
  box-sizing: border-box;
  cursor: pointer;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 28px;
  line-height: 39.2px;
}

.c-header-inner-2__nav {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  position: relative;
  margin-right: auto;
  margin-left: 16px;
}

.c-header-inner-2__nav-list {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  margin: 0px;
  list-style-type: disc;
}

.c-header-inner-2__nav-item {
  display: flex;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  height: 100%;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  padding-right: 16px;
  padding-left: 16px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__cta {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-inner-2__group-8 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-header-inner-2__nav-link {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  width: max-content;
  height: 100%;
  color: #FAFAF9;
  cursor: pointer;
  line-height: 18.2px;
  text-decoration-line: none;
  text-align: center;
  white-space: nowrap;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0, 0.7, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__group-9 {
  display: block;
  box-sizing: border-box;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__menu-toggle-2 {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-inner-2__group-10 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
}

.c-header-inner-2__group-11 {
  display: flex;
  align-items: center;
  gap: 16px;
  box-sizing: border-box;
  height: 100%;
}

.c-header-inner-2__group-12 {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__group-13 {
  display: block;
  box-sizing: border-box;
  position: relative;
}

.c-header-inner-2__cta-2 {
  display: flex;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  height: 32px;
  padding: 7px 7px 7px 12px;
  background-color: transparent;
  color: #FAFAF9;
  border: 1px solid #FAFAF9;
  border-radius: 4px;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__cta-3 {
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  height: 32px;
  background-color: #FAFAF9;
  color: #0F0E0D;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 14px;
  text-decoration-line: none;
  white-space: nowrap;
  padding-right: 12px;
  padding-left: 12px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2__text-2 {
  display: block;
  box-sizing: border-box;
  margin: 0px;
}

.c-header-inner-2__cta-2:hover {
  background-color: #FAFAF9;
  color: #0F0E0D;
}

.c-header-inner-2__cta-2:focus {
  background-color: #FAFAF9;
  color: #0F0E0D;
}

.c-header-inner-2__cta-3:hover {
  background-color: #8F8B85;
}

.c-header-inner-2__cta-3:focus {
  box-shadow: transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px;
  outline: none;
}
```

**Mobile anatomy**

- `header-inner-2-mobile`: the component root, a `<header>` (`.c-header-inner-2-mobile`)
- `header-inner-2-mobile-group`: inner block (`.c-header-inner-2-mobile__group`)
- `header-inner-2-mobile-group-2`: inner block (`.c-header-inner-2-mobile__group-2`)
- `header-inner-2-mobile-group-3`: inner grid (`.c-header-inner-2-mobile__group-3`)
- `header-inner-2-mobile-group-4`: inner flex row (`.c-header-inner-2-mobile__group-4`)
- `header-inner-2-mobile-group-5`: inner flex row (`.c-header-inner-2-mobile__group-5`)
- `header-inner-2-mobile-group-6`: inner flex row (`.c-header-inner-2-mobile__group-6`)
- `header-inner-2-mobile-logo`: link (`.c-header-inner-2-mobile__logo`)
- `header-inner-2-mobile-group-7`: inner flex row (`.c-header-inner-2-mobile__group-7`, 2 instances)
- `header-inner-2-mobile-group-8`: inner group (`.c-header-inner-2-mobile__group-8`, 2 instances), content not captured
- `header-inner-2-mobile-logo-text`: label text, 10 characters (`.c-header-inner-2-mobile__logo-text`, 2 instances)
- `header-inner-2-mobile-inner`: inner flex row (`.c-header-inner-2-mobile__inner`)
- `header-inner-2-mobile-group-9`: inner flex row (`.c-header-inner-2-mobile__group-9`)
- `header-inner-2-mobile-group-10`: inner flex row (`.c-header-inner-2-mobile__group-10`)
- `header-inner-2-mobile-text`: label text, 8 characters (`.c-header-inner-2-mobile__text`)
- `header-inner-2-mobile-group-11`: inner flex row (`.c-header-inner-2-mobile__group-11`)
- `header-inner-2-mobile-group-12`: inner flex row (`.c-header-inner-2-mobile__group-12`)
- `header-inner-2-mobile-menu-toggle`: button (`.c-header-inner-2-mobile__menu-toggle`)
- `header-inner-2-mobile-menu-toggle-icon`: icon placeholder, 24x25px (`.c-header-inner-2-mobile__menu-toggle-icon`)

**Mobile recipe**

```html
<div class="c-header-inner-2-mobile-scope">
  <header class="c-header-inner-2-mobile">
    <div class="c-header-inner-2-mobile__group"></div>
    <div class="c-header-inner-2-mobile__group-2">
      <div class="c-header-inner-2-mobile__group-3">
        <div class="c-header-inner-2-mobile__group-4">
          <div class="c-header-inner-2-mobile__group-5">
            <div class="c-header-inner-2-mobile__group-6">
              <a class="c-header-inner-2-mobile__logo" href="#">
                <span class="c-header-inner-2-mobile__group-7">
                  <span class="c-header-inner-2-mobile__group-8"></span>
                  <span class="c-header-inner-2-mobile__logo-text">lorem ipsu</span>
                </span>
                <span class="c-header-inner-2-mobile__group-7">
                  <span class="c-header-inner-2-mobile__group-8"></span>
                  <span class="c-header-inner-2-mobile__logo-text">lorem ipsu</span>
                </span>
              </a>
            </div>
          </div>
        </div>
      </div>
      <div class="c-header-inner-2-mobile__inner">
        <div class="c-header-inner-2-mobile__group-9">
          <div class="c-header-inner-2-mobile__group-10">
            <div class="c-header-inner-2-mobile__text">lorem ip</div>
          </div>
          <div class="c-header-inner-2-mobile__group-11">
            <div class="c-header-inner-2-mobile__group-12">
              <button class="c-header-inner-2-mobile__menu-toggle" type="button">
                <span class="c-header-inner-2-mobile__menu-toggle-icon" aria-hidden="true"></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</div>
```

```css
.c-header-inner-2-mobile-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-inner-2-mobile {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  position: fixed;
  top: 0px;
  right: 0px;
  left: 0px;
  z-index: 100;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2-mobile__group {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: #FAFAF9B8;
  backdrop-filter: blur(16px);
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-2-mobile__group-2 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  position: relative;
}

.c-header-inner-2-mobile__group-3 {
  display: grid;
  grid-template-rows: 1fr;
  box-sizing: border-box;
  position: relative;
  z-index: 30;
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-size: 14px;
  line-height: 18.2px;
  text-align: left;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: grid-template-rows, color, background-color;
}

.c-header-inner-2-mobile__group-3::after {
  content: "";
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 390px;
  background-color: #0F0E0D;
}

.c-header-inner-2-mobile__group-4 {
  display: flex;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-header-inner-2-mobile__group-5 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding-top: 8px;
  padding-bottom: 8px;
}

.c-header-inner-2-mobile__group-6 {
  display: flex;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-header-inner-2-mobile__logo {
  display: flex;
  box-sizing: border-box;
  width: max-content;
  color: #FAFAF9;
  cursor: pointer;
  transform: matrix(1, 0, 0, 1, -134.083, 0);
  text-decoration-line: none;
  white-space: nowrap;
}

.c-header-inner-2-mobile__group-7 {
  display: flex;
  align-items: center;
  gap: 10px;
  box-sizing: border-box;
  padding-right: 16px;
  padding-left: 16px;
}

.c-header-inner-2-mobile__group-8 {
  display: block;
  box-sizing: border-box;
}

.c-header-inner-2-mobile__logo-text {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  font-weight: 500;
}

.c-header-inner-2-mobile__inner {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 72px;
  max-width: 1920px;
  position: relative;
  padding-right: 28px;
  padding-left: 28px;
  margin-right: auto;
  margin-left: auto;
}

.c-header-inner-2-mobile__group-9 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
}

.c-header-inner-2-mobile__group-10 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.c-header-inner-2-mobile__text {
  display: block;
  box-sizing: border-box;
  cursor: pointer;
  font-family: HarveySerifFont, "HarveySerifFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 28px;
  line-height: 39.2px;
}

.c-header-inner-2-mobile__group-11 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
}

.c-header-inner-2-mobile__group-12 {
  display: flex;
  align-items: center;
  gap: 8px;
  box-sizing: border-box;
}

.c-header-inner-2-mobile__menu-toggle {
  display: block;
  box-sizing: border-box;
  padding: 0px;
  position: relative;
  z-index: 30;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-inner-2-mobile__menu-toggle-icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 24px;
  height: 25px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
}

.c-header-inner-2-mobile__logo:focus {
  transform: matrix(1, 0, 0, 1, -188.31, 0);
}
```

**States**

- `header-inner-2-cta-2` hover (`header-inner-2-cta-2-hover`): background-color #FAFAF9, color #0F0E0D
- `header-inner-2-cta-2` focus (`header-inner-2-cta-2-focus`): background-color #FAFAF9, color #0F0E0D
- `header-inner-2-cta-3` hover (`header-inner-2-cta-3-hover`): background-color #8F8B85
- `header-inner-2-cta-3` focus: box-shadow transparent 0px 0px 0px 0px, transparent 0px 0px 0px 0px, #FFFFFF 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, transparent 0px 0px 0px 0px, outline none
- mobile, `header-inner-2-mobile-logo` focus: transform matrix(1, 0, 0, 1, -188.31, 0)

### Button, secondary (2)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `button-secondary-2`: the component root, a `<button>` (`.c-button-secondary-2`)
- `button-secondary-2-icon`: icon placeholder, 24x25px (`.c-button-secondary-2__icon`)

**Recipe**

```html
<div class="c-button-secondary-2-scope">
  <button class="c-button-secondary-2" type="button">
    <span class="c-button-secondary-2__icon" aria-hidden="true"></span>
  </button>
</div>
```

```css
.c-button-secondary-2-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-button-secondary-2 {
  display: flex;
  justify-content: center;
  align-items: center;
  border-spacing: 0px;
  box-sizing: border-box;
  width: 72px;
  aspect-ratio: 1 / 1;
  padding: 0px;
  overflow-x: hidden;
  overflow-y: hidden;
  background-color: #FAFAF933;
  color: #0F0E0D;
  border: 1px solid #FAFAF94D;
  border-radius: 3.35544e+07px;
  backdrop-filter: blur(6px);
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.c-button-secondary-2__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 24px;
  height: 25px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
}
```

**States**

- No hover or focus change was observed.

### Button, ghost (3)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `button-ghost-3`: the component root, a `<button>` (`.c-button-ghost-3`)
- `button-ghost-3-icon`: icon placeholder, 16px (`.c-button-ghost-3__icon`)

**Recipe**

```html
<div class="c-button-ghost-3-scope">
  <button class="c-button-ghost-3" type="button">
    <span class="c-button-ghost-3__icon" aria-hidden="true"></span>
  </button>
</div>
```

```css
.c-button-ghost-3-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
}

.c-button-ghost-3 {
  display: inline-flex;
  flex-shrink: 0;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 50%;
  right: 32px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-button-ghost-3__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition: opacity 0.3s cubic-bezier(0.3, 0.3, 0.3, 1);
}
```

**States**

- No hover or focus change was observed.

### Card (6)

**Verification**: verified against the live page at desktop.

**Anatomy**

- Group: 3 instances in a 1-column grid, 128px gap; the recipe carries the values they all share
- `card-6`: the component root, a `<div>` (`.c-card-6`)
- `card-6-group`: inner flex row (`.c-card-6__group`)
- `card-6-group-2`: inner block (`.c-card-6__group-2`, 2 instances)
- `card-6-title`: heading, 19 characters (`.c-card-6__title`)
- `card-6-body`: label text, 120 characters (`.c-card-6__body`)
- `card-6-group-3`: inner flex row (`.c-card-6__group-3`)
- `card-6-group-4`: inner block (`.c-card-6__group-4`)
- `card-6-media`: image placeholder, 688x516px (`.c-card-6__media`)
- `card-6-media-2`: image placeholder, 688x516px (`.c-card-6__media-2`)
- `card-6-group-5`: inner flex column (`.c-card-6__group-5`)
- `card-6-group-6`: inner block (`.c-card-6__group-6`, 4 instances)
- `card-6-title-2`: heading, 14 characters (`.c-card-6__title-2`, 4 instances)
- `card-6-body-2`: label text, 105 characters (`.c-card-6__body-2`, 4 instances)

**Recipe**

```html
<div class="c-card-6-scope">
  <div class="c-card-6">
    <div class="c-card-6__group">
      <div class="c-card-6__group-2">
        <h3 class="c-card-6__title">lorem ipsum dolor s</h3>
      </div>
      <p class="c-card-6__body">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lorem ipsum dolor sit amet consectetur adip</p>
    </div>
    <div class="c-card-6__group-3">
      <div class="c-card-6__group-2">
        <div class="c-card-6__group-4">
          <span class="c-card-6__media" aria-hidden="true"></span>
          <span class="c-card-6__media-2" aria-hidden="true"></span>
        </div>
      </div>
      <div class="c-card-6__group-5">
        <div class="c-card-6__group-6">
          <h4 class="c-card-6__title-2">lorem ipsum do</h4>
          <p class="c-card-6__body-2">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lorem ipsum dolor sit amet c</p>
        </div>
        <div class="c-card-6__group-6">
          <h4 class="c-card-6__title-2">lorem ipsum dolor</h4>
          <p class="c-card-6__body-2">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lorem ipsum dolor sit amet consect</p>
        </div>
        <div class="c-card-6__group-6">
          <h4 class="c-card-6__title-2">lorem ipsum dolor sit amet</h4>
          <p class="c-card-6__body-2">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod temp</p>
        </div>
        <div class="c-card-6__group-6">
          <h4 class="c-card-6__title-2">lorem ipsum dolor</h4>
          <p class="c-card-6__body-2">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lorem ipsum dolor sit amet consectetur</p>
        </div>
      </div>
    </div>
  </div>
</div>
```

```css
.c-card-6-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card-6 {
  display: inline-flex;
  flex-direction: column;
  border-spacing: 0px;
  box-sizing: border-box;
  max-height: 778px;
  position: sticky;
  top: 106px;
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card-6__group {
  display: flex;
  justify-content: space-between;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 100%;
  padding-top: 32px;
  padding-bottom: 32px;
  margin-bottom: 16px;
  border-top-width: 1px;
  border-top-style: solid;
  border-top-color: #CCCAC6;
}

.c-card-6__group-2 {
  display: block;
  box-sizing: border-box;
  width: 50%;
}

.c-card-6__title {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  font-size: 32px;
  font-weight: 500;
  line-height: 35.2px;
  letter-spacing: -0.32px;
}

.c-card-6__body {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #33312C;
  font-size: 20px;
  font-weight: 500;
  line-height: 26px;
}

.c-card-6__group-3 {
  display: flex;
  justify-content: space-between;
  flex-grow: 1;
  flex-basis: 0%;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-card-6__group-4 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  max-height: 100%;
  aspect-ratio: 1.33399 / 1;
  position: relative;
  overflow-x: hidden;
  overflow-y: hidden;
  border-radius: 8px;
}

.c-card-6__media {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 688px;
  height: 516px;
  max-width: 100%;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
}

.c-card-6__media-2 {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 688px;
  height: 516px;
  max-width: 100%;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  z-index: 10;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
}

.c-card-6__group-5 {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 32px;
  box-sizing: border-box;
  width: 40%;
  padding-right: 64px;
}

.c-card-6__group-6 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  padding-top: 16px;
  border-top-width: 1px;
  border-top-style: solid;
  border-top-color: #CCCAC6;
}

.c-card-6__title-2 {
  display: block;
  box-sizing: border-box;
  margin: 0px 0px 8px;
  font-size: 16px;
  font-weight: 500;
  line-height: 20.8px;
  letter-spacing: -0.16px;
}

.c-card-6__body-2 {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #33312C;
  line-height: 20.8px;
}

.c-card-6:hover {
  z-index: 1;
}

.c-card-6:focus {
  z-index: 1;
}
```

**States**

- hover: z-index 1
- focus: z-index 1

### Card (7)

**Verification**: verified against the live page at desktop.

**Anatomy**

- Group: 4 instances in a 1-column grid, 32px gap; the recipe carries the values they all share
- `card-7`: the component root, a `<div>` (`.c-card-7`)
- `card-7-title`: heading, 14 characters (`.c-card-7__title`)
- `card-7-body`: label text, 105 characters (`.c-card-7__body`)

**Recipe**

```html
<div class="c-card-7-scope">
  <div class="c-card-7">
    <h4 class="c-card-7__title">lorem ipsum do</h4>
    <p class="c-card-7__body">lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor lorem ipsum dolor sit amet c</p>
  </div>
</div>
```

```css
.c-card-7-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-card-7 {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  padding-top: 16px;
  border-top-width: 1px;
  border-top-style: solid;
  border-top-color: #CCCAC6;
}

.c-card-7__title {
  display: block;
  box-sizing: border-box;
  margin: 0px 0px 8px;
  font-size: 16px;
  font-weight: 500;
  line-height: 20.8px;
  letter-spacing: -0.16px;
}

.c-card-7__body {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #33312C;
  line-height: 20.8px;
}
```

**States**

- No hover or focus change was observed.

### Video player

**Verification**: verified against the live page at desktop.

**Anatomy**

- `video-player`: the component root, a `<button>` (`.c-video-player`)
- `video-player-group`: inner group (`.c-video-player__group`)

**Recipe**

```html
<div class="c-video-player-scope">
  <button class="c-video-player" type="button">
    <div class="c-video-player__group"></div>
  </button>
</div>
```

```css
.c-video-player-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-video-player {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 0px;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-video-player__group {
  display: block;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: hidden;
  overflow-y: hidden;
  border-radius: 8px;
  line-height: 0px;
}
```

**States**

- No hover or focus change was observed.

### Link list

**Verification**: verified against the live page at desktop.

**Anatomy**

- `link-list`: the component root, a `<nav>` (`.c-link-list`), content not captured
- `link-list-group`: inner flex column (`.c-link-list__group`, 2 instances)
- `link-list-title`: heading, 8 characters (`.c-link-list__title`, 2 instances)
- `link-list-list`: inner flex column (`.c-link-list__list`, 2 instances)
- `link-list-link`: link, 8-character label (`.c-link-list__link`, 16 instances), content not captured
- `link-list-item`: inner group (`.c-link-list__item`), content not captured

**Recipe**

```html
<div class="c-link-list-scope">
  <nav class="c-link-list">
    <div class="c-link-list__group">
      <h3 class="c-link-list__title">lorem ip</h3>
      <ul class="c-link-list__list">
        <a class="c-link-list__link" href="#">lorem ip</a>
        <a class="c-link-list__link" href="#">lorem</a>
        <a class="c-link-list__link" href="#">lorem</a>
        <a class="c-link-list__link" href="#">lorem ips</a>
        <a class="c-link-list__link" href="#">lorem</a>
        <a class="c-link-list__link" href="#">lorem ipsum do</a>
        <a class="c-link-list__link" href="#">lorem ipsum dolor sit</a>
        <a class="c-link-list__link" href="#">lorem ipsum dolo</a>
        <a class="c-link-list__link" href="#">lorem ips</a>
        <a class="c-link-list__link" href="#">lorem ipsum d</a>
        <a class="c-link-list__link" href="#">lorem ipsum</a>
      </ul>
    </div>
    <div class="c-link-list__group">
      <h3 class="c-link-list__title">lorem ips</h3>
      <ul class="c-link-list__list">
        <a class="c-link-list__link" href="#">lorem ipsu</a>
        <a class="c-link-list__link" href="#">lorem ipsum d</a>
        <a class="c-link-list__link" href="#">lorem ipsu</a>
        <a class="c-link-list__link" href="#">lorem ip</a>
        <a class="c-link-list__link" href="#">lorem ips</a>
        <li class="c-link-list__item"></li>
      </ul>
    </div>
  </nav>
</div>
```

```css
.c-link-list-scope {
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-link-list {
  display: inline-grid;
  gap: 16px;
  grid-template-columns: repeat(5, minmax(0px, 1fr));
  border-spacing: 0px;
  box-sizing: border-box;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-link-list__group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}

.c-link-list__title {
  display: block;
  box-sizing: border-box;
  margin: 0px;
  color: #8F8B85;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  letter-spacing: -0.14px;
}

.c-link-list__list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  padding: 0px;
  margin: 0px;
  list-style-type: none;
}

.c-link-list__link {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  color: #FAFAF9;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 18.2px;
  text-decoration-line: none;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.7, 0, 0.3, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-link-list__item {
  display: list-item;
  box-sizing: border-box;
}
```

**States**

- No hover or focus change was observed.

### Banner

**Verification**: flagged, the render matched 5% of the original pixels, below the 96% required after 2 correction attempts.

**Anatomy**

- `banner`: the component root, a `<header>` (`.c-banner`)
- `banner-group`: inner block (`.c-banner__group`)
- `banner-group-2`: inner block (`.c-banner__group-2`)
- `banner-group-3`: inner grid (`.c-banner__group-3`)
- `banner-group-4`: inner flex row (`.c-banner__group-4`)
- `banner-group-5`: inner flex row (`.c-banner__group-5`), content not captured
- `banner-button`: button (`.c-banner__button`), content not captured
- `banner-group-6`: inner flex row (`.c-banner__group-6`)
- `banner-group-7`: inner flex row (`.c-banner__group-7`)
- `banner-group-8`: inner flex row (`.c-banner__group-8`), content not captured
- `banner-group-9`: inner flex row (`.c-banner__group-9`), content not captured
- `banner-group-10`: inner flex row (`.c-banner__group-10`), content not captured

**Recipe**

```html
<div class="c-banner-scope">
  <header class="c-banner">
    <div class="c-banner__group"></div>
    <div class="c-banner__group-2">
      <div class="c-banner__group-3">
        <div class="c-banner__group-4">
          <div class="c-banner__group-5"></div>
          <button class="c-banner__button" type="button"></button>
        </div>
      </div>
      <div class="c-banner__group-6">
        <div class="c-banner__group-7">
          <div class="c-banner__group-8"></div>
          <nav class="c-banner__group-9"></nav>
          <div class="c-banner__group-10"></div>
        </div>
      </div>
    </div>
  </header>
</div>
```

```css
.c-banner-scope {
  background-color: #0F0E0D;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-banner {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  position: fixed;
  top: 0px;
  right: 0px;
  left: 0px;
  z-index: 100;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-banner__group {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: #0F0E0D99;
  backdrop-filter: blur(16px);
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-banner__group-2 {
  display: block;
  box-sizing: border-box;
  width: 100%;
  position: relative;
}

.c-banner__group-3 {
  display: grid;
  grid-template-rows: 1fr;
  box-sizing: border-box;
  position: relative;
  z-index: 30;
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-size: 14px;
  line-height: 18.2px;
  text-align: center;
  padding-right: 32px;
  padding-left: 32px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: grid-template-rows, color, background-color;
}

.c-banner__group-3::after {
  content: "";
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 1440px;
  background-color: #FAFAF9;
}

.c-banner__group-4 {
  display: flex;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: hidden;
}

.c-banner__group-5 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding-top: 8px;
  padding-bottom: 8px;
}

.c-banner__button {
  display: flex;
  flex-shrink: 0;
  box-sizing: border-box;
  padding: 8px;
  position: absolute;
  top: 50%;
  right: 32px;
  background-color: transparent;
  color: #0F0E0D;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  margin-right: -8px;
}

.c-banner__group-6 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 72px;
  max-width: 1920px;
  position: relative;
  padding-right: 32px;
  padding-left: 32px;
  margin-right: auto;
  margin-left: auto;
}

.c-banner__group-7 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  position: relative;
}

.c-banner__group-8 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.c-banner__group-9 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  position: relative;
  margin-right: auto;
  margin-left: 16px;
}

.c-banner__group-10 {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
}
```

**States**

- No hover or focus change was observed.

### Breadcrumb

**Verification**: verified against the live page at desktop.

**Anatomy**

- `breadcrumb`: the component root, a `<nav>` (`.c-breadcrumb`)
- `breadcrumb-list`: inner flex row (`.c-breadcrumb__list`)
- `breadcrumb-item`: inner group (`.c-breadcrumb__item`, 2 instances)
- `breadcrumb-link`: link (`.c-breadcrumb__link`)
- `breadcrumb-text`: label text, 8 characters (`.c-breadcrumb__text`, 2 instances)
- `breadcrumb-text-active`: label text, 14 characters (`.c-breadcrumb__text-active`)

**Recipe**

```html
<div class="c-breadcrumb-scope">
  <nav class="c-breadcrumb">
    <ol class="c-breadcrumb__list">
      <li class="c-breadcrumb__item">
        <a class="c-breadcrumb__link" href="#">
          <span class="c-breadcrumb__text">lorem ip</span>
          <span class="c-breadcrumb__text">l</span>
        </a>
      </li>
      <li class="c-breadcrumb__item">
        <span class="c-breadcrumb__text-active">lorem ipsum do</span>
      </li>
    </ol>
  </nav>
</div>
```

```css
.c-breadcrumb-scope {
  background-color: #FAFAF9;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-breadcrumb {
  display: inline-block;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #0F0E0D;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-breadcrumb__list {
  display: flex;
  flex-wrap: wrap;
  box-sizing: border-box;
  padding: 0px;
  margin: 0px;
  list-style-type: none;
}

.c-breadcrumb__item {
  display: list-item;
  box-sizing: border-box;
  color: #706D66;
  font-weight: 500;
  line-height: 20.8px;
}

.c-breadcrumb__link {
  display: inline;
  box-sizing: border-box;
  color: #706D66;
  cursor: pointer;
  text-decoration-line: none;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0, 0.7, 0.3, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-breadcrumb__text-active {
  display: inline;
  box-sizing: border-box;
  color: #0F0E0D;
}
```

**States**

- No hover or focus change was observed.

### Header (inner, 3)

**Verification**: verified against the live page at desktop.

Variant observed on https://www.harvey.ai/platform/command-center.

**Anatomy**

- `header-inner-3`: the component root, a `<nav>` (`.c-header-inner-3`)
- `header-inner-3-nav`: inner flex row (`.c-header-inner-3__nav`)
- `header-inner-3-nav-item`: inner flex row (`.c-header-inner-3__nav-item`, 6 instances)
- `header-inner-3-cta`: the `button-ghost` button (`.c-header-inner-3__cta`, 2 instances)
- `header-inner-3-group`: inner flex row (`.c-header-inner-3__group`, 4 instances)
- `header-inner-3-text`: label text, 8 characters (`.c-header-inner-3__text`, 4 instances)
- `header-inner-3-icon`: icon placeholder, 16px (`.c-header-inner-3__icon`, 4 instances)
- `header-inner-3-nav-link`: link, 9-character label (`.c-header-inner-3__nav-link`, 2 instances)
- `header-inner-3-button`: button (`.c-header-inner-3__button`, 2 instances)

**Recipe**

```html
<div class="c-header-inner-3-scope">
  <nav class="c-header-inner-3">
    <ul class="c-header-inner-3__nav">
      <li class="c-header-inner-3__nav-item">
        <button class="c-header-inner-3__cta" type="button">
          <div class="c-header-inner-3__group">
            <span class="c-header-inner-3__text">lorem ip</span>
            <span class="c-header-inner-3__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
      <li class="c-header-inner-3__nav-item">
        <button class="c-header-inner-3__cta" type="button">
          <div class="c-header-inner-3__group">
            <span class="c-header-inner-3__text">lorem ips</span>
            <span class="c-header-inner-3__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
      <li class="c-header-inner-3__nav-item">
        <a class="c-header-inner-3__nav-link" href="#">lorem ips</a>
      </li>
      <li class="c-header-inner-3__nav-item">
        <a class="c-header-inner-3__nav-link" href="#">lorem ip</a>
      </li>
      <li class="c-header-inner-3__nav-item">
        <button class="c-header-inner-3__button" type="button">
          <div class="c-header-inner-3__group">
            <span class="c-header-inner-3__text">lorem ips</span>
            <span class="c-header-inner-3__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
      <li class="c-header-inner-3__nav-item">
        <button class="c-header-inner-3__button" type="button">
          <div class="c-header-inner-3__group">
            <span class="c-header-inner-3__text">lorem i</span>
            <span class="c-header-inner-3__icon" aria-hidden="true"></span>
          </div>
        </button>
      </li>
    </ul>
  </nav>
</div>
```

```css
.c-header-inner-3-scope {
  background-color: #0F0E0D;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-inner-3 {
  display: inline-flex;
  align-items: center;
  border-spacing: 0px;
  box-sizing: border-box;
  position: relative;
  color: #FAFAF9;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-header-inner-3__nav {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  margin: 0px;
  list-style-type: disc;
}

.c-header-inner-3__nav-item {
  display: flex;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  height: 100%;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  padding-right: 16px;
  padding-left: 16px;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0.3, 0.3, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-3__cta {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}

.c-header-inner-3__group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
}

.c-header-inner-3__text {
  display: block;
  box-sizing: border-box;
  line-height: 18.2px;
}

.c-header-inner-3__icon {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 16px;
  height: 16px;
  overflow-x: hidden;
  overflow-y: hidden;
  vertical-align: middle;
  background-color: currentcolor;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: transform, translate, scale, rotate;
}

.c-header-inner-3__nav-link {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 4px;
  box-sizing: border-box;
  width: max-content;
  height: 100%;
  color: #FAFAF9;
  cursor: pointer;
  line-height: 18.2px;
  text-decoration-line: none;
  text-align: center;
  white-space: nowrap;
  transition-duration: 0.3s;
  transition-timing-function: cubic-bezier(0, 0.7, 0.3, 1);
  transition-property: color, background-color, border-color, fill, stroke;
}

.c-header-inner-3__button {
  display: block;
  box-sizing: border-box;
  height: 100%;
  padding: 0px;
  background-color: transparent;
  color: #FAFAF9;
  border: 0;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
}
```

**States**

- No hover or focus change was observed.

### Button, primary (2)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `button-primary-2`: the component root, a `<button>` (`.c-button-primary-2`), 6-character label

**Recipe**

```html
<div class="c-button-primary-2-scope">
  <button class="c-button-primary-2" type="button">lorem</button>
</div>
```

```css
.c-button-primary-2-scope {
  background-color: #FAFAF9;
  color: #333333;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 19.5px;
}

.c-button-primary-2 {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  flex-basis: 0%;
  border-spacing: 0px;
  box-sizing: border-box;
  height: 48px;
  padding: 0px 20px;
  background-color: #0F0E0D;
  color: #FAFAF9;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 500;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: center;
  appearance: button;
  transition: all 0.2s ease-in-out;
}

.c-button-primary-2:hover {
  background-color: #33312C;
}

.c-button-primary-2:focus {
  box-shadow: #8F8B85 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px;
  outline: none;
}
```

**States**

- hover (`button-primary-2-hover`): background-color #33312C
- focus: box-shadow #8F8B85 0px 0px 0px 2px, #8F8B85 0px 0px 0px 4px, outline none

### Input (2)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `input-2`: the component root, a `<input>` (`.c-input-2`), 10-character placeholder

**Recipe**

```html
<div class="c-input-2-scope">
  <input class="c-input-2" type="text" placeholder="lorem ipsu">
</div>
```

```css
.c-input-2-scope {
  background-color: #FAFAF9;
  color: #333333;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 19.5px;
}

.c-input-2 {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  width: 352px;
  height: 48px;
  min-height: 30.4px;
  padding: 0px 16px;
  position: relative;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: clip;
  overflow-y: clip;
  background-color: transparent;
  color: #0F0E0D;
  border: 1px solid #ADABA5;
  border-radius: 4px;
  cursor: text;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: start;
  appearance: none;
  transition: all 0.2s ease-in-out;
}

.c-input-2:hover {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  border: 1px solid #0F0E0D;
}

.c-input-2:focus {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  border: 1px solid #0F0E0D;
  outline: none;
}
```

**States**

- hover: top auto, right auto, bottom auto, left auto, border 1px solid #0F0E0D
- focus: top auto, right auto, bottom auto, left auto, border 1px solid #0F0E0D, outline none

### Select

**Verification**: verified against the live page at desktop.

**Anatomy**

- `select`: the component root, a `<select>` (`.c-select`), 9-character placeholder

**Recipe**

```html
<div class="c-select-scope">
  <select class="c-select"><option>lorem ips</option></select>
</div>
```

```css
.c-select-scope {
  background-color: #FAFAF9;
  color: #333333;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 19.5px;
}

.c-select {
  display: block;
  align-items: center;
  border-spacing: 0px;
  box-sizing: border-box;
  width: 736px;
  height: 48px;
  min-height: 30.4px;
  padding: 0px 40px 0px 16px;
  position: relative;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 1px solid #ADABA5;
  border-radius: 4px;
  cursor: default;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: start;
  white-space: pre;
  appearance: none;
  transition: all 0.2s ease-in-out;
}

.c-select:hover {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  border: 1px solid #0F0E0D;
}

.c-select:focus {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  border: 1px solid #0F0E0D;
  outline: none;
}
```

**States**

- hover: top auto, right auto, bottom auto, left auto, border 1px solid #0F0E0D
- focus: top auto, right auto, bottom auto, left auto, border 1px solid #0F0E0D, outline none

### Select (2)

**Verification**: verified against the live page at desktop.

**Anatomy**

- `select-2`: the component root, a `<select>` (`.c-select-2`), 9-character placeholder

**Recipe**

```html
<div class="c-select-2-scope">
  <select class="c-select-2"><option>lorem ips</option></select>
</div>
```

```css
.c-select-2-scope {
  background-color: #FAFAF9;
  color: #333333;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 19.5px;
}

.c-select-2 {
  display: block;
  align-items: center;
  border-spacing: 0px;
  box-sizing: border-box;
  width: 352px;
  height: 48px;
  min-height: 30.4px;
  padding: 0px 40px 0px 16px;
  position: relative;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 1px solid #ADABA5;
  border-radius: 4px;
  cursor: default;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: start;
  white-space: pre;
  appearance: none;
  transition: all 0.2s ease-in-out;
}

.c-select-2:hover {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  border: 1px solid #0F0E0D;
}

.c-select-2:focus {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  border: 1px solid #0F0E0D;
  outline: none;
}
```

**States**

- hover: top auto, right auto, bottom auto, left auto, border 1px solid #0F0E0D
- focus: top auto, right auto, bottom auto, left auto, border 1px solid #0F0E0D, outline none

### Form field group

**Verification**: verified against the live page at desktop.

**Anatomy**

- Group: 4 instances in a 1-column grid; the recipe carries the values they all share
- `form-field-group`: the component root, a `<div>` (`.c-form-field-group`)
- `form-field-group-group`: inner flex column (`.c-form-field-group__group`)
- `form-field-group-group-2`: inner flex column (`.c-form-field-group__group-2`, 2 instances)
- `form-field-group-group-3`: inner group (`.c-form-field-group__group-3`, 2 instances)
- `form-field-group-text`: label text, 1 characters (`.c-form-field-group__text`, 2 instances)
- `form-field-group-text-2`: label text, 11 characters (`.c-form-field-group__text-2`, 2 instances)
- `form-field-group-field`: inner group (`.c-form-field-group__field`, 2 instances)
- `form-field-group-group-4`: inner block (`.c-form-field-group__group-4`)

**Recipe**

```html
<div class="c-form-field-group-scope">
  <div class="c-form-field-group">
    <div class="c-form-field-group__group">
      <div class="c-form-field-group__group-2">
        <label class="c-form-field-group__group-3">
          <div class="c-form-field-group__text">l</div>
          <span class="c-form-field-group__text-2">lorem ipsum</span>
        </label>
        <div class="c-form-field-group__field"></div>
      </div>
    </div>
    <div class="c-form-field-group__group-4">
      <div class="c-form-field-group__group-2">
        <label class="c-form-field-group__group-3">
          <div class="c-form-field-group__text">l</div>
          <span class="c-form-field-group__text-2">lorem ipsu</span>
        </label>
        <div class="c-form-field-group__field"></div>
      </div>
    </div>
  </div>
</div>
```

```css
.c-form-field-group-scope {
  background-color: #FAFAF9;
  color: #333333;
  font-family: Helvetica, Arial, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 19.5px;
}

.c-form-field-group {
  display: inline-grid;
  justify-content: center;
  gap: 32px;
  grid-template-columns: repeat(2, 1fr);
  border-spacing: 0px;
  box-sizing: border-box;
  color: #333333;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 19.5px;
  text-align: left;
}

.c-form-field-group__group {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  width: 100%;
  min-height: 26px;
  position: relative;
}

.c-form-field-group__group-2 {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  width: 100%;
  position: relative;
  margin-top: auto;
  margin-bottom: 16px;
}

.c-form-field-group__group-3 {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: fit-content;
  position: relative;
  color: #0F0E0D;
  cursor: default;
  font-size: 16px;
  line-height: 20.8px;
  margin-bottom: 8px;
}

.c-form-field-group__text {
  display: block;
  box-sizing: border-box;
  position: absolute;
  top: 2px;
  right: -10px;
  padding-left: 5px;
}

.c-form-field-group__field {
  display: block;
  box-sizing: border-box;
  width: 352px;
  height: 48px;
  min-height: 30.4px;
  padding: 0px 16px;
  position: relative;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  overflow-x: clip;
  overflow-y: clip;
  background-color: transparent;
  color: #0F0E0D;
  border: 1px solid #ADABA5;
  border-radius: 4px;
  cursor: text;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  letter-spacing: normal;
  text-transform: none;
  text-align: start;
  appearance: none;
  transition: all 0.2s ease-in-out;
}

.c-form-field-group__group-4 {
  box-sizing: border-box;
}
```

**States**

- No hover or focus change was observed.

### Logo item

**Verification**: not verifiable, what the page placed in it (photos, media, ads) covers most of it and nothing else differs, so the comparison could not be judged.

**Anatomy**

- Group: 6 instances in a 19-column grid; the recipe carries the values they all share
- `logo-item`: the component root, a `<li>` (`.c-logo-item`)
- `logo-item-media`: image placeholder, 93x60px (`.c-logo-item__media`)

**Recipe**

```html
<div class="c-logo-item-scope">
  <li class="c-logo-item">
    <span class="c-logo-item__media" aria-hidden="true"></span>
  </li>
</div>
```

```css
.c-logo-item-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-logo-item {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  border-spacing: 0px;
  box-sizing: border-box;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  list-style-type: none;
  padding-right: 24px;
  padding-left: 24px;
}

.c-logo-item__media {
  display: block;
  flex-shrink: 0;
  box-sizing: border-box;
  width: 93px;
  height: 60px;
  max-width: 100%;
  overflow-x: clip;
  overflow-y: clip;
  vertical-align: middle;
  background-color: currentcolor;
}
```

**States**

- No hover or focus change was observed.

### Checkbox

**Verification**: verified against the live page at desktop.

**Anatomy**

- `checkbox`: the component root, a `<input>` (`.c-checkbox`), 3-character placeholder

**Recipe**

```html
<div class="c-checkbox-scope">
  <input class="c-checkbox" type="text" placeholder="lor">
</div>
```

```css
.c-checkbox-scope {
  background-color: #FAFAF9;
  color: #333333;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 19.5px;
}

.c-checkbox {
  display: block;
  border-spacing: 0px;
  box-sizing: border-box;
  width: 20px;
  height: 20px;
  padding: 0px;
  position: relative;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: transparent;
  color: #0F0E0D;
  border: 1px solid #ADABA5;
  border-radius: 4px;
  cursor: pointer;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 19.2px;
  letter-spacing: normal;
  text-transform: none;
  text-align: start;
  appearance: none;
  transition: border-color 0.2s ease-in-out;
}

.c-checkbox:hover {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  border: 1px solid #0F0E0D;
}

.c-checkbox:focus {
  top: auto;
  right: auto;
  bottom: auto;
  left: auto;
  outline: none;
}
```

**States**

- hover: top auto, right auto, bottom auto, left auto, border 1px solid #0F0E0D
- focus: top auto, right auto, bottom auto, left auto, outline none

### Footer (inner)

**Verification**: desktop verified against the live page at desktop; mobile flagged, the render matched 95% of the original pixels, below the 96% required after 2 correction attempts.

Variant observed on https://www.harvey.ai/contact-sales.

**Anatomy**

- `footer-inner`: the component root, a `<footer>` (`.c-footer-inner`)
- `footer-inner-link`: link, 8-character label (`.c-footer-inner__link`, 2 instances)
- `footer-inner-text`: label text, 28 characters (`.c-footer-inner__text`)

**Desktop recipe**

```html
<div class="c-footer-inner-scope">
  <footer class="c-footer-inner">
    <a class="c-footer-inner__link" href="#">lorem ip</a>
    <a class="c-footer-inner__link" href="#">lorem</a>
    <span class="c-footer-inner__text">lorem ipsum dolor sit amet c</span>
  </footer>
</div>
```

```css
.c-footer-inner-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-inner {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 16px;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 32px;
  position: relative;
  z-index: 10;
  background-color: #FAFAF9;
  color: #706D66;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
}

.c-footer-inner__link {
  display: block;
  box-sizing: border-box;
  color: #706D66;
  cursor: pointer;
  font-weight: 500;
  text-decoration-line: none;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-footer-inner__text {
  display: block;
  box-sizing: border-box;
  font-weight: 500;
}

.c-footer-inner__link:hover {
  color: #0F0E0D;
}
```

**Mobile anatomy**

- `footer-inner-mobile`: the component root, a `<footer>` (`.c-footer-inner-mobile`)
- `footer-inner-mobile-link`: link, 8-character label (`.c-footer-inner-mobile__link`, 2 instances)
- `footer-inner-mobile-text`: label text, 28 characters (`.c-footer-inner-mobile__text`)

**Mobile recipe**

```html
<div class="c-footer-inner-mobile-scope">
  <footer class="c-footer-inner-mobile">
    <a class="c-footer-inner-mobile__link" href="#">lorem ip</a>
    <a class="c-footer-inner-mobile__link" href="#">lorem</a>
    <span class="c-footer-inner-mobile__text">lorem ipsum dolor sit amet c</span>
  </footer>
</div>
```

```css
.c-footer-inner-mobile-scope {
  background-color: #FAFAF9;
  color: #FFFFFF;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
}

.c-footer-inner-mobile {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 14px;
  border-spacing: 0px;
  box-sizing: border-box;
  padding: 28px;
  position: relative;
  z-index: 10;
  background-color: #FAFAF9;
  color: #706D66;
  font-family: HarveySansFont, "HarveySansFont Fallback", -apple-system, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif, sans-serif;
  font-size: 14px;
  font-weight: 400;
  line-height: 18.2px;
}

.c-footer-inner-mobile__link {
  display: block;
  box-sizing: border-box;
  color: #706D66;
  cursor: pointer;
  font-weight: 500;
  text-decoration-line: none;
  transition-duration: 0.15s;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to;
}

.c-footer-inner-mobile__text {
  display: block;
  box-sizing: border-box;
  font-weight: 500;
}

.c-footer-inner-mobile__link:hover {
  color: #0F0E0D;
}
```

**States**

- `footer-inner-link` hover (`footer-inner-link-hover`): color #0F0E0D
- mobile, `footer-inner-mobile-link` hover (`footer-inner-mobile-link-hover`): color #0F0E0D

## Do's and Don'ts

### Do
- **Set headlines in the serif at 400.** Use `hero-display`, `display-lg`, `display-md` or `display-sm`, all `HarveySerifFont` at weight 400 with their negative tracking. Keep UI copy in `HarveySansFont`.
- **Use only weights 400 and 500.** 500 is the sans emphasis cut (`label`, `body-strong`, `headline`).
- **Keep controls at `rounded.sm` (4px).** The site does this across `button-primary`, `button-secondary`, `button-primary-2`, `input-2`, `select` and `checkbox`. Large media cards take `rounded.md` (8px) (`card-6-group-4`, `video-player-group`).
- **Use the measured control heights.** Compact outlined CTAs are 32px (`button-primary`). The solid Ink CTA and form fields are 48px (`button-primary-2`, `input-2`, `select`, `select-2`). The dark newsletter field and its button are 63px (`input`, `button-secondary`). Nav buttons fill the 72px bar (`button-ghost`, `navigation-button`).
- **Reserve the solid Ink fill for the main CTA.** Solid **Ink** (`primary`, #0F0E0D) is the main CTA fill (`button-primary-2`), hovering to `ink-secondary`. The compact `button-primary` is outlined in Ink and fills with Ink on hover and focus.
- **Keep the frosted header.** Fixed headers and banners use translucent fills with `blur(16px)` (`header-landing-group`, `announcement-banner-group`). The frosted media control uses `blur(6px)` (`button-secondary-2`).
- **Separate list and stat rows with hairlines.** Use a 1px `hairline` top rule (`card-6-group`, `card-7`) and a 2px rule for stats (`card-5`). On dark, use `border-dark` (`footer-landing-columns`).
- **Space sections at 64px.** Use `section-padding-y` between sections and alternate off-white and Ink bands for structure.

### Don't
- **Don't introduce a brand hue.** There is no blue or purple accent. `highlight` (#F6F202) is a rare marker, and `focus-ring` / `focus-ring-strong` are for focus only.
- **Don't bold the serif, and don't add weights.** No 300 or 600+.
- **Don't put drop shadows on cards or buttons.** The soft shadow (`rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.1) 0px 4px 6px -4px`) belongs to floating overlays only. Dark-section cards lift with `surface-dark`.
- **Don't make the header opaque.** Never replace the frosted blur with a solid fill.
- **Don't pill-round text buttons or nav items.** Keep `rounded.full` for round icon or media controls.
- **Don't use pure black for text.** `surface-black` is for media backdrops; text is `ink`.
- **Don't add a third typeface.** No mono and no display script.
- **Don't use gradients for fills.** Every fill is flat.

## Responsive Behavior

### Scope
This analysis is **two-viewport only** (desktop and mobile). No intermediate breakpoints were observed, so none are specified here.

### What changes on mobile
- **Header.** The header keeps its 106px stack of announcement bar plus nav (`header-landing-mobile`, `header-inner-2-mobile`). The desktop nav links and ghost CTAs collapse into a single hamburger toggle (`header-landing-mobile-menu-toggle`, 24x25px icon). The frosted `blur(16px)` layer remains, sitting on a translucent off-white fill (`header-landing-mobile-group`, #FAFAF9B8). The announcement strip is solid Ink (`header-landing-mobile-group-3`, #0F0E0D). The logo row tightens to a 10px gap (`header-landing-mobile-gap`).
- **Footer.** The dark footer stays `footer-landing-mobile` on #0F0E0D. Its link columns re-flow into a narrower grid with a wider 28px column gap (`footer-landing-mobile-column-gap`) and 14px stacks (`footer-landing-mobile-gap`). The footer grows from 699px (`footer-landing`) to 1435px (`footer-landing-mobile`) as columns stack. The light legal bar `footer-inner-mobile` (flagged: the render matched 95% of the original pixels, below the 96% required) reduces its padding to 28px.
- **Content.** In the screenshots, the two-column hero, card rows and text/media feature splits all stack to a single column. Cards go full-width, logo walls drop to fewer columns, and the cookie modal stacks its buttons.
- **Type.** Serif statement text in the header keeps 28px (`header-landing-mobile-text`). The rest of the display ladder was not separately measured at mobile.

### Touch targets
- **Comfortable.** The main touch-sized controls are 48px: `button-primary-2`, `input-2`, `select`.
- **Small.** Compact icon buttons are 32px (`close-button`, `button-ghost-3`). The mobile menu toggle measures only 24x25px (`header-landing-mobile-menu-toggle`). When rebuilding, pad these hit areas toward 44–48px without changing their visual size.

## Iteration Guide

1. **Reference tokens, never hex.** Use `ink`, `ink-secondary`, `muted`, `muted-soft`, `hairline`, `border-strong`, `border-dark`, `surface`, `surface-muted`, `surface-dark`. If you need the warm off-white seen in components (#FAFAF9), map it to `surface` unless the task demands exact parity.
2. **Respect the two-family, two-weight rule.** Serif tokens (`hero-display`, `display-lg`, `display-md`, `display-sm`) are always 400. Sans tokens use 400 or 500. A new size must follow the tracking curve (about -1% of size for 24px and up, normal for 20px and below) and the leading curve (1.05 for display, 1.3 for UI, 1.5 for long body).
3. **Build variants from existing recipes.**
   - Solid CTA: `button-primary-2` (Ink fill, 48px, `rounded.sm`).
   - Compact outlined CTA: `button-primary` (32px, 1px Ink border).
   - Dark-band outlined: `button-secondary`.
   - Nav items: ghost buttons (`button-ghost`, `button-ghost-2`).
   - Forms: `input-2`, `select` and `checkbox` with a `border-strong` resting border that turns Ink on hover and focus.
4. **Elevation boundaries are fixed.** Tone first (`surface-dark` tiles on Ink bands), hairlines second, `blur(16px)` frosted glass for anything pinned, and the soft shadow only for true overlays. Focus uses spread-only box-shadow rings. Never shadow a card.
5. **Radius is binary.** `rounded.sm` for controls and small cards, `rounded.md` for large media. `rounded.full` only for circular icon or media controls. Don't invent intermediate radii.
6. **Keep the macro rhythm.** Sections separate with `section-padding-y` (64px) and band color flips. Card rows use `card-4-grid-gap` / `card-4-grid-row-gap`, feature rows `card-6-grid-gap`, lists `card-7-grid-gap`.
7. **Color accent stays rare.** `highlight` may appear as a small mark at most once per view. Blue (`focus-ring`, `focus-ring-strong`) is reserved for focus states. Never introduce new hues.

## Known Gaps

- **Pages.** All 5 captured pages succeeded: home, a blog article, customers, platform/command-center and contact-sales. No grounded values were dropped, but auth-walled product surfaces (the actual Harvey app) were not reachable.
- **Flagged recipes.** These did not reproduce exactly and should be treated as approximate:
  - `hero` (flagged: the `hero-title` y did not reproduce the measured 64px)
  - `header-landing` (flagged: the render matched 5% of the original pixels, below the 96% required)
  - `banner` (flagged: the render matched 5% of the original pixels)
  - `card-3` (flagged: the render matched 8% of the original pixels)
  - `card-5` (flagged: the `card-5-group` y did not reproduce the measured 43px)
  - `footer-inner-mobile` (flagged: the render matched 95% of the original pixels)
- **Unverifiable recipes.** `card-2`, `logo-carousel` and `logo-item` are not verifiable: photos and media covered most of each component, so the comparison could not be judged.
- **Focus-ring colors.** `focus-ring` (#99C8FF) and `focus-ring-strong` (#005FCC) were measured only on component states, never in page sampling. Their exact application points are uncertain; the visible focus rings on recipes use Paper and Pebble greys.
- **Untokenized colors.**
  - The warm off-white #FAFAF9 is used widely in recipes but is not a palette token.
  - `form-field-group` carries #333333 text at 13px, likely from an embedded third-party form. It sits outside the type ladder.
  - Helvetica appeared once on one page.
- **Interaction coverage.** Hover and focus states were captured only where listed on recipes (buttons, inputs, footer links, header CTAs). Active and pressed states, menu-open states, dropdown panels and the mobile navigation drawer were not captured.
- **Motion.** Animation, transitions, carousel behavior of the logo wall and video playback were not observable.
- **Responsive.** Only desktop and mobile viewports were captured, so breakpoint values and tablet layouts are unknown.
- **`rounded.xs` (3px).** Measured on pages but on no recipe, so its exact usage is unconfirmed.
- **Soft shadow.** The overlay shadow was measured on one page only, presumably the cookie modal.
