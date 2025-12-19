" =============================================================================
" .vimrc - Minimal Vim configuration (fallback when nvim unavailable)
" =============================================================================

" -----------------------------------------------------------------------------
" Basic settings
" -----------------------------------------------------------------------------
set nocompatible              " Use Vim defaults
syntax on                     " Syntax highlighting
set number                    " Line numbers
set ruler                     " Cursor position
set cursorline                " Highlight current line
set hlsearch                  " Highlight search results
set incsearch                 " Incremental search
set laststatus=2              " Always show status line

" -----------------------------------------------------------------------------
" Indentation (4 spaces)
" -----------------------------------------------------------------------------
set tabstop=4
set shiftwidth=4
set expandtab                 " Tabs to spaces
set autoindent                " Auto indent
set smartindent               " Smart indent

" -----------------------------------------------------------------------------
" Key mappings
" -----------------------------------------------------------------------------
" jk/kj to escape (muscle memory saver)
inoremap jk <Esc>
inoremap kj <Esc>

" Y yanks to end of line (consistent with D and C)
nnoremap Y y$

" Enter creates new line in normal mode
nnoremap <Enter> o<Esc>

" Comment/uncomment with # (useful for bash/python scripts)
nnoremap ; I# <Esc>0
nnoremap ' ^xx

" -----------------------------------------------------------------------------
" Colorscheme
" -----------------------------------------------------------------------------
colorscheme desert
