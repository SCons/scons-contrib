# scons-mode for emacs

`scons-mode` for syntax highlighting, based on `python-mode`.

## Installation

### Copy the file

Add `scons-mode.el` to a directory in your [load
path](https://www.emacswiki.org/emacs/LoadPath), often
`~/.emacs.d/lisp/`.

### Initialize with `require`.

[Open your init
file](https://www.gnu.org/software/emacs/manual/html_node/emacs/Find-Init.html)
and add to it the following lines:

```elisp
(require 'scons-mode)
(add-to-list 'auto-mode-alist '("SConstruct". scons-mode))
```

### Initialize with `use-package`

If you prefer
[`use-package`](https://github.com/jwiegley/use-package), add these
lines to your init file instead.

```elisp
(use-package scons-mode
  :config
  (add-to-list 'auto-mode-alist '("SConstruct". scons-mode)))
```

## Support in other packages

### color-identifiers-mode

If you use the
[`color-identifiers-mode`](https://github.com/ankurdave/color-identifiers-mode)
minor mode, add this to your init file so that
`color-identifiers-mode` will work with `scons-mode` (taken from the
python example):

```elisp
(add-to-list
             'color-identifiers:modes-alist
             `(scons-mode . (,color-identifiers:re-not-inside-class-access
                             "\\_<\\([a-zA-Z_$]\\(?:\\s_\\|\\sw\\)*\\)"
                             (nil font-lock-variable-name-face tree-sitter-hl-face:variable))))))
```

Add either as-is or to the `:config` section of `use-package
color-identifiers-mode`.
