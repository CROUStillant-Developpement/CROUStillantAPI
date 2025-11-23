# Quick Start Guide: Image Customization

## Overview
This guide provides quick examples to get started with the new image customization feature.

## Basic Usage

### 1. Default Theme (No Customization)
Use one of the predefined themes without any color customization:
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=light
GET /v1/restaurants/1/menu/21-10-2024/image?theme=purple
GET /v1/restaurants/1/menu/21-10-2024/image?theme=dark
```

### 2. Single Color Override
Override just the header color while keeping other colors from the theme:
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=light&color_header=%23FF0000
```
Result: Red header (#FF0000) with light theme defaults for other text

### 3. Multiple Color Overrides
Customize multiple colors at once:
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=dark&color_header=%23FFD700&color_content=%23FFA500
```
Result: Gold header (#FFD700) and orange content (#FFA500) with dark theme background

### 4. Full Custom Color Scheme
Override all color components:
```
GET /v1/restaurants/1/menu/21-10-2024/image?theme=light&color_header=%23FF5733&color_content=%23C70039&color_title=%23900C3F&color_infos=%23581845
```

## Color Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `color_header` | Restaurant name and date | `%23000000` (black) |
| `color_content` | Menu items and categories | `%23373737` (dark gray) |
| `color_title` | Section titles | `%23333333` (darker gray) |
| `color_infos` | Restaurant information | `%234F4F4F` (medium gray) |

## Color Format

- **Full format**: `#RRGGBB` (e.g., `#FF5733`)
- **Short format**: `#RGB` (e.g., `#F57`)
- **URL encoded**: Replace `#` with `%23` in URLs

## Common Color Examples

### Professional Schemes
```
# Blue Corporate
color_header=%232C3E50&color_content=%2334495E&color_title=%232980B9&color_infos=%233498DB

# Green Fresh
color_header=%2327AE60&color_content=%232ECC71&color_title=%231E8449&color_infos=%2316A085

# Purple Modern
color_header=%238E44AD&color_content=%239B59B6&color_title=%23663399&color_infos=%237D3C98
```

### High Contrast Schemes
```
# High Visibility
color_header=%23FFFFFF&color_content=%23FFFF00&color_title=%2300FF00&color_infos=%2300FFFF

# Black & White
color_header=%23000000&color_content=%23333333&color_title=%23666666&color_infos=%23999999
```

## Tips

1. **Start with a theme**: Choose a base theme that has the background style you want
2. **Override selectively**: You don't need to customize all colors
3. **Test readability**: Ensure text colors contrast well with the background
4. **Use URL encoding**: Remember to encode `#` as `%23` in URLs
5. **Invalid colors are ignored**: If a color format is invalid, the theme default is used

## Error Handling

The API gracefully handles invalid colors:
- Invalid format → Uses theme default
- Missing parameter → Uses theme default
- Partial customization → Applies valid colors, uses defaults for others

## Full Example Request

```bash
curl "https://api.croustillant.menu/v1/restaurants/1/menu/21-10-2024/image?repas=midi&theme=light&color_header=%23FF0000&color_content=%2300FF00" \
  -o menu.png
```

This will generate a menu image with:
- Meal: Lunch (midi)
- Theme: Light background
- Header: Red (#FF0000)
- Content: Green (#00FF00)
- Title & Infos: Light theme defaults
