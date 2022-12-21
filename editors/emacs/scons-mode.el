;;; scons-mode.el --- GNU Emacs major mode (only font-locking) for scons output

;; Copyright (C) 2007 by Per Nordlöw

;; Author: Per Nordlöw <per.nordlow@gmail.com>
;; Version 0.1

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 2, or (at your option)
;; any later version.

;;; Code:

(defgroup scons-mode nil
  "Scons mode."
  :group 'wp
  :prefix "scons-")

(defvar scons-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map "\es" 'center-line)
    map)
  "Major mode keymap for `scons-mode'.")

;; Main
(defface scons-mode-main-face
  '((t (:inherit font-lock-function-name-face :bold t)))
  "*Face used to highlight main line in scons."
  :group 'scons-mode-mode)
(defvar scons-mode-main-face 'scons-mode-main-face)

(defconst scons-mode-font-lock-keywords
  (progn
    (require 'font-lock)
    (list
     ;; Function Names
     ;; (list (concat
     ;;        "^ "                     ;line begins with a space
     ;;        ".*" " "
     ;;        "\\(" "[[:alnum:]_]+" "\\)" "$")
     ;;       1 'font-lock-function-name-face)
     ;; (list (concat
     ;;        "^ "                     ;line begins with a space
     ;;        ".*" " "
     ;;        "\\(" "[[:alnum:]_]+" "\\)" " "
     ;;        "\\[" "self" "\\]" "$")
     ;;       1 'font-lock-function-name-face)
     (list (concat
            (rx symbol-start (group (| "Environment"
                                       "Export"

                                       "Clone"
                                       "Append"

                                       "Import"
                                       "Default"
                                       "Alias"
                                       "Object"
                                       "File"
                                       "Dir"
                                       "StaticLibrary"
                                       "SharedLibrary"
                                       "Builder"
                                       "Action"
                                       "SConscript"
                                       "Program"
                                       "Return"
                                       "NodeList"
                                       "ListAction"
                                       "Entry"
                                       "RootDir")) symbol-end)
            )
           1 'font-lock-builtin-face)
     ;; (list (concat
     ;;        "^[[:digit:]]"                   ;line begins with a number
     ;;        ".*" " "
     ;;        "\\(" "[[:alnum:]_]+" "\\)" "$")
     ;;       1 'scons-mode-main-face)
     ))
  "Expressions to font-lock in Operators mode.")

(defcustom scons-mode-hook nil
  "Hook run by function `scons-mode'."
  :type 'hook
  :group 'scons-mode)

;;;###autoload
(define-derived-mode scons-mode python-mode "SConstruct (scons)"
  "Major mode for font locking of SConstruct.
\\{scons-mode-map}
Turning on Operators mode runs `python-mode-hook', then `scons-mode-hook'."
  (use-local-map scons-mode-map)
  (font-lock-add-keywords 'scons-mode
                          scons-mode-font-lock-keywords))

(provide 'scons-mode)

;;; scons-mode.el ends here
