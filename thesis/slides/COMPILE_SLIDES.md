# Compile Slide Presentation

Slides dùng XeLaTeX (không cần biber — không có bibliography).

## Lệnh compile

```bash
cd D:/CloudProject/thesis/slides
xelatex presentation.tex
```

Chạy **một lần** là đủ (không cần biber, không cần chạy nhiều lần).

## Lỗi font Arial không tìm thấy

Thay `\setsansfont{Arial}` bằng:
```latex
\setsansfont{TeX Gyre Heros}   % clone của Arial, có trong TeX Live
```
