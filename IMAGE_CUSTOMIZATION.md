# Image Customization

## Overview

CROUStillant API now supports custom color parameters for menu image generation, allowing users to personalize the appearance of generated menu images.

## Features

- **Theme-based generation**: Use predefined themes (light, purple, dark)
- **Custom color override**: Override specific colors within a theme
- **Flexible color format**: Supports both #RRGGBB and #RGB hexadecimal formats

## Usage

### Endpoint

```
GET /v1/restaurants/{code}/menu/{date}/image
```

### Parameters

#### Required Parameters
- `code` (path): Restaurant ID
- `date` (path): Menu date in DD-MM-YYYY format

#### Optional Parameters
- `repas` (query): Meal type - "matin", "midi", or "soir" (default: "midi")
- `theme` (query): Base theme - "light", "purple", or "dark" (default: "light")

#### Color Customization Parameters (Optional)
- `color_header` (query): Header text color (e.g., #000000)
- `color_content` (query): Content text color (e.g., #373737)
- `color_title` (query): Title text color (e.g., #333333)
- `color_infos` (query): Information text color (e.g., #4F4F4F)

### Examples

#### Example 1: Using Default Theme
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=light
```

#### Example 2: Custom Header Color
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=light&color_header=%23FF0000
```

#### Example 3: Multiple Custom Colors
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=dark&color_header=%23FF5733&color_content=%23C70039&color_title=%23900C3F&color_infos=%23581845
```

#### Example 4: Partial Customization
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=purple&color_header=%2300FF00&color_content=%230000FF
```

## Color Format

Colors must be provided in hexadecimal format:
- 6-digit format: `#RRGGBB` (e.g., #FF5733)
- 3-digit format: `#RGB` (e.g., #F57)

**Note**: When used in URLs, the `#` character must be URL-encoded as `%23`.

## Default Theme Colors

### Light Theme
- Header: `#000000` (black)
- Content: `#373737` (dark gray)
- Title: `#333333` (darker gray)
- Infos: `#4F4F4F` (medium gray)

### Purple Theme
- Header: `#FFFFFF` (white)
- Content: `#F4EEE0` (cream)
- Title: `#F4EEE0` (cream)
- Infos: `#F4EEE0` (cream)

### Dark Theme
- Header: `#FFFFFF` (white)
- Content: `#F4EEE0` (cream)
- Title: `#F4EEE0` (cream)
- Infos: `#F4EEE0` (cream)

## Validation

- Invalid color formats are silently ignored
- Only valid hexadecimal colors are applied
- Custom colors override the theme's default colors
- If no custom colors are provided or all are invalid, the theme defaults are used

## Notes

- Custom colors work with any base theme
- You can customize individual colors without affecting others
- The background image and layout remain theme-specific
- Custom colors are applied on top of the selected theme
