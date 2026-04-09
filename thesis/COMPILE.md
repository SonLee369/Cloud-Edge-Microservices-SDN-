# Hướng dẫn Compile Luận văn LaTeX

## Yêu cầu phần mềm

| Phần mềm | Phiên bản tối thiểu | Ghi chú |
|---|---|---|
| TeX Live | 2022 trở lên | Bao gồm XeLaTeX + Biber |
| Font Times New Roman | — | Có sẵn trên Windows |

> **Lưu ý:** Luận văn dùng **XeLaTeX** (không phải pdfLaTeX) vì cần hỗ trợ tiếng Việt Unicode và font Times New Roman hệ thống.

---

## Cài đặt TeX Live (nếu chưa có)

### Windows
1. Tải installer tại: https://tug.org/texlive/acquire-netinstall.html
2. Chạy `install-tl-windows.bat`
3. Chọn **Full scheme** để có đủ packages
4. Quá trình cài khoảng 30–60 phút

### Kiểm tra sau cài đặt
```bash
xelatex --version
biber --version
```

---

## Compile (cách thủ công)

Mở terminal tại thư mục `thesis/` và chạy **theo đúng thứ tự**:

```bash
# Bước 1: Compile lần 1 (tạo .aux, .bcf)
xelatex main.tex

# Bước 2: Xử lý bibliography
biber main

# Bước 3: Compile lần 2 (điền references vào document)
xelatex main.tex

# Bước 4: Compile lần 3 (fix TOC, cross-references)
xelatex main.tex
```

Output: `main.pdf`

> Phải compile **đúng 4 bước** theo thứ tự. Bỏ qua `biber` sẽ khiến citations hiển thị dạng `[?]`.

---

## Compile một lệnh (khuyến nghị)

Dùng `latexmk` để tự động hóa toàn bộ quá trình:

```bash
latexmk -xelatex -bibtex main.tex
```

Xóa file tạm và compile lại từ đầu:

```bash
latexmk -xelatex -bibtex -CA main.tex
```

---

## Dùng VS Code (khuyến nghị cho soạn thảo)

### Cài đặt extension
- Cài extension **LaTeX Workshop** (James Yu)

### Cấu hình `.vscode/settings.json`
Tạo file `.vscode/settings.json` trong thư mục `thesis/` với nội dung:

```json
{
  "latex-workshop.latex.tools": [
    {
      "name": "xelatex",
      "command": "xelatex",
      "args": ["-synctex=1", "-interaction=nonstopmode", "%DOC%"]
    },
    {
      "name": "biber",
      "command": "biber",
      "args": ["%DOCFILE%"]
    }
  ],
  "latex-workshop.latex.recipes": [
    {
      "name": "xelatex -> biber -> xelatex x2",
      "tools": ["xelatex", "biber", "xelatex", "xelatex"]
    }
  ],
  "latex-workshop.latex.recipe.default": "xelatex -> biber -> xelatex x2",
  "latex-workshop.view.pdf.viewer": "tab"
}
```

Sau đó nhấn `Ctrl+Alt+B` để build, `Ctrl+Alt+V` để xem PDF.

---

## Xử lý lỗi thường gặp

### Lỗi font Times New Roman không tìm thấy

```
! fontspec error: "font-not-found"
```

**Giải pháp:** Thay `Times New Roman` bằng `TeX Gyre Termes` trong `main.tex`:

```latex
% Dòng cũ
\setmainfont{Times New Roman}

% Thay bằng
\setmainfont{TeX Gyre Termes}
```

`TeX Gyre Termes` là bản clone của Times New Roman, có sẵn trong TeX Live.

---

### Lỗi Biber không tìm thấy

```
ERROR - Cannot find 'biber' in PATH
```

**Giải pháp:**
```bash
# Kiểm tra biber có trong PATH chưa
where biber        # Windows
which biber        # Linux/macOS

# Nếu chưa có, cài qua TeX Live Manager
tlmgr install biber
```

---

### Citations hiển thị `[?]` hoặc `??`

Chưa chạy `biber`. Thực hiện lại đủ 4 bước compile.

---

### Lỗi tiếng Việt bị vỡ / mất dấu

Đảm bảo file `.tex` được lưu dưới encoding **UTF-8** (không phải ANSI). Trong VS Code: nhìn góc dưới bên phải, click vào encoding và chọn `UTF-8`.

---

### Lỗi `Package polyglossia Error`

```
! Package polyglossia Error: The language 'vietnamese' is not defined.
```

**Giải pháp:**
```bash
tlmgr install polyglossia
```

---

## Dọn dẹp file tạm

```bash
# Xóa thủ công
rm -f main.aux main.bbl main.bcf main.blg main.lof \
      main.log main.lot main.out main.run.xml main.toc

# Hoặc dùng latexmk
latexmk -CA
```

---

## Cấu trúc thư mục

```
thesis/
├── main.tex              ← File chính, compile file này
├── references.bib        ← Danh sách tài liệu tham khảo
├── COMPILE.md            ← File hướng dẫn này
└── chapters/
    ├── cover.tex         ← Trang bìa
    ├── commitment.tex    ← Lời cam đoan
    ├── abbreviations.tex ← Danh mục từ viết tắt
    ├── intro.tex         ← Mở đầu
    ├── chapter1.tex      ← Chương 1
    ├── chapter2.tex      ← Chương 2
    ├── chapter3.tex      ← Chương 3
    ├── chapter4.tex      ← Chương 4
    └── conclusion.tex    ← Kết luận
```

> Chỉ cần compile `main.tex` — tất cả chapter files được `\input{}` tự động.
