# Kaomoji Guide for PingFang TC Font

This guide documents which kaomoji render correctly in Typst with PingFang TC font (macOS default Chinese font).

## Tested & Safe Kaomoji

These kaomoji have been tested and render correctly:

### Happy/Positive
- `╰(°▽°)╯` - Very happy, celebratory
- `(°▽°)` - Simple happy face
- `(￣▽￣)／` - Casual, relaxed greeting

### Neutral/Shrug
- `┐(￣ヘ￣)┌` - Shrug, mild frustration
- `¯\_(ツ)_/¯` - Classic shrug (ASCII version)

### Surprised
- `ヽ(°〇°)ﾉ` - Surprised with raised arms

### Working Hard
- `(ง •̀_•́)ง` - Fighting spirit (may need testing)

## Problematic Characters (Avoid)

These characters don't render properly in PingFang TC:

### Markdown Checkboxes
- `- [ ]` and `- [x]` - Render as weird squares in Typst PDF
- **Solution**: Use plain bullet points `- Item` instead
- Or use emoji checkmarks if needed: `✓` (but test first)

### Kaomoji - Combining Characters Issue
- `(◕‿◕)` - The `‿` (undertie) renders as square
- `(◕_◕)` - May work as alternative

### Thai/Special Scripts
- `(๑•̀ㅂ•́)و✧` - Thai `๑` and Arabic `و` don't render
- Anything with `๑`, `و`, `✧` characters

### Emoji-Style
- Most emoji don't render well in PDF
- Stick to ASCII-based kaomoji

## Testing New Kaomoji

To test a kaomoji:

1. Add it to a .typ file
2. Compile with `typst compile file.typ`
3. Open PDF and check for squares (□) or missing characters
4. If squares appear, the kaomoji is not safe to use

## Typst Syntax Note

In Typst, use `#h(0.3em)` to add spacing before kaomoji:

```typst
- 應該可以做好 #h(0.3em) (°▽°)
```

This prevents the kaomoji from touching the preceding text.
