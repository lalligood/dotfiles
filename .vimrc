" ==================================================================
" .vimrc
" ==================================================================

" ==================================================================
" PERSONAL SETTINGS
" ==================================================================

" Enable syntax highlighting
syntax on
" Set color scheme
colorscheme vividchalk
" Turn on smart indent feature
set smartindent
" Set indent to 4 spaces
set shiftwidth=4
" Alter backspace behavior to treat indent spaces like tabs
set softtabstop=4
" Change tabs into spaces
set expandtab
" Turn on line numbers
set number
" Turn on visual word wrap at the end of a word...
set wrap linebreak
" ...but disable wrapping onto a new line
set formatoptions-=t
" Highlight column 88, useful when using large windows
set colorcolumn=88
" Highlight the current line
set cursorline
" Highlight search pattern while typing & results after pressing <Enter>.
set hlsearch
set incsearch
" Enable spelling dictionary locale
set spelllang=en_us
" Enable ruler in bottom-right corner
set ruler
" Disable backup files
set nobackup
" Disable swapfile
set noswapfile
" Enable persistent undo
silent !mkdir ~/.vim/undo > /dev/null 2>&1
set undodir=~/.vim/undo//
set undofile
" Set Blowfish2 for encryption algorithm
if v:version > 800
    set cryptmethod=blowfish2
endif
" Enable folding & load/save folds
set foldenable
set foldmethod=manual
augroup remember_folds
    autocmd BufWinLeave *.* mkview
    autocmd BufWinEnter *.* silent loadview
augroup END
" Make tabs, trailing whitespace, & non-breaking spaces visible
" Inspired by https://www.reddit.com/r/vim/comments/4hoa6e/what_do_you_use_for_your_listchars/
set listchars=tab:»›,trail:·,nbsp:¤,eol:↲
set list
" Disable screen redraw to speed up macros
set lazyredraw
" Disable modeline support
set nomodeline

" ==================================================================
" FILE SYNTAX HIGHLIGHTING
" ==================================================================

" Arduino sketch files - requires arduino.vim
autocmd BufNewFile,BufRead *.pde setf arduino
autocmd BufNewFile,BufRead *.ino setf arduino
" Linux configuration files
autocmd BufNewFile,BufRead *.conf setf dosini
" SQL files - requires sql.vim
autocmd BufNewFile,BufRead *.sql setf sql
" Python script files
autocmd BufNewFile,BufRead *.py
    \ set tabstop=4 |
    \ set softtabstop=4 |
    \ set shiftwidth=4 |
    \ set textwidth=79 |
    \ set expandtab |
    \ set autoindent |
    \ set fileformat=unix |
    \ set encoding=utf-8

" ==================================================================
" PERSONAL KEYMAPPINGS
" ==================================================================

" Close window
nnoremap <bs> :q<CR>
" Turn diff off
nnoremap <leader>D :diffoff!<CR>
" Turn off search result highlights
nnoremap <silent> <leader><space> :noh<CR>:call clearmatches()<CR>
" Move search results into the middle of the screen
nnoremap n nzzzv
nnoremap N Nzzzv
" Remove any trailing whitespace
nnoremap <leader>ww mz:%s/\s\+$//<CR>:let @/=''<CR>
" Turn relativenumber on or off
nnoremap <silent> <F1> <Esc>:set relativenumber!<CR><Bar>:echo "Relative numbering: " . strpart("OffOn", 3 * &relativenumber, 3)<CR>
" Enable/disable ability to paste with/without leading spaces
nnoremap <F3> <Esc>:set invpaste paste?<CR>
set pastetoggle=<F3>
set showmode
" Turn spell check On or Off
nnoremap <F4> <Esc>:set spell!<CR><Bar>:echo "Spell Check: " . strpart("OffOn", 3 * &spell, 3)<CR>
" Go to previous misspelled word
nnoremap <F5> <Esc>[s
" Go to next misspelled word
nnoremap <F6> <Esc>]s
" Display correct spelling suggestions
nnoremap <F7> <Esc>z=
" Jump to next file in buffer
nnoremap <leader>j :bn<CR>
" Jump to previous file in buffer
nnoremap <leader>k :bp<CR>
" This changes default behavior of arrow keys for easier navigation with
" long lines (paragraphs)
nnoremap <Down> gj
nnoremap <Up> gk
vnoremap <Down> gj
vnoremap <Up> gk
inoremap <Down> <C-o>gj
inoremap <Up> <C-o>gk
" Faster splits
nnoremap <leader>v <C-w>v
nnoremap <leader>s <C-w>s
" Faster navigation between splits
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Pathogen plugin manager
execute pathogen#infect()
