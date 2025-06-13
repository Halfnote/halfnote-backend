import 'styled-components';

declare module 'styled-components' {
  export interface DefaultTheme {
    colors: {
      primary: string;
      secondary: string;
      background: string;
      white: string;
      gray: {
        100: string;
        200: string;
        300: string;
        400: string;
        500: string;
        600: string;
        700: string;
        800: string;
        900: string;
      };
      success: string;
      error: string;
      warning: string;
    };
    fonts: {
      primary: string;
    };
    breakpoints: {
      mobile: string;
      tablet: string;
      desktop: string;
    };
  }
} 