# Rooyin Font Files

The UI references two Persian font files in this directory:

- `Rooyin-Regular.woff2` (weight 400)
- `Rooyin-Bold.woff2` (weight 700)

## If you have the fonts

Drop the `.woff2` files into this folder and they'll be picked up
automatically on the next app launch.

## If you don't have them

The UI **gracefully falls back** to the following stack (declared in
`ui/style.css`):

```
"Rooyin", "Vazirmatn", "Segoe UI", Tahoma, sans-serif
```

So the app runs perfectly without these files — Persian text simply uses
the system default (Vazirmatn on most Linux distros, Segoe UI / Tahoma on
Windows).

## Where to get Rooyin

Rooyin is a free Persian font from the RastiKerdar / Shahab-Karami family.
You can also substitute any Persian webfont you prefer — just rename the
files to match the names above, or edit the `@font-face` rules in
`ui/style.css`.
